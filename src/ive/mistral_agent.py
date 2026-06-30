import json
import os
import pathlib
import platform
import subprocess
import sys
from typing import Any

import mistralai

from .config import load_api_key


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to project directory",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file (creates parent directories if needed)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to project directory",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edit a file by replacing the first occurrence of a string",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to project directory",
                    },
                    "old_string": {
                        "type": "string",
                        "description": "Text to replace",
                    },
                    "new_string": {
                        "type": "string",
                        "description": "Replacement text",
                    },
                },
                "required": ["path", "old_string", "new_string"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a shell command in the project directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "glob_files",
            "description": "Find files matching a glob pattern recursively",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern (e.g. **/*.tsx)",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and directories in a path relative to project",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path relative to project",
                    },
                },
                "required": ["path"],
            },
        },
    },
]


def _handle_tool_call(name: str, args: dict[str, Any], work_dir: pathlib.Path) -> str:
    match name:
        case "read_file":
            path = work_dir / args["path"]
            try:
                return path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                return f"Error: {e}"

        case "write_file":
            path = work_dir / args["path"]
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(args["content"], encoding="utf-8")
                return f"Written {len(args['content'])} bytes to {args['path']}"
            except Exception as e:
                return f"Error: {e}"

        case "edit_file":
            path = work_dir / args["path"]
            try:
                content = path.read_text(encoding="utf-8")
                if args["old_string"] not in content:
                    return f"Error: old_string not found in {args['path']}"
                content = content.replace(args["old_string"], args["new_string"], 1)
                path.write_text(content, encoding="utf-8")
                return f"Edited 1 occurrence in {args['path']}"
            except Exception as e:
                return f"Error: {e}"

        case "run_command":
            try:
                result = subprocess.run(
                    args["command"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(work_dir),
                )
                output = result.stdout
                if result.stderr:
                    output += "\n--- stderr ---\n" + result.stderr
                if result.returncode != 0:
                    output += f"\n--- exit code {result.returncode} ---"
                if not output.strip():
                    output = "(no output)"
                return output
            except subprocess.TimeoutExpired:
                return "Error: Command timed out after 120s"
            except Exception as e:
                return f"Error: {e}"

        case "glob_files":
            try:
                matches = list(work_dir.rglob(args["pattern"]))
                return "\n".join(str(m.relative_to(work_dir)) for m in matches)
            except Exception as e:
                return f"Error: {e}"

        case "list_directory":
            path = work_dir / args["path"]
            try:
                entries = sorted(
                    f"{e.name}{'/' if e.is_dir() else ''}"
                    for e in path.iterdir()
                    if not e.name.startswith(".")
                )
                return "\n".join(entries) if entries else "(empty)"
            except Exception as e:
                return f"Error: {e}"

    return f"Unknown tool: {name}"


def _get_api_key() -> str:
    key = load_api_key()
    if key:
        return key
    print("ive: No Mistral API key found. Set MISTRAL_API_KEY env var or run `ive auth login mistral`", file=sys.stderr)
    sys.exit(1)


_os_info: str | None = None


def _get_os_info() -> str:
    global _os_info
    if _os_info is None:
        system = platform.system()
        release = platform.release()
        machine = platform.machine()
        if system == "Windows":
            import struct
            bits = 8 * struct.calcsize("P")
            _os_info = f"Windows {release} ({bits}-bit) on {machine}"
        elif system == "Linux":
            try:
                with open("/etc/os-release") as f:
                    data = dict(
                        l.split("=", 1)
                        for l in f.read().splitlines()
                        if "=" in l
                    )
                distro = data.get("PRETTY_NAME", data.get("ID", "Linux")).strip('"')
            except OSError:
                distro = "Linux"
            _os_info = f"{distro} kernel {release} on {machine}"
        elif system == "Darwin":
            _os_info = f"macOS {release} on {machine}"
        else:
            _os_info = f"{system} {release} on {machine}"
    return _os_info


def run_mistral(
    project_dir: pathlib.Path,
    prompt: str,
    message: str,
    model: str | None = None,
    agent: str | None = None,
):
    api_key = _get_api_key()
    client = mistralai.Mistral(api_key=api_key)
    model_name = model or os.environ.get("MISTRAL_MODEL", "mistral-large-latest")

    system = (
        f"You are an automated agent working in the project directory {project_dir}. "
        f"The host system is {_get_os_info()}. "
        f"You have tools for reading/writing files, running commands, and exploring "
        f"the filesystem. Use these tools to complete the task. "
        f"When you are done, summarize what you did."
    )

    print(f"ive: {message}...")

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]

    while True:
        try:
            response = client.chat.complete(
                model=model_name,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
        except Exception as e:
            print(f"ive: Mistral API error: {e}", file=sys.stderr)
            sys.exit(1)

        choice = response.choices[0]
        msg = choice.message

        if not msg.tool_calls:
            if msg.content:
                print(msg.content)
            break

        tool_calls_dict = []
        for tc in msg.tool_calls:
            tool_calls_dict.append({
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            })

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": tool_calls_dict,
        })

        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError as e:
                result = f"Error: Invalid JSON arguments: {e}"
            else:
                result = _handle_tool_call(tc.function.name, args, project_dir)
                # Truncate very large results
                if len(result) > 50000:
                    result = result[:50000] + "\n... (truncated)"

            messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tc.id,
            })
