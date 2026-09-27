"""Metrics step: baseline, x-height, side-bearings, spacing.

This part (6a) only adds ink-bounding-box detection, the building block
everything else in this file is computed from. Side-bearings come in
6b, global font metrics (baseline/x-height) in 6c's wiring.
"""

import numpy as np
from PIL import Image


def glyph_ink_bbox(img: Image.Image) -> tuple[int, int, int, int] | None:
    """Return (left, top, right, bottom) of the ink pixels in a glyph crop.

    Expects a binarized image (0 = ink, 255 = paper), as produced by
    preprocess.binarize. Returns None if the crop has no ink at all
    (e.g. an empty guideline-sheet box, or — as expected right now —
    a crop that landed on blank paper because the grid geometry isn't
    validated against a real sheet yet).
    """
    arr = np.array(img.convert("L") if img.mode != "L" else img)
    ys, xs = np.where(arr < 128)

    if len(xs) == 0:
        return None

    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
