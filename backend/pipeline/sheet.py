"""Generates the printable guideline sheet for Milestone 1's English
kill-test.

Uses segment.compute_grid_boxes() directly, rather than reimplementing
the geometry — this is the whole point: the sheet you print and the
grid the pipeline expects to crop are the same math, not two things
that might drift apart.

This part (9a) draws boxes + labels. 9b wires it into something you
actually run to produce and save the PNG.
"""

from PIL import Image, ImageDraw, ImageFont

from pipeline.segment import compute_grid_boxes

# A4 at 150 DPI. Paper size isn't specified anywhere in AGENTS.md/PRD.md
# (it's one of the open questions) — A4 is the reasonable default given
# the primary audience is in India.
SHEET_WIDTH = 1240
SHEET_HEIGHT = 1754

# Four solid black squares, one per corner, sitting inside the sheet's
# outer margin (outside the glyph grid, which starts at MARGIN_FRAC in
# segment.py — so markers never overlap a glyph box). These let the
# pipeline (a) confirm a photo is actually of a Hatekhori sheet before
# processing it, and (b) find the sheet's real corners in a photo to
# perspective-correct it, rather than assuming the photo is already
# cropped tight.
CORNER_MARKER_SIZE = 40
CORNER_MARKER_INSET = 20


def corner_marker_boxes(width: int, height: int) -> dict:
    """Return {corner_name: (x0, y0, x1, y1)} for all four markers."""
    s = CORNER_MARKER_SIZE
    m = CORNER_MARKER_INSET
    return {
        "top_left": (m, m, m + s, m + s),
        "top_right": (width - m - s, m, width - m, m + s),
        "bottom_left": (m, height - m - s, m + s, height - m),
        "bottom_right": (width - m - s, height - m - s, width - m, height - m),
    }


def draw_corner_markers(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    for box in corner_marker_boxes(width, height).values():
        draw.rectangle(box, fill=0)


def generate_guideline_sheet() -> Image.Image:
    """Render the printable sheet: one box per glyph, each labeled with
    the character to write inside it, plus corner markers.
    """
    img = Image.new("L", (SHEET_WIDTH, SHEET_HEIGHT), color=255)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    for entry in compute_grid_boxes(SHEET_WIDTH, SHEET_HEIGHT):
        x0, y0, x1, y1 = entry["box"]
        char = entry["char"]
        draw.rectangle([x0, y0, x1, y1], outline=0, width=1)

        # Label sits in the gutter ABOVE the box, not inside it — unlike
        # an earlier version that placed it just inside the box's
        # corner, this guarantees the label's ink can never be captured
        # by segment.py's crop regardless of inset tuning, since it's
        # entirely outside the box's own coordinates.
        label_bbox = draw.textbbox((0, 0), char, font=font)
        label_height = label_bbox[3] - label_bbox[1]
        draw.text((x0, y0 - label_height - 3), char, fill=0, font=font)

    draw_corner_markers(draw, SHEET_WIDTH, SHEET_HEIGHT)

    return img
