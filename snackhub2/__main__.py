import sys
from pathlib import Path

from snackhub2.services.env_loader import load_env_files


def _configure_console_encoding() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


_configure_console_encoding()

_project_root = Path(__file__).resolve().parents[1]
load_env_files(
    [
        _project_root / ".env",
        Path.cwd() / ".env",
    ],
    override=False,
)

from snackhub2.main import run_app


if __name__ == "__main__":
    run_app()
