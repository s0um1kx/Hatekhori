"""Vectorize step: turn a binarized glyph bitmap into a vector outline.

Uses potracer (https://github.com/tatarize/potrace) — a pure-Python
port of Potrace — chosen deliberately to avoid the C-toolchain build
problems Pillow/pillow-heif already hit on Windows in this project.

This part (5a) only adds the trace function. Converting the traced
Path into an inspectable SVG is 5b; wiring into an endpoint is 5c.
"""

from PIL import Image
from potrace import Bitmap, POTRACE_TURNPOLICY_MINORITY


def trace_glyph(img: Image.Image):
    """Trace a binarized glyph image into a potrace Path.

    Expects dark ink on a light background (as produced by
    preprocess.binarize). Returns a potrace.Path — iterate over its
    curves and their segments to get vector coordinates.
    """
    bitmap = Bitmap(img, blacklevel=0.5)
    return bitmap.trace(
        turdsize=2,
        turnpolicy=POTRACE_TURNPOLICY_MINORITY,
        alphamax=1.0,
        opticurve=True,
        opttolerance=0.2,
    )
