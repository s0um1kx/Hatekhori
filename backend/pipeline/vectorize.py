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


def path_to_svg(path, width: int, height: int) -> str:
    """Render a traced potrace Path as an SVG string, for visual inspection.

    Follows the conversion shown in potracer's own README: walk each
    curve's segments, emitting line commands for corners and cubic
    Bezier commands otherwise.
    """
    parts = []
    for curve in path:
        start = curve.start_point
        parts.append(f"M{start.x},{start.y}")
        for segment in curve.segments:
            if segment.is_corner:
                a = segment.c
                b = segment.end_point
                parts.append(f"L{a.x},{a.y}L{b.x},{b.y}")
            else:
                a = segment.c1
                b = segment.c2
                c = segment.end_point
                parts.append(f"C{a.x},{a.y} {b.x},{b.y} {c.x},{c.y}")
        parts.append("z")

    path_data = "".join(parts)
    return (
        f'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f'<path stroke="none" fill="black" fill-rule="evenodd" d="{path_data}"/>'
        f"</svg>"
    )
