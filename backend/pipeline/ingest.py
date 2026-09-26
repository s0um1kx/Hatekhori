"""Ingest step: take raw uploaded bytes, persist them, hand back an id.

Validation (content-sniffing, size/dimension caps, EXIF strip) is added
in parts 2b/2c/2d — this part only proves the upload path works end to
end.
"""

import uuid
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def save_upload(file_bytes: bytes, original_filename: str) -> dict:
    upload_id = str(uuid.uuid4())
    suffix = Path(original_filename).suffix
    dest = UPLOAD_DIR / f"{upload_id}{suffix}"
    dest.write_bytes(file_bytes)
    return {
        "id": upload_id,
        "stored_path": str(dest),
        "original_filename": original_filename,
        "size_bytes": len(file_bytes),
    }
