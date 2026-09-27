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


def generate_guideline_sheet() -> Image.Image:
    """Render the printable sheet: one box per glyph, each labeled with
    the character to write inside it.
    """
    img = Image.new("L", (SHEET_WIDTH, SHEET_HEIGHT), color=255)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    for entry in compute_grid_boxes(SHEET_WIDTH, SHEET_HEIGHT):
        x0, y0, x1, y1 = entry["box"]
        draw.rectangle([x0, y0, x1, y1], outline=0, width=1)
        # Small guide label in the box's top-left corner, not meant to
        # be written over — the person writes their own version of the
        # character in the rest of the box.
        draw.text((x0 + 4, y0 + 2), entry["char"], fill=0, font=font)

    return img
