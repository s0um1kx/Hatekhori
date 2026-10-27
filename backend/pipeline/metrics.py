"""Where the ink is inside a glyph crop."""

import numpy as np
from PIL import Image


def glyph_ink_bbox(img: Image.Image) -> tuple[int, int, int, int] | None:
    """(left, top, right, bottom) of the dark pixels in a binarized crop, or None if it is blank."""
    ys, xs = np.where(np.array(img.convert("L")) < 128)
    if len(xs) == 0:
        return None
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
