import argparse
import os
import pathlib
import subprocess
import sys
import tempfile

STEPS = [
    {
        "file": "DESIGN.md",
        "label": "brand design document",
        "msg": "Generate .brand/DESIGN.md",
        "output": ".brand/DESIGN.md",
    },
    {
        "file": "1.md",
        "label": "asset extraction",
        "msg": "Extract static media assets to .brand/assets/",
        "output": ".brand/assets/",
    },
    {
        "file": "2.md",
        "label": "UI element extraction",
        "msg": "Extract React components to .brand/elements/html/",
        "output": ".brand/elements/html/",
    },
    {
        "file": "3.md",
        "label": "SVG rendering",
        "msg": "Render components as SVG to .brand/elements/svg/",
        "output": ".brand/elements/svg/",
    },
    {
        "file": "4.md",
        "label": "screenshots",
        "msg": "Capture screenshots to .brand/screenshots/",
        "output": ".brand/screenshots/",
    },
    {
        "file": "5.md",
        "label": "map generation",
        "msg": "Generate .brand/map.json",
        "output": ".brand/map.json",
    },
]


def main():
    parser = argparse.ArgumentParser(prog="ive")
    subparsers = parser.add_subparsers(dest="command", required=True)

    steps_desc = "\n".join(f"  {i}  {s['label']}" for i, s in enumerate(STEPS))
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize brand design for the project",
        description="Run the brand extraction pipeline against the project.\n\n"
        "Steps:\n" + steps_desc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    init_parser.add_argument("--dir", default=".", help="Project directory (default: current dir)")
    init_parser.add_argument("--agent", default=None, help="Opencode agent to use (default: active agent)")
    init_parser.add_argument("--model", default=None, help="Model to use (e.g. anthropic/claude-sonnet-4)")
    init_parser.add_argument("--steps", default=None, help="Steps to run, e.g. 0-3 or 0,2,5 (default: all)")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(
            pathlib.Path(args.dir).resolve(),
            agent=args.agent,
            model=args.model,
            steps=args.steps,
        )


def parse_steps(spec: str | None) -> list[int]:
    if spec is None:
        return list(range(len(STEPS)))
    result = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            for i in range(int(a.strip()), int(b.strip()) + 1):
                result.add(i)
        else:
            result.add(int(part))
    return sorted(result)


def cmd_init(project_dir: pathlib.Path, agent: str | None = None, model: str | None = None, steps: str | None = None):
    project_dir.joinpath(".brand").mkdir(exist_ok=True)

    prompt_dir = pathlib.Path(__file__).resolve().parent / "prompts"
    if not prompt_dir.exists():
        print("ive: prompts/ directory not found", file=sys.stderr)
        sys.exit(1)

    step_indices = parse_steps(steps)
    context_cache: str | None = None

    for idx in step_indices:
        if idx < 0 or idx >= len(STEPS):
            print(f"ive: invalid step {idx}", file=sys.stderr)
            sys.exit(1)

        step = STEPS[idx]
        prompt_path = prompt_dir / step["file"]
        if not prompt_path.exists():
            print(f"ive: {step['file']} not found", file=sys.stderr)
            sys.exit(1)

        prompt_text = prompt_path.read_text(encoding="utf-8")

        if idx == 0:
            if context_cache is None:
                context_cache = gather_context(project_dir)
            prompt_text = (
                f"{prompt_text}\n\n"
                f"---\n\n"
                f"## Project Context\n\n"
                f"{context_cache}"
            )

        print(f"ive: [{idx}] {step['label']}...")
        run_opencode(project_dir, prompt_text, step["msg"], agent=agent, model=model)

        output = project_dir / step["output"]
        if output.exists():
            print(f"ive: [{idx}] done \u2014 {output}")
        else:
            print(f"ive: [{idx}] opencode completed but {step['output']} was not created", file=sys.stderr)


def run_opencode(project_dir: pathlib.Path, prompt: str, message: str, agent: str | None = None, model: str | None = None):
    prompt_file = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(prompt)
            prompt_file = f.name

        parts = ["opencode", "run"]
        parts.extend(["-f", prompt_file])
        parts.extend(["--dir", str(project_dir)])
        parts.append("--dangerously-skip-permissions")
        parts.append("--pure")
        if agent:
            parts.extend(["--agent", agent])
        if model:
            parts.extend(["-m", model])
        parts.append(message)

        cmd = " ".join(f'"{p}"' if " " in p else p for p in parts)
        result = subprocess.run(cmd, shell=True)

        if result.returncode != 0:
            print("ive: opencode run failed", file=sys.stderr)
            sys.exit(1)
    finally:
        if prompt_file is not None:
            os.unlink(prompt_file)


def gather_context(project_dir: pathlib.Path) -> str:
    parts = []

    for pattern in ("README.md", "package.json", "pyproject.toml", "Cargo.toml", "composer.json"):
        f = project_dir / pattern
        if f.exists() and f.stat().st_size < 50000:
            parts.append(f"### `{pattern}`\n```\n{f.read_text(encoding='utf-8', errors='replace')[:3000]}\n```\n")

    parts.append("### Project Files\n")
    tree = get_file_tree(project_dir, max_depth=3)
    parts.append(f"```\n{tree}\n```")

    return "\n".join(parts)


def get_file_tree(project_dir: pathlib.Path, max_depth: int = 3) -> str:
    ignore = {".git", "node_modules", "__pycache__", ".venv", ".brand", "target", ".next", "dist", "build"}
    lines = []
    project_dir = project_dir.resolve()

    def walk(current: pathlib.Path, depth: int):
        if depth > max_depth:
            return
        try:
            entries = sorted(current.iterdir(), key=lambda x: (x.is_file(), x.name))
        except PermissionError:
            return
        for entry in entries:
            if entry.name in ignore or entry.name.startswith("."):
                continue
            indent = "  " * depth
            if entry.is_dir():
                lines.append(f"{indent}{entry.name}/")
                walk(entry, depth + 1)
            else:
                lines.append(f"{indent}{entry.name}")

    walk(project_dir, 0)
    return "\n".join(lines)


if __name__ == "__main__":
    main()
