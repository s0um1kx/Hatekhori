"""Accept an uploaded photo: confirm it really is a JPEG/PNG, cap its size, drop its metadata."""

import hashlib
import io
import time
import uuid
from pathlib import Path

from PIL import Image, ImageOps

from pipeline.cleanup import OUTPUT_DIR, UPLOAD_DIR

# shortcut: placeholder limits, set from real capture data once there is some (PRD.md §11)
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024
MAX_PIXEL_DIMENSION = 6000
# Hard-limit pixel decode count to eliminate decompression bombs before raster allocation
Image.MAX_IMAGE_PIXELS = 36_000_000
REJECTED_HASHES_FILE = OUTPUT_DIR / "rejected_hashes.log"


def log_rejected_hash(file_bytes: bytes, reason: str) -> None:
    """Record SHA-256 hash of rejected uploads for abuse tracking without retaining raw images (PRD §6a)."""
    try:
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        entry = f"{time.time():.0f}\t{sha256}\t{reason}\n"
        with open(REJECTED_HASHES_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except OSError:
        pass


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
        log_rejected_hash(file_bytes[:1024], "upload_too_large_bytes")
        raise UploadTooLarge(f"That file is larger than the {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB limit.")
    try:
        img = Image.open(io.BytesIO(file_bytes))  # reads the real format from the bytes, not the filename
    except (OSError, Image.DecompressionBombError):
        img = None
    # MPO is what some phone cameras write for an ordinary JPEG.
    if img is None or img.format not in ("JPEG", "MPO", "PNG"):
        log_rejected_hash(file_bytes, "unsupported_or_corrupt_file_format")
        raise UnsupportedFileType(
            "That file doesn't look like a JPG or PNG image — please upload a photo of your guideline sheet."
        )
    if max(img.size) > MAX_PIXEL_DIMENSION:
        log_rejected_hash(file_bytes, "dimensions_too_large")
        raise UploadTooLarge(f"That image is larger than the {MAX_PIXEL_DIMENSION}px-per-side limit.")

    # Phones often store a portrait photo sideways plus a "rotate me" flag. Viewers obey the
    # flag; our pipeline wouldn't, and would file every letter in the wrong box. Apply it now.
    fmt = "PNG" if img.format == "PNG" else "JPEG"
    img = ImageOps.exif_transpose(img)

    # Re-saving writes pixels only: EXIF/GPS never reach the file (AGENTS.md §6).
    out = io.BytesIO()
    img.save(out, format=fmt, **({"quality": 95} if fmt == "JPEG" else {}))

    upload_id = str(uuid.uuid4())
    upload_path(upload_id).write_bytes(out.getvalue())
    return upload_id
