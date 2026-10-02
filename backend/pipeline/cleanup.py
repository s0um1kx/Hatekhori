"""Data retention — implements the table in AGENTS.md §7 / privacy-policy.md:

- Raw uploaded photo: deleted immediately once used (preprocessing is
  the only step that ever reads it — nothing downstream touches the
  original upload again), or within 24h regardless if abandoned.
- Generated font + glyphs/vectors/metrics: kept 30 days for re-download,
  then purged.

This part (1) only adds delete_raw_upload, the immediate-on-use path.
Part 2 adds the 24h/30-day sweep functions; part 3 runs them
automatically in the background.
"""

import shutil
import time
from pathlib import Path

from pipeline.ingest import UPLOAD_DIR

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

UPLOAD_MAX_AGE_HOURS = 24
OUTPUT_MAX_AGE_DAYS = 30


def delete_raw_upload(upload_id: str) -> None:
    """Delete the raw uploaded file for this id, if it still exists.

    Safe to call even if the file is already gone (e.g. called twice,
    or already swept) — deletion is best-effort, not an error if
    there's nothing to delete.
    """
    for match in UPLOAD_DIR.glob(f"{upload_id}.*"):
        match.unlink(missing_ok=True)


def sweep_old_uploads(max_age_hours: float = UPLOAD_MAX_AGE_HOURS) -> int:
    """Delete any raw upload file older than max_age_hours.

    Safety net for uploads that never reached /preprocess — an
    abandoned or failed flow, where delete_raw_upload()'s normal
    on-use deletion never got triggered. Returns how many were removed.
    """
    cutoff = time.time() - max_age_hours * 3600
    deleted = 0
    for path in UPLOAD_DIR.iterdir():
        if path.is_file() and path.stat().st_mtime < cutoff:
            path.unlink(missing_ok=True)
            deleted += 1
    return deleted


def sweep_old_outputs(max_age_days: float = OUTPUT_MAX_AGE_DAYS) -> int:
    """Delete any output/<id> folder older than max_age_days.

    Per AGENTS.md §7: generated fonts are kept 30 days for re-download,
    then purged server-side. Returns how many folders were removed.
    """
    cutoff = time.time() - max_age_days * 86400
    deleted = 0
    for path in OUTPUT_DIR.iterdir():
        if path.is_dir() and path.stat().st_mtime < cutoff:
            shutil.rmtree(path, ignore_errors=True)
            deleted += 1
    return deleted
