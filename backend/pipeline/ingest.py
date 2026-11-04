"""Accept an uploaded photo: confirm it really is a JPEG/PNG, cap its size, drop its metadata."""

import hashlib
import io
import time
import uuid
from pathlib import Path

from PIL import Image, ImageOps

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

from pipeline.cleanup import OUTPUT_DIR, UPLOAD_DIR

# shortcut: placeholder limits, set from real capture data once there is some (PRD.md §11)
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024
MAX_PIXEL_DIMENSION = 6000
# Hard-limit pixel decode count to eliminate decompression bombs before raster allocation
Image.MAX_IMAGE_PIXELS = 36_000_000
REJECTED_HASHES_FILE = OUTPUT_DIR / "rejected_hashes.log"


def log_rejected_hash(file_input: bytes | Path, reason: str) -> None:
    """Record SHA-256 hash of rejected uploads for abuse tracking without retaining raw images (PRD §6a)."""
    try:
        hasher = hashlib.sha256()
        if isinstance(file_input, Path):
            with open(file_input, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
        else:
            hasher.update(file_input)
        entry = f"{time.time():.0f}\t{hasher.hexdigest()}\t{reason}\n"
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


def save_upload(file_input: bytes | Path) -> str:
    """Validate and store the photo, returning its new id.

    Accepts raw bytes or a Path to a temporary file on disk. Caller cleans up temporary files.
    """
    is_path = isinstance(file_input, Path)
    file_size = file_input.stat().st_size if is_path else len(file_input)

    if file_size > MAX_FILE_SIZE_BYTES:
        log_rejected_hash(file_input, "upload_too_large_bytes")
        raise UploadTooLarge(f"That file is larger than the {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB limit.")

    try:
        with Image.open(file_input if is_path else io.BytesIO(file_input)) as img_file:
            fmt_raw = img_file.format
            size_raw = img_file.size
            if fmt_raw not in ("JPEG", "MPO", "PNG", "HEIF"):
                log_rejected_hash(file_input, "unsupported_or_corrupt_file_format")
                raise UnsupportedFileType(
                    "That file doesn't look like a JPG, PNG, or HEIC image — please upload a photo of your guideline sheet."
                )

            if max(size_raw) > MAX_PIXEL_DIMENSION:
                log_rejected_hash(file_input, "dimensions_too_large")
                raise UploadTooLarge(f"That image is larger than the {MAX_PIXEL_DIMENSION}px-per-side limit.")

            fmt = "PNG" if fmt_raw == "PNG" else "JPEG"
            img = ImageOps.exif_transpose(img_file)
            if fmt == "JPEG" and img.mode != "RGB":
                # Flatten alpha/palette to white background for clean OCR/tracing
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else img.convert("RGBA").split()[-1])
                    img = bg
                else:
                    img = img.convert("RGB")
            img.load()
    except (OSError, Image.DecompressionBombError):
        log_rejected_hash(file_input, "unsupported_or_corrupt_file_format")
        raise UnsupportedFileType(
            "That file doesn't look like a JPG, PNG, or HEIC image — please upload a photo of your guideline sheet."
        )

    upload_id = str(uuid.uuid4())
    dest_path = upload_path(upload_id)
    # Re-saving writes pixels only: EXIF/GPS never reach the file (AGENTS.md §6).
    img.save(dest_path, format=fmt, **({"quality": 95} if fmt == "JPEG" else {}))
    img.close()

    return upload_id
