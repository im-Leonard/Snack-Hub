import os
from pathlib import Path


def load_env_files(paths: list[Path], override: bool = False) -> None:
    for path in paths:
        _load_single_env_file(path, override=override)


def _load_single_env_file(path: Path, override: bool = False) -> None:
    if not path.exists() or not path.is_file():
        return

    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.lower().startswith("export "):
            line = line[7:].strip()

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]

        if not override and key in os.environ and os.environ.get(key):
            continue

        os.environ[key] = value
