import argparse
import os
import pathlib
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(prog="ive")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize brand design for the project")
    init_parser.add_argument("--dir", default=".", help="Project directory (default: current dir)")
    init_parser.add_argument("--agent", default=None, help="Opencode agent to use (default: active agent)")
    init_parser.add_argument("--model", default=None, help="Model to use (e.g. anthropic/claude-sonnet-4)")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(
            pathlib.Path(args.dir).resolve(),
            agent=args.agent,
            model=args.model,
        )


def cmd_init(project_dir: pathlib.Path, agent: str | None = None, model: str | None = None):
    prompt = read_prompt()
    context = gather_context(project_dir)

    final_prompt = (
        f"{prompt}\n\n"
        f"---\n\n"
        f"## Project Context\n\n"
        f"{context}\n\n"
        f"---\n\n"
        f"Generate the `.brand/DESIGN.md` file in the current project directory."
    )

    print(f"ive: creating .brand/DESIGN.md in {project_dir}")
    project_dir.joinpath(".brand").mkdir(exist_ok=True)

    prompt_file = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(final_prompt)
            prompt_file = f.name

        parts = ["opencode", "run"]
        parts.extend(["-f", prompt_file])
        parts.extend(["--dir", str(project_dir)])
        parts.append("--dangerously-skip-permissions")
        if agent:
            parts.extend(["--agent", agent])
        if model:
            parts.extend(["-m", model])
        parts.append("Generate .brand/DESIGN.md using the instructions in the attached file")

        cmd = " ".join(f'"{p}"' if " " in p else p for p in parts)
        result = subprocess.run(cmd, shell=True)

        if result.returncode != 0:
            print("ive: opencode run failed", file=sys.stderr)
            sys.exit(1)

        design_path = project_dir / ".brand" / "DESIGN.md"
        if design_path.exists():
            print(f"ive: done — {design_path}")
        else:
            print(
                "ive: opencode completed but DESIGN.md was not created",
                file=sys.stderr,
            )
    finally:
        if prompt_file is not None:
            os.unlink(prompt_file)


def read_prompt() -> str:
    src = pathlib.Path(__file__).resolve().parent
    candidates = [
        src / "prompts" / "DESIGN.md",
        src.parent.parent / "prompts" / "DESIGN.md",
    ]
    for p in candidates:
        if p.exists():
            return p.read_text(encoding="utf-8")
    print("ive: prompts/DESIGN.md not found", file=sys.stderr)
    sys.exit(1)


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
