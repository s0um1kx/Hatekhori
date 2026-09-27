"""Compile step: vectors + metrics -> a real .otf font file.

This part (7a) only adds the pen-drawing helper that turns a potrace
Path into calls on a fontTools pen. Building the actual glyph
charstrings is 7b, and 7c wires the whole thing into an endpoint that
produces a downloadable font file.
"""


def draw_potrace_path(pen, trace_path, crop_height: float) -> None:
    """Replay a potrace Path's curves onto a fontTools pen.

    Image coordinates have y increasing downward from the top; font
    coordinates have y increasing upward from the baseline. Per the
    baseline convention set in metrics.py (baseline = bottom of the
    glyph's own crop), flipping is just `crop_height - y`.
    """

    def flip(point):
        return (point.x, crop_height - point.y)

    for curve in trace_path:
        pen.moveTo(flip(curve.start_point))
        for segment in curve.segments:
            if segment.is_corner:
                pen.lineTo(flip(segment.c))
                pen.lineTo(flip(segment.end_point))
            else:
                pen.curveTo(flip(segment.c1), flip(segment.c2), flip(segment.end_point))
        pen.closePath()
