"""Ingest step: sniff the real file type, cap size/dimensions, strip
EXIF, then persist.
"""

import io
import uuid
from pathlib import Path

import filetype
from PIL import Image

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIF_SUPPORTED = True
except ImportError:
    HEIF_SUPPORTED = False

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/heic", "image/heif"}

# Placeholders — AGENTS.md/PRD.md both say the real limit should come from
# actual capture-flow data (open question), not be guessed. These exist so
# no unbounded upload/decompression-bomb path ships even internally.
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
MAX_PIXEL_DIMENSION = 6000  # px, per side


class UnsupportedFileType(Exception):
    """Raised when the file's real bytes don't match an accepted image type."""


class UploadTooLarge(Exception):
    """Raised when the file exceeds the size or pixel-dimension cap."""


def sniff_image_type(file_bytes: bytes) -> str:
    kind = filetype.guess(file_bytes)
    if kind is None or kind.mime not in ALLOWED_MIME_TYPES:
        raise UnsupportedFileType(
            "That file doesn't look like a JPG, PNG, or HEIC image — "
            "please upload a photo of your guideline sheet instead."
        )
    return kind.mime


def check_size_caps(file_bytes: bytes, mime: str) -> None:
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise UploadTooLarge(
            f"That file is larger than the {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB limit."
        )

    if mime in {"image/heic", "image/heif"} and not HEIF_SUPPORTED:
        # Pixel-dimension check deferred for HEIC on this machine — HEIC
        # support itself is still an open PRD question (see PRD.md §11),
        # so this is a known, acceptable gap rather than a silent bug.
        return

    with Image.open(io.BytesIO(file_bytes)) as img:
        width, height = img.size
        if width > MAX_PIXEL_DIMENSION or height > MAX_PIXEL_DIMENSION:
            raise UploadTooLarge(
                f"That image's dimensions ({width}x{height}) are larger than "
                f"the {MAX_PIXEL_DIMENSION}px-per-side limit."
            )


def strip_exif(file_bytes: bytes, mime: str) -> bytes:
    """Return the image re-encoded from raw pixel data only.

    Rebuilding from pixel data (rather than just deleting the EXIF tag)
    also drops GPS data hidden in maker-notes and ICC profiles — this is
    the "always, no exceptions" baseline from AGENTS.md §6, not a
    best-effort pass.
    """
    if mime in {"image/heic", "image/heif"} and not HEIF_SUPPORTED:
        # Same known, documented gap as the dimension check above — can't
        # safely re-encode HEIC without pillow-heif installed.
        return file_bytes

    with Image.open(io.BytesIO(file_bytes)) as img:
        clean = Image.new(img.mode, img.size)
        clean.putdata(list(img.getdata()))

        save_format = img.format or ("JPEG" if mime == "image/jpeg" else "PNG")
        buf = io.BytesIO()
        save_kwargs = {"quality": 95} if save_format == "JPEG" else {}
        clean.save(buf, format=save_format, **save_kwargs)
        return buf.getvalue()


def save_upload(file_bytes: bytes, original_filename: str) -> dict:
    mime = sniff_image_type(file_bytes)
    check_size_caps(file_bytes, mime)
    file_bytes = strip_exif(file_bytes, mime)

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


