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
        draw.rectangle([x0, y0, x1, y1], outline=0, width=1)
        # Small guide label in the box's top-left corner, not meant to
        # be written over — the person writes their own version of the
        # character in the rest of the box.
        draw.text((x0 + 4, y0 + 2), entry["char"], fill=0, font=font)

    draw_corner_markers(draw, SHEET_WIDTH, SHEET_HEIGHT)

    return img


def generate_synthetic_filled_sheet() -> Image.Image:
    """Render the sheet with each box already 'filled in' using a system
    font, standing in for handwriting.

    This is NOT the real kill-test — PRD.md §9 requires real, varied
    handwriting photos. It exists to sanity-check the pipeline (grid
    alignment, vectorization, font compilation) end-to-end without a
    printer, before spending a real printed sheet on it.
    """
    img = Image.new("L", (SHEET_WIDTH, SHEET_HEIGHT), color=255)
    draw = ImageDraw.Draw(img)

    # Font size is a fraction of the actual box height, not a hardcoded
    # value — a fixed size would silently stop filling the box properly
    # whenever the grid (and therefore box size) changes, making this
    # self-test quietly unrepresentative of real ink coverage.
    sample_box = compute_grid_boxes(SHEET_WIDTH, SHEET_HEIGHT)[0]["box"]
    box_height = sample_box[3] - sample_box[1]
    font_size = int(box_height * 0.6)

    try:
        glyph_font = ImageFont.truetype("arial.ttf", size=font_size)
    except OSError:
        # No arial.ttf on this machine — fall back to the built-in
        # bitmap font. It's small, but the point here is a structural
        # test, not a beautiful synthetic glyph.
        glyph_font = ImageFont.load_default()

    for entry in compute_grid_boxes(SHEET_WIDTH, SHEET_HEIGHT):
        x0, y0, x1, y1 = entry["box"]
        char = entry["char"]

        bbox = draw.textbbox((0, 0), char, font=glyph_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        box_width = x1 - x0
        box_height = y1 - y0

        text_x = x0 + (box_width - text_width) / 2 - bbox[0]
        text_y = y0 + (box_height - text_height) / 2 - bbox[1]
        draw.text((text_x, text_y), char, fill=0, font=glyph_font)

    draw_corner_markers(draw, SHEET_WIDTH, SHEET_HEIGHT)

    return img
