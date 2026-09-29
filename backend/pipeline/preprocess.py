"""Preprocess step: grayscale -> binarize -> deskew, in that order.

All three cleanup functions plus run_preprocess() to chain them. Wired
into an endpoint in main.py.
"""

import numpy as np
from PIL import Image


def to_grayscale(img: Image.Image) -> Image.Image:
    return img.convert("L")


def binarize(img: Image.Image, threshold: int = 128) -> Image.Image:
    """Push every pixel to pure black or pure white.

    Expects a grayscale image. Anything darker than `threshold` becomes
    ink (black); everything else becomes paper (white). This threshold
    is a placeholder — real handwriting-photo lighting varies enough
    that it'll likely need to become adaptive once real Milestone 1
    photos are run through it.
    """
    gray = img.convert("L") if img.mode != "L" else img
    return gray.point(lambda p: 0 if p < threshold else 255)


def deskew(img: Image.Image) -> Image.Image:
    """Estimate rotation angle from ink-pixel layout and correct it.

    Expects a binarized image (0 = ink, 255 = paper). Finds the
    principal axis of the ink pixels via PCA and rotates so that axis
    is horizontal. This is a first-pass heuristic — good enough for the
    kill-test, but may need replacing with a more robust method
    (e.g. Hough-line based) if it misbehaves on real photos.
    """
    arr = np.array(img.convert("L") if img.mode != "L" else img)
    ys, xs = np.where(arr < 128)

    if len(xs) < 10:
        return img  # not enough ink to estimate skew reliably

    coords = np.column_stack([xs, ys]).astype(np.float64)
    coords -= coords.mean(axis=0)
    cov = np.cov(coords.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    principal = eigenvectors[:, np.argmax(eigenvalues)]

    angle = np.degrees(np.arctan2(principal[1], principal[0]))
    # Normalize to a small correction range — ink's principal axis could
    # come out closer to vertical than horizontal depending on layout.
    if angle > 45:
        angle -= 90
    elif angle < -45:
        angle += 90

    return img.rotate(angle, expand=True, fillcolor=255)


def run_preprocess(img: Image.Image) -> Image.Image:
    """Chain grayscale -> binarize into one call.

    deskew() is intentionally NOT called here. The self-test (running a
    perfectly axis-aligned synthetic sheet through the pipeline)
    revealed it produces a bogus rotation angle on a full page of
    scattered glyph shapes — PCA over all ink pixels doesn't represent
    true page skew when the ink is spread out in a grid rather than a
    single line of text. It was shifting every glyph out of its box.

    Real rotation/perspective correction is a better fit for M3's
    actual capture flow (correcting against the sheet's known corners),
    not blind ink-PCA at this stage. deskew() is left defined below in
    case it's useful later, just not wired into the default chain.
    """
    gray = to_grayscale(img)
    return binarize(gray)
