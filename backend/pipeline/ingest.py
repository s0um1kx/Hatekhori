"""Ingest step: sniff the real file type from bytes, then persist.

Size/pixel-dimension caps are added in 2c, EXIF stripping in 2d.
"""

import uuid
from pathlib import Path

import filetype

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/heic", "image/heif"}


class UnsupportedFileType(Exception):
    """Raised when the file's real bytes don't match an accepted image type."""


def sniff_image_type(file_bytes: bytes) -> str:
    kind = filetype.guess(file_bytes)
    if kind is None or kind.mime not in ALLOWED_MIME_TYPES:
        raise UnsupportedFileType(
            "That file doesn't look like a JPG, PNG, or HEIC image — "
            "please upload a photo of your guideline sheet instead."
        )
    return kind.mime


def save_upload(file_bytes: bytes, original_filename: str) -> dict:
    mime = sniff_image_type(file_bytes)

    upload_id = str(uuid.uuid4())
    suffix = Path(original_filename).suffix
    dest = UPLOAD_DIR / f"{upload_id}{suffix}"
    dest.write_bytes(file_bytes)
    return {
        "id": upload_id,
        "stored_path": str(dest),
        "original_filename": original_filename,
        "size_bytes": len(file_bytes),
        "detected_mime": mime,
    }

