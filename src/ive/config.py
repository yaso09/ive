import json
import os
import pathlib
import stat
import sys


def config_dir() -> pathlib.Path:
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return pathlib.Path(appdata) / "ive"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return pathlib.Path(xdg) / "ive"
    return pathlib.Path.home() / ".config" / "ive"


def auth_path() -> pathlib.Path:
    return config_dir() / "auth.json"


def load_api_key() -> str | None:
    env = os.environ.get("MISTRAL_API_KEY")
    if env:
        return env
    p = auth_path()
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            return data.get("mistral_api_key")
        except (json.JSONDecodeError, OSError):
            pass
    return None


def save_api_key(key: str) -> pathlib.Path:
    d = config_dir()
    d.mkdir(parents=True, exist_ok=True)
    p = auth_path()
    p.write_text(
        json.dumps({"mistral_api_key": key}, indent=2),
        encoding="utf-8",
    )
    if sys.platform != "win32":
        p.chmod(stat.S_IRUSR | stat.S_IWUSR)
    return p
