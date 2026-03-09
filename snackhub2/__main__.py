import os
import sys
import tempfile
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


def _configure_local_temp_dir(project_root: Path) -> None:
    candidates: list[Path] = []
    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        candidates.append(Path(local_app_data) / "SnackhubTemp")
    candidates.append(project_root / ".tmp")
    candidates.append(Path(tempfile.gettempdir()) / "SnackhubTemp")

    selected: Path | None = None
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            probe = candidate / ".write_test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            selected = candidate
            break
        except Exception:
            continue

    if selected is None:
        print("Warnung: Kein beschreibbarer Temp-Ordner gefunden, nutze System-Default.")
        return

    temp_value = str(selected)
    os.environ["TMP"] = temp_value
    os.environ["TEMP"] = temp_value
    os.environ["TMPDIR"] = temp_value
    tempfile.tempdir = temp_value


_configure_console_encoding()

_project_root = Path(__file__).resolve().parents[1]
_configure_local_temp_dir(_project_root)
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
