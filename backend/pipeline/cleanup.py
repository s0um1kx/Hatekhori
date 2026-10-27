"""Retention (AGENTS.md §7): raw uploads live at most 24h, generated fonts 30 days."""

import time
from pathlib import Path

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

UPLOAD_MAX_AGE_S = 24 * 3600
OUTPUT_MAX_AGE_S = 30 * 24 * 3600


def sweep(directory: Path, max_age_s: float) -> None:
    cutoff = time.time() - max_age_s
    for path in directory.iterdir():
        if path.is_file() and path.stat().st_mtime < cutoff:
            path.unlink(missing_ok=True)
