"""Image cleanup (OpenCV adaptive thresholding) and file retention (AGENTS.md §7)."""

import os
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

BASE_DIR = Path(os.getenv("HATEKHORI_DATA_DIR", Path(__file__).resolve().parent.parent.parent))
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Retention limits (PRD.md §6b)
UPLOAD_MAX_AGE_S = 3600  # Abandoned uploads purged after 1 hour (successful ones deleted immediately)
OUTPUT_MAX_AGE_S = 30 * 24 * 3600  # Generated fonts kept for 30 days
UPLOAD_MAX_FILES = 100
UPLOAD_MAX_BYTES = 50 * 1024 * 1024  # 50 MB
OUTPUT_MAX_FILES = 1000
OUTPUT_MAX_BYTES = 200 * 1024 * 1024  # 200 MB


def binarize_sheet(sheet: Image.Image) -> Image.Image:
    """OpenCV adaptive thresholding and morphological cleanup.

    Eliminates camera shadows, uneven room lighting, and paper grain,
    converting the rectified grayscale sheet into clean binary ink on paper.
    Returns a PIL Image with 0 for dark ink and 255 for paper.
    """
    arr = np.array(sheet.convert("L"))
    # Adaptive threshold handles lighting gradients across phone captures
    clean = cv2.adaptiveThreshold(
        arr, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, 12
    )
    # Median blur suppresses isolated salt-and-pepper camera noise without dulling stroke corners
    clean = cv2.medianBlur(clean, 3)
    return Image.fromarray(clean, mode="L")


def sweep(
    directory: Path,
    max_age_s: float,
    max_files: int | None = None,
    max_bytes: int | None = None,
) -> None:
    """Purge files older than max_age_s and enforce LRU quota caps (oldest first)."""
    if not directory.exists():
        return
    cutoff = time.time() - max_age_s
    surviving = []
    total_bytes = 0

    for path in directory.iterdir():
        if path.is_file():
            try:
                st = path.stat()
            except OSError:
                continue
            if st.st_mtime < cutoff:
                try:
                    path.unlink(missing_ok=True)
                except OSError:
                    pass
            else:
                surviving.append((st.st_mtime, st.st_size, path))
                total_bytes += st.st_size

    # LRU quota eviction: oldest first if file count or total directory size exceeds caps
    if (max_files and len(surviving) > max_files) or (max_bytes and total_bytes > max_bytes):
        surviving.sort(key=lambda x: x[0])  # oldest first
        remaining_count = len(surviving)
        for _, size, path in surviving:
            if (not max_files or remaining_count <= max_files) and (
                not max_bytes or total_bytes <= max_bytes
            ):
                break
            try:
                path.unlink(missing_ok=True)
                total_bytes -= size
                remaining_count -= 1
            except OSError:
                pass
