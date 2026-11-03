"""Segment step: slice the cleaned guideline sheet into individual glyph boxes.

Phase 2 (The Indic Extension): Bengali primary alphabet (60 glyphs):
- 11 Vowels (স্বরবর্ণ): অ, আ, ই, ঈ, উ, ঊ, ঋ, এ, ঐ, ও, ঔ
- 39 Consonants (ব্যঞ্জনবর্ণ): ক to ঁ
- 10 Vowel signs/matras (কারচিহ্ন): া to ৌ
Arranged in 10 rows x 6 columns on A4 paper.
"""

from PIL import Image

GRID_ROWS = 10
GRID_COLS = 6  # 10x6 = 60 Bengali characters

# Margin around the whole grid, and gutter between boxes, as a fraction
# of image width/height.
MARGIN_FRAC = 0.05
GUTTER_FRAC = 0.01

BENGALI_VOWELS = [
    "অ", "আ", "ই", "ঈ", "উ", "ঊ", "ঋ", "এ", "ঐ", "ও", "ঔ"
]

BENGALI_CONSONANTS = [
    "ক", "খ", "গ", "ঘ", "ঙ",
    "চ", "ছ", "জ", "ঝ", "ঞ",
    "ট", "ঠ", "ড", "ঢ", "ণ",
    "ত", "থ", "দ", "ধ", "ন",
    "প", "ফ", "ব", "ভ", "ম",
    "য", "র", "ল", "শ", "ষ", "স", "হ",
    "ড়", "ঢ়", "য়", "ৎ",
    "ং", "ঃ", "ঁ"
]

BENGALI_MATRAS = [
    "া", "ি", "ী", "ু", "ূ", "ৃ", "ে", "ৈ", "ো", "ৌ"
]

BENGALI_CHARS = BENGALI_VOWELS + BENGALI_CONSONANTS + BENGALI_MATRAS


def char_grid(script: str = "bn") -> list[str]:
    """Ordered list of glyphs, reading left-to-right, top-to-bottom. Defaults to Bengali (60 glyphs)."""
    if script == "en":
        import string
        symbols = list(".,!?'\"()-:;@#$%&*+=/\\_[]{}<>")
        return list(string.ascii_uppercase + string.ascii_lowercase + string.digits) + symbols
    return list(BENGALI_CHARS)


def compute_grid_boxes(img_width: int, img_height: int, chars: list[str] | None = None) -> list[dict]:
    """Return [{char, box: (x0, y0, x1, y1)}, ...] in pixel coordinates.

    Assumes the preprocessed image is the guideline sheet cropped
    reasonably tight to its edges (deskew handles rotation, not
    cropping) — box positions are simple fractions of the full image.
    """
    if chars is None:
        chars = char_grid()

    cols = 6 if len(chars) == 60 else (9 if len(chars) == 90 else GRID_COLS)
    rows = len(chars) // cols

    usable_width = img_width * (1 - 2 * MARGIN_FRAC)
    usable_height = img_height * (1 - 2 * MARGIN_FRAC)
    margin_x = img_width * MARGIN_FRAC
    margin_y = img_height * MARGIN_FRAC

    gutter_x = img_width * GUTTER_FRAC
    gutter_y = img_height * GUTTER_FRAC

    box_width = (usable_width - gutter_x * (cols - 1)) / cols
    box_height = (usable_height - gutter_y * (rows - 1)) / rows

    boxes = []
    for i, char in enumerate(chars):
        row = i // cols
        col = i % cols

        x0 = margin_x + col * (box_width + gutter_x)
        y0 = margin_y + row * (box_height + gutter_y)
        x1 = x0 + box_width
        y1 = y0 + box_height

        boxes.append({"char": char, "box": (x0, y0, x1, y1)})

    return boxes


# How much to shrink each box, on every side, before actually cropping
# a glyph out of it — as a fraction of the box's own width/height.
CROP_INSET_FRACTION = 0.06


def crop_glyphs(img: Image.Image, chars: list[str] | None = None) -> dict[str, Image.Image]:
    """Slice each glyph box out of the preprocessed sheet image.

    Returns a dict keyed by character, e.g. {"অ": <Image>, "ক": <Image>, ...}.
    """
    boxes = compute_grid_boxes(img.width, img.height, chars=chars)
    result = {}
    for entry in boxes:
        x0, y0, x1, y1 = entry["box"]
        inset_x = (x1 - x0) * CROP_INSET_FRACTION
        inset_y = (y1 - y0) * CROP_INSET_FRACTION
        result[entry["char"]] = img.crop((x0 + inset_x, y0 + inset_y, x1 - inset_x, y1 - inset_y))
    return result
