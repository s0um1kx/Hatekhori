"""Perspective correction using the 4 corner markers found by
validate.find_corner_markers().

This is what properly replaces the disabled deskew step (see
preprocess.py) — instead of guessing a rotation angle from ink
distribution, it uses 4 known reference points to compute a real
geometric correction, warping the photo into the exact canonical shape
segment.py's grid math assumes.
"""

import numpy as np
from PIL import Image

from pipeline.sheet import SHEET_HEIGHT, SHEET_WIDTH, corner_marker_boxes

# Consistent ordering used to pair up source/destination points.
CORNER_ORDER = ["top_left", "top_right", "bottom_right", "bottom_left"]


def _canonical_marker_centers() -> dict:
    boxes = corner_marker_boxes(SHEET_WIDTH, SHEET_HEIGHT)
    return {name: ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2) for name, b in boxes.items()}


def _find_perspective_coeffs(dest_pts, src_pts) -> np.ndarray:
    """Solve for the 8 coefficients PIL's Image.transform(..., PERSPECTIVE,
    coeffs) needs.

    PIL samples the OUTPUT image by mapping each output (x, y) to an
    input coordinate via those coefficients — so `dest_pts` (canonical,
    output-space) and `src_pts` (detected, input-space) go in that
    order, not reversed.
    """
    matrix = []
    for (x, y), (src_x, src_y) in zip(dest_pts, src_pts):
        matrix.append([x, y, 1, 0, 0, 0, -src_x * x, -src_x * y])
        matrix.append([0, 0, 0, x, y, 1, -src_y * x, -src_y * y])

    a = np.array(matrix, dtype=np.float64)
    b = np.array(src_pts, dtype=np.float64).reshape(8)
    return np.linalg.solve(a, b)


def correct_perspective(img: Image.Image, marker_centers: dict) -> Image.Image:
    """Warp `img` so its 4 detected markers land on their canonical
    positions, producing a SHEET_WIDTH x SHEET_HEIGHT image in the same
    coordinate system segment.py's grid math expects.
    """
    canonical = _canonical_marker_centers()
    dest_pts = [canonical[name] for name in CORNER_ORDER]
    src_pts = [marker_centers[name] for name in CORNER_ORDER]

    coeffs = _find_perspective_coeffs(dest_pts, src_pts)

    return img.transform(
        (SHEET_WIDTH, SHEET_HEIGHT),
        Image.PERSPECTIVE,
        coeffs,
        resample=Image.BICUBIC,
    )
