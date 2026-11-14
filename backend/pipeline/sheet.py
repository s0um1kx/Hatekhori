"""Generates the printable guideline sheet for Bengali handwriting font capture.

Phase 2 (The Indic Extension):
- 10 rows x 6 columns (60 glyphs) on standard A4 paper.
- 11 Vowels (স্বরবর্ণ): অ to ঔ
- 39 Consonants (ব্যঞ্জনবর্ণ): ক to ঁ
- 10 Matras (কারচিহ্ন): ◌া to ◌ৌ
"""

import os
from PIL import Image, ImageDraw, ImageFont

from pipeline.segment import BENGALI_MATRAS, char_grid, compute_grid_boxes

# A4 at 150 DPI.
SHEET_WIDTH = 1240
SHEET_HEIGHT = 1754

# Four solid black squares, one per corner, sitting inside the sheet's
# outer margin.
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


def orientation_bar_box(width: int, height: int) -> tuple:
    """A bar across the top margin, between the two top corner squares."""
    return (100, 36, width - 100, 46)


def draw_orientation_bar(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    draw.rectangle(orientation_bar_box(width, height), fill=0)


def get_indic_font(size: int = 20, script: str = "bn") -> ImageFont.ImageFont:
    """Find a TrueType font capable of rendering Bengali, Hindi, or Latin characters."""
    font_candidates = [
        os.path.join(os.path.dirname(__file__), "fonts", "nirmala.ttf"),
        os.path.join(os.path.dirname(__file__), "nirmala.ttf"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "hatekhori-bengali.otf") if script == "bn" else None,
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "hatekhori-hindi.otf") if script == "hi" else None,
    ]
    windir = os.environ.get("WINDIR", "C:\\Windows")
    font_candidates.extend([
        os.path.join(windir, "Fonts", "Nirmala.ttc"),
        os.path.join(windir, "Fonts", "NirmalaB.ttc"),
        "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/deva/lohit_hi.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    ])
    for path in font_candidates:
        if path and os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default(size=size)


get_bengali_font = get_indic_font


def generate_guideline_sheet(script: str = "bn") -> Image.Image:
    """Render the printable guideline sheet for Bengali (60 glyphs), Hindi (60 glyphs), or English (90 glyphs)."""
    img = Image.new("L", (SHEET_WIDTH, SHEET_HEIGHT), color=255)
    draw = ImageDraw.Draw(img)
    s = script.lower()

    font = get_indic_font(size=20, script=s)
    boxes = compute_grid_boxes(SHEET_WIDTH, SHEET_HEIGHT, chars=char_grid(script=s))

    from pipeline.segment import BENGALI_MATRAS, HINDI_MATRAS
    if s == "bn":
        modifiers = set(BENGALI_MATRAS)
    elif s == "hi":
        modifiers = set(HINDI_MATRAS + ["ं", "ः", "ँ", "्"])
    else:
        modifiers = set()

    for entry in boxes:
        x0, y0, x1, y1 = entry["box"]
        char = entry["char"]
        # Draw clean crisp cell rectangle
        draw.rectangle([x0, y0, x1, y1], outline=0, width=1)

        # Format label with dotted circle for combining vowel signs/matras
        label = f"\u25CC{char}" if char in modifiers else char
        bb = draw.textbbox((0, 0), label, font=font)

        # Position label cleanly 4px above cell top line with 4px left margin
        # (bb[3] gives the bottom-most extent of ink, ensuring zero overlap with cell boundary)
        text_y = int((y0 - 4) - bb[3])
        text_x = int((x0 + 4) - bb[0])
        draw.text((text_x, text_y), label, fill=0, font=font)

    draw_corner_markers(draw, SHEET_WIDTH, SHEET_HEIGHT)
    draw_orientation_bar(draw, SHEET_WIDTH, SHEET_HEIGHT)

    return img
