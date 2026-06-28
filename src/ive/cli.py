import argparse
import importlib.metadata
import os
import pathlib
import shutil
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
    init_parser.add_argument("--steps", default=None, help='Steps to run, e.g. "0-3", "0,2,5", "!3" (exclude), "!2,!4" (default: all)')

    create_parser = subparsers.add_parser("create", help="Create a new project")
    create_subparsers = create_parser.add_subparsers(dest="create_command")
    create_video_parser = create_subparsers.add_parser("video", help="Create a new Remotion video project")
    create_video_parser.add_argument("name", help="Video project name")
    create_video_parser.add_argument("--dir", default=".", help="Project directory (default: current dir)")

    script_parser = create_subparsers.add_parser("script", help="Create a script file")
    script_parser.add_argument("--to", required=True, help="Video name (e.g. my-video)")
    script_parser.add_argument("--dir", default=".", help="Project directory (default: current dir)")
    script_parser.add_argument("--agent", default=None, help="Opencode agent to use (default: active agent)")
    script_parser.add_argument("--model", default=None, help="Model to use (e.g. anthropic/claude-sonnet-4)")

    delete_parser = subparsers.add_parser("delete", help="Delete a resource")
    delete_subparsers = delete_parser.add_subparsers(dest="delete_command", required=False)
    delete_script_parser = delete_subparsers.add_parser("script", help="Delete a script file")
    delete_script_parser.add_argument("--to", required=True, help="Video name (e.g. my-video)")
    delete_script_parser.add_argument("--dir", default=".", help="Project directory (default: current dir)")
    delete_video_parser = delete_subparsers.add_parser("video", help="Delete an entire video project")
    delete_video_parser.add_argument("path", help="Video name (e.g. my-video)")
    delete_video_parser.add_argument("--dir", default=".", help="Project directory (default: current dir)")

    list_parser = subparsers.add_parser("list", help="List resources")
    list_subparsers = list_parser.add_subparsers(dest="list_command")
    list_video_parser = list_subparsers.add_parser("video", help="List video projects")
    list_video_parser.add_argument("--dir", default=".", help="Project directory (default: current dir)")

    check_parser = subparsers.add_parser("check", help="Check if init has been run")
    check_parser.add_argument("--dir", default=".", help="Project directory (default: current dir)")

    show_parser = subparsers.add_parser("show", help="Show a resource")
    show_subparsers = show_parser.add_subparsers(dest="show_command")
    show_script_parser = show_subparsers.add_parser("script", help="Show a video script")
    show_script_parser.add_argument("--of", required=True, help="Video name (e.g. my-video)")
    show_script_parser.add_argument("--dir", default=".", help="Project directory (default: current dir)")

    generate_parser = subparsers.add_parser("generate", help="Generate a video via opencode TUI")
    generate_subparsers = generate_parser.add_subparsers(dest="generate_command")
    generate_video_parser = generate_subparsers.add_parser("video", help="Generate a video from its script")
    generate_video_parser.add_argument("name", help="Video name (e.g. my-video)")
    generate_video_parser.add_argument("--dir", default=".", help="Project directory (default: current dir)")
    generate_video_parser.add_argument("--agent", default=None, help="Opencode agent to use (default: active agent)")
    generate_video_parser.add_argument("--model", default=None, help="Model to use (e.g. anthropic/claude-sonnet-4)")

    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(
            pathlib.Path(args.dir).resolve(),
            agent=args.agent,
            model=args.model,
            steps=args.steps,
        )
    elif args.command == "create":
        if args.create_command == "video":
            cmd_create_remotion_video(args.name, pathlib.Path(args.dir).resolve())
        elif args.create_command == "script":
            cmd_create_script(args.to, pathlib.Path(args.dir).resolve(), agent=args.agent, model=args.model)
    elif args.command == "delete":
        if args.delete_command is None:
            cmd_delete_brand(pathlib.Path(".").resolve())
        elif args.delete_command == "script":
            cmd_delete_script(args.to, pathlib.Path(args.dir).resolve())
        elif args.delete_command == "video":
            cmd_delete_video(args.path, pathlib.Path(args.dir).resolve())
    elif args.command == "list":
        if args.list_command == "video":
            cmd_list_video(pathlib.Path(args.dir).resolve())
    elif args.command == "show":
        if args.show_command == "script":
            cmd_show_script(args.of, pathlib.Path(args.dir).resolve())
    elif args.command == "generate":
        if args.generate_command == "video":
            cmd_generate_video(args.name, pathlib.Path(args.dir).resolve(), agent=args.agent, model=args.model)
    elif args.command == "check":
        cmd_check(pathlib.Path(args.dir).resolve())
    elif args.command == "version":
        cmd_version()


