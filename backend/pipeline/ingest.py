"""Accept an uploaded photo: confirm it really is a JPEG/PNG, cap its size, drop its metadata."""

import io
import uuid
from pathlib import Path

from PIL import Image

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# shortcut: placeholder limits, set from real capture data once there is some (PRD.md §11)
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024
MAX_PIXEL_DIMENSION = 6000


class UnsupportedFileType(Exception):
    pass


class UploadTooLarge(Exception):
    pass


def upload_path(upload_id) -> Path:
    # One exact filename per id: no globbing, so an id can never match someone else's file.
    return UPLOAD_DIR / f"{upload_id}.img"


def save_upload(file_bytes: bytes) -> str:
    """Validate and store the photo, returning its new id."""
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise UploadTooLarge(f"That file is larger than the {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB limit.")
    try:
        img = Image.open(io.BytesIO(file_bytes))  # reads the real format from the bytes, not the filename
    except (OSError, Image.DecompressionBombError):
        img = None
    # MPO is what some phone cameras write for an ordinary JPEG.
    if img is None or img.format not in ("JPEG", "MPO", "PNG"):
        raise UnsupportedFileType(
            "That file doesn't look like a JPG or PNG image — please upload a photo of your guideline sheet."
        )
    if max(img.size) > MAX_PIXEL_DIMENSION:
        raise UploadTooLarge(f"That image is larger than the {MAX_PIXEL_DIMENSION}px-per-side limit.")

    # Re-saving writes pixels only: EXIF/GPS never reach the file (AGENTS.md §6).
    out = io.BytesIO()
    if img.format == "PNG":
        img.save(out, format="PNG")
    else:
        img.save(out, format="JPEG", quality=95)

    upload_id = str(uuid.uuid4())
    upload_path(upload_id).write_bytes(out.getvalue())
    return upload_id
