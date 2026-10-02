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

from pathlib import Path

from pipeline.ingest import UPLOAD_DIR


def delete_raw_upload(upload_id: str) -> None:
    """Delete the raw uploaded file for this id, if it still exists.

    Safe to call even if the file is already gone (e.g. called twice,
    or already swept) — deletion is best-effort, not an error if
    there's nothing to delete.
    """
    for match in UPLOAD_DIR.glob(f"{upload_id}.*"):
        match.unlink(missing_ok=True)