def parse_steps(spec: str | None) -> list[int]:
    if spec is None:
        return list(range(len(STEPS)))
    include = set()
    exclude = set()
    for part in spec.split(","):
        part = part.strip()
        if part.startswith("!"):
            exclude.add(int(part[1:]))
        elif "-" in part:
            a, b = part.split("-", 1)
            for i in range(int(a.strip()), int(b.strip()) + 1):
                include.add(i)
        else:
            include.add(int(part))
    if not include:
        include = set(range(len(STEPS)))
    return sorted(include - exclude)


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


def cmd_version():
    try:
        ver = importlib.metadata.version("ive")
    except importlib.metadata.PackageNotFoundError:
        src = pathlib.Path(__file__).resolve().parent.parent.parent
        pyproject = src / "pyproject.toml"
        if pyproject.exists():
            for line in pyproject.read_text(encoding="utf-8").splitlines():
                if line.startswith("version = "):
                    ver = line.split("=", 1)[1].strip().strip('"')
                else:
                    ver = "unknown"
        else:
            ver = "unknown"
    print(ver)


def cmd_check(project_dir: pathlib.Path):
    brand_dir = project_dir / ".brand"
    if not brand_dir.exists():
        print("ive: init not run yet — .brand/ does not exist")
        return

    all_ok = True
    for i, step in enumerate(STEPS):
        out = project_dir / step["output"]
        exists = out.exists()
        status = "ok" if exists else "missing"
        if not exists:
            all_ok = False
        print(f"  [{i}] {step['label']}: {status}")

    if all_ok:
        print("ive: init completed successfully")
    else:
        print("ive: init incomplete — some steps are missing")


def cmd_create_remotion_video(name: str, project_dir: pathlib.Path):
    videos_dir = project_dir / ".brand" / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    cwd = os.getcwd()
    try:
        os.chdir(str(videos_dir))
        result = subprocess.run(
            f'npx -y create-video@latest --yes --blank --no-tailwind "{name}"',
            shell=True,
        )
        if result.returncode != 0:
            print("ive: failed to create Remotion video project", file=sys.stderr)
            sys.exit(1)
    finally:
        os.chdir(cwd)

    print(f"ive: done \u2014 {videos_dir / name}")


def cmd_show_script(target: str, project_dir: pathlib.Path):
    script_path = project_dir / ".brand" / "videos" / target / "script.md"
    if not script_path.exists():
        print(f"ive: script.md not found at {script_path}", file=sys.stderr)
        sys.exit(1)
    print(script_path.read_text(encoding="utf-8", errors="replace"))


def cmd_generate_video(name: str, project_dir: pathlib.Path, agent: str | None = None, model: str | None = None):
    script_path = project_dir / ".brand" / "videos" / name / "script.md"
    if not script_path.exists():
        print(f"ive: script.md not found at {script_path}", file=sys.stderr)
        sys.exit(1)

    prompt = (
        f"Generate the Remotion video project at `.brand/videos/{name}` "
        f"based on the script in `.brand/videos/{name}/script.md`. "
        f"Use the project context and brand design from `.brand/` as reference."
    )

    parts = ["opencode", str(project_dir), "--prompt", prompt]
    if agent:
        parts.extend(["--agent", agent])
    if model:
        parts.extend(["-m", model])

    cmd = " ".join(f'"{p}"' if " " in p else p for p in parts)
    subprocess.run(cmd, shell=True)


