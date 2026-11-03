"""Where the ink is inside a glyph crop."""

import numpy as np
from PIL import Image


def glyph_has_ink(img: Image.Image) -> bool:
    """Fast check if there is any dark ink in a crop without allocating coordinate arrays."""
    gray = img if img.mode == "L" else img.convert("L")
    return gray.getextrema()[0] < 128


def glyph_ink_bbox(img: Image.Image) -> tuple[int, int, int, int] | None:
    """(left, top, right, bottom) of the dark pixels in a binarized crop, or None if it is blank."""
    gray = img if img.mode == "L" else img.convert("L")
    if not glyph_has_ink(gray):
        return None
    ys, xs = np.where(np.asarray(gray) < 128)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
