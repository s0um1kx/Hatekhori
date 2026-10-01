"""Segment step: slice the cleaned guideline sheet into individual glyph
boxes.

English M1 glyph set: A-Z, a-z, 0-9, plus common punctuation/symbols
(90 glyphs total) — per PRD.md's own "~60-90 glyphs" budget for English
internal validation (this is never shown publicly).
"""

import string

from PIL import Image

GRID_ROWS = 10
GRID_COLS = 9  # 9x10 = 90, exactly matching the glyph count below, no empty cells

# Margin around the whole grid, and gutter between boxes, as a fraction
# of image width/height. Placeholders until a real printed sheet exists
# to measure against (there's no physical guideline-sheet template yet
# — that's part of the still-unbuilt M3 capture UI).
MARGIN_FRAC = 0.05
GUTTER_FRAC = 0.01

# Common punctuation/symbols, added to the original A-Z/a-z/0-9 set.
SYMBOLS = list(".,!?'\"()-:;@#$%&*+=/\\_[]{}<>")

# Standard (Adobe Glyph List-style) names for characters that aren't
# safe as-is — several of these are characters Windows forbids in
# filenames (/ \ : * ? " < >), and all of them need a real name for the
# font's internal glyph table anyway, so one mapping serves both uses.
_GLYPH_NAME_OVERRIDES = {
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
    "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
    ".": "period", ",": "comma", "!": "exclam", "?": "question",
    "'": "quotesingle", '"': "quotedbl", "(": "parenleft", ")": "parenright",
    "-": "hyphen", ":": "colon", ";": "semicolon", "@": "at",
    "#": "numbersign", "$": "dollar", "%": "percent", "&": "ampersand",
    "*": "asterisk", "+": "plus", "=": "equal", "/": "slash",
    "\\": "backslash", "_": "underscore", "[": "bracketleft",
    "]": "bracketright", "{": "braceleft", "}": "braceright",
    "<": "less", ">": "greater",
}


def glyph_name_for(char: str) -> str:
    """Filesystem- and font-safe name for a glyph (e.g. '/' -> 'slash').

    Plain letters are already safe and returned as-is; everything else
    uses the standard glyph-name mapping above.
    """
    return _GLYPH_NAME_OVERRIDES.get(char, char)


def char_grid() -> list[str]:
    """Ordered list of the 90 glyphs, reading left-to-right, top-to-bottom."""
    return list(string.ascii_uppercase + string.ascii_lowercase + string.digits) + SYMBOLS


def compute_grid_boxes(img_width: int, img_height: int) -> list[dict]:
    """Return [{char, box: (x0, y0, x1, y1)}, ...] in pixel coordinates.

    Assumes the preprocessed image is the guideline sheet cropped
    reasonably tight to its edges (deskew handles rotation, not
    cropping) — box positions are simple fractions of the full image.
    """
    chars = char_grid()

    usable_width = img_width * (1 - 2 * MARGIN_FRAC)
    usable_height = img_height * (1 - 2 * MARGIN_FRAC)
    margin_x = img_width * MARGIN_FRAC
    margin_y = img_height * MARGIN_FRAC

    gutter_x = img_width * GUTTER_FRAC
    gutter_y = img_height * GUTTER_FRAC

    box_width = (usable_width - gutter_x * (GRID_COLS - 1)) / GRID_COLS
    box_height = (usable_height - gutter_y * (GRID_ROWS - 1)) / GRID_ROWS

    boxes = []
    for i, char in enumerate(chars):
        row = i // GRID_COLS
        col = i % GRID_COLS

        x0 = margin_x + col * (box_width + gutter_x)
        y0 = margin_y + row * (box_height + gutter_y)
        x1 = x0 + box_width
        y1 = y0 + box_height

        boxes.append({"char": char, "box": (x0, y0, x1, y1)})

    return boxes


def crop_glyphs(img: Image.Image) -> dict[str, Image.Image]:
    """Slice each glyph box out of the preprocessed sheet image.

    Returns a dict keyed by character, e.g. {"A": <Image>, "b": <Image>, ...}.
    """
    boxes = compute_grid_boxes(img.width, img.height)
    return {entry["char"]: img.crop(entry["box"]) for entry in boxes}