def cmd_create_script(target: str, project_dir: pathlib.Path, agent: str | None = None, model: str | None = None):
    print("Script prompt (Ctrl+Z then Enter to finish):")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    user_prompt = "\n".join(lines).strip()
    if not user_prompt:
        print("ive: no prompt provided, aborting", file=sys.stderr)
        sys.exit(1)

    prompt_dir = pathlib.Path(__file__).resolve().parent / "prompts"
    template_path = prompt_dir / "script.md"
    template = template_path.read_text(encoding="utf-8") if template_path.exists() else ""

    context = gather_context(project_dir, include_brand=True)

    final_prompt = (
        f"{template}\n\n"
        f"## Project Context\n\n"
        f"{context}\n\n"
        f"## User Request\n\n"
        f"{user_prompt}\n\n"
        f"Save the script to `.brand/videos/{target}/script.md`"
    )

    script_path = project_dir / ".brand" / "videos" / target / "script.md"
    script_path.parent.mkdir(parents=True, exist_ok=True)

    run_opencode(project_dir, final_prompt, f"Generate .brand/videos/{target}/script.md", agent=agent, model=model)

    if script_path.exists():
        print(f"ive: done \u2014 {script_path}")
    else:
        print("ive: opencode completed but script.md was not created", file=sys.stderr)


def cmd_list_video(project_dir: pathlib.Path):
    videos_dir = project_dir / ".brand" / "videos"
    if not videos_dir.exists():
        return
    names = sorted(
        e.name for e in videos_dir.iterdir()
        if e.is_dir() and not e.name.startswith(".")
    )
    if names:
        for n in names:
            script_path = videos_dir / n / "script.md"
            has_script = "script.md" if script_path.exists() else ""
            print(f"{n}  {has_script}")
    else:
        print("(no videos)")


def cmd_delete_brand(project_dir: pathlib.Path):
    brand_dir = project_dir / ".brand"
    if brand_dir.exists():
        shutil.rmtree(brand_dir)
        print(f"ive: deleted \u2014 {brand_dir}")
    else:
        print(f"ive: not found \u2014 {brand_dir}", file=sys.stderr)
        sys.exit(1)


def cmd_delete_video(video_path: str, project_dir: pathlib.Path):
    video_dir = project_dir / ".brand" / "videos" / video_path
    if video_dir.exists() and video_dir.is_dir():
        shutil.rmtree(video_dir)
        print(f"ive: deleted \u2014 {video_dir}")
    else:
        print(f"ive: not found \u2014 {video_dir}", file=sys.stderr)
        sys.exit(1)


def cmd_delete_script(target: str, project_dir: pathlib.Path):
    script_path = project_dir / ".brand" / "videos" / target / "script.md"
    if script_path.exists():
        script_path.unlink()
        print(f"ive: deleted \u2014 {script_path}")
    else:
        print(f"ive: not found \u2014 {script_path}", file=sys.stderr)
        sys.exit(1)


def _clean(text: str) -> str:
    return text.encode("utf-8", errors="surrogatepass").decode("utf-8", errors="replace")


def run_opencode(project_dir: pathlib.Path, prompt: str, message: str, agent: str | None = None, model: str | None = None):
    prompt = _clean(prompt)
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


def gather_context(project_dir: pathlib.Path, include_brand: bool = False) -> str:
    parts = []

    for pattern in ("README.md", "package.json", "pyproject.toml", "Cargo.toml", "composer.json"):
        f = project_dir / pattern
        if f.exists() and f.stat().st_size < 50000:
            parts.append(f"### `{pattern}`\n```\n{f.read_text(encoding='utf-8', errors='replace')[:3000]}\n```\n")

    if include_brand:
        brand_dir = project_dir / ".brand"
        if brand_dir.exists():
            parts.append("### `.brand/` contents\n")
            for f in sorted(brand_dir.rglob("*")):
                if f.is_file() and f.stat().st_size < 100000:
                    rel = f.relative_to(project_dir)
                    parts.append(f"**`{rel}`**\n```\n{f.read_text(encoding='utf-8', errors='replace')[:5000]}\n```\n")

    parts.append("### Project Files\n")
    tree = get_file_tree(project_dir, max_depth=3, include_brand=include_brand)
    parts.append(f"```\n{tree}\n```")

    return "\n".join(parts)


def get_file_tree(project_dir: pathlib.Path, max_depth: int = 3, include_brand: bool = False) -> str:
    ignore = {".git", "node_modules", "__pycache__", ".venv", "target", ".next", "dist", "build"}
    if not include_brand:
        ignore.add(".brand")
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
