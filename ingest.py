"""File ingestion and security guardrails for Hatekhori.

Implements non-negotiable ingest requirements per AGENTS.md §6:
1. Real content-sniffing on file bytes (magic bytes).
2. Hard caps on file size (20 MB) and pixel dimensions (8000 x 8000).
3. EXIF metadata stripping on ingest, always, no exceptions.
4. Considered, kind error messages per AGENTS.md §10.
"""

from __future__ import annotations

import io
import os
from typing import Tuple, Optional
from PIL import Image


# Non-negotiable limits
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB
MAX_PIXEL_DIMENSION = 8000              # 8000 x 8000 pixels

# Magic byte signatures
MAGIC_JPEG = b"\xff\xd8\xff"
MAGIC_PNG = b"\x89PNG\r\n\x1a\n"


class IngestError(Exception):
    """Raised when an uploaded handwriting sample fails ingestion guardrails."""
    def __init__(self, message: str, kind_reason: str):
        super().__init__(message)
        self.kind_reason = kind_reason


def sniff_image_format(data: bytes) -> str:
    """Sniff raw file bytes to determine the actual image format.

    Rejects files whose content does not match genuine JPEG or PNG magic signatures.
    """
    if len(data) < 8:
        raise IngestError(
            "File is too short to be a valid image",
            "This file seems incomplete or empty. Please check the photo and try uploading again.",
        )

    if data.startswith(MAGIC_PNG):
        return "PNG"
    elif data.startswith(MAGIC_JPEG):
        return "JPEG"
    else:
        raise IngestError(
            "Invalid file signature",
            "We could not recognize this image format. Please submit a standard JPEG or PNG photo of your guideline sheet.",
        )


def load_and_sanitize_image(
    file_source: str | bytes | io.BytesIO,
) -> Tuple[Image.Image, dict]:
    """Ingest, validate, and sanitize an input handwriting image.

    - Reads raw bytes and checks file size limits.
    - Performs magic byte sniffing.
    - Strips all EXIF metadata by loading raw pixel data into a fresh PIL Image.
    - Validates pixel dimensions against safety caps.

    Returns:
        (sanitized_pil_image, metadata_dict)
    """
    raw_bytes: bytes

    if isinstance(file_source, str):
        if not os.path.exists(file_source):
            raise IngestError(
                f"File not found: {file_source}",
                "The specified file could not be found. Please check the file path and try again.",
            )
        file_size = os.path.getsize(file_source)
        if file_size > MAX_FILE_SIZE_BYTES:
            size_mb = file_size / (1024 * 1024)
            raise IngestError(
                f"File size {size_mb:.1f} MB exceeds limit",
                f"This image is {size_mb:.1f} MB, which is a bit too large for processing. Please keep uploads under 20 MB.",
            )
        with open(file_source, "rb") as f:
            raw_bytes = f.read()

    elif isinstance(file_source, bytes):
        if len(file_source) > MAX_FILE_SIZE_BYTES:
            size_mb = len(file_source) / (1024 * 1024)
            raise IngestError(
                f"File size {size_mb:.1f} MB exceeds limit",
                f"This image is {size_mb:.1f} MB, which exceeds our 20 MB cap. Please try a smaller photo.",
            )
        raw_bytes = file_source

    elif isinstance(file_source, io.BytesIO):
        raw_bytes = file_source.getvalue()
        if len(raw_bytes) > MAX_FILE_SIZE_BYTES:
            size_mb = len(raw_bytes) / (1024 * 1024)
            raise IngestError(
                f"File size {size_mb:.1f} MB exceeds limit",
                f"This image is {size_mb:.1f} MB, which exceeds our 20 MB cap. Please try a smaller photo.",
            )
    else:
        raise IngestError(
            "Unsupported file source",
            "We were unable to read this file. Please provide a path or byte stream to an image.",
        )

    # 1. Content-sniffing on bytes
    fmt = sniff_image_format(raw_bytes)

    # 2. Open image securely
    try:
        with Image.open(io.BytesIO(raw_bytes)) as pil_img:
            # Check dimensions before processing
            w, h = pil_img.size
            if w > MAX_PIXEL_DIMENSION or h > MAX_PIXEL_DIMENSION:
                raise IngestError(
                    f"Dimensions {w}x{h} exceed cap {MAX_PIXEL_DIMENSION}",
                    f"This image has dimensions {w}×{h} px, which exceeds our maximum limit of {MAX_PIXEL_DIMENSION}×{MAX_PIXEL_DIMENSION} px.",
                )

            # 3. Strip EXIF metadata completely:
            # Convert to RGB and copy raw raster data into a brand new Image instance with no info/exif dicts.
            rgb_img = pil_img.convert("RGB")
            sanitized = Image.new("RGB", rgb_img.size)
            sanitized.putdata(list(rgb_img.getdata()))
            # Ensure info dictionary is empty
            sanitized.info = {}

    except IngestError:
        raise
    except Exception as e:
        raise IngestError(
            f"Failed to decode image: {e}",
            "We were unable to decode this image. It may be damaged or saved in an unexpected format.",
        )

    metadata = {
        "format": fmt,
        "width": sanitized.width,
        "height": sanitized.height,
        "size_bytes": len(raw_bytes),
        "exif_stripped": True,
    }

    return sanitized, metadata
