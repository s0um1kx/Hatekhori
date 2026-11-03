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


def get_bengali_font(size: int = 22) -> ImageFont.ImageFont:
    """Find a system TrueType font capable of rendering Bengali characters."""
    windir = os.environ.get("WINDIR", "C:\\Windows")
    candidates = [
        os.path.join(windir, "Fonts", "Nirmala.ttc"),
        os.path.join(windir, "Fonts", "NirmalaB.ttc"),
        "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default(size=size)


def generate_guideline_sheet(script: str = "bn") -> Image.Image:
    """Render the printable guideline sheet for either Bengali (60 glyphs) or English (90 glyphs)."""
    img = Image.new("L", (SHEET_WIDTH, SHEET_HEIGHT), color=255)
    draw = ImageDraw.Draw(img)

    if script == "en":
        font = ImageFont.load_default(size=18)
        boxes = compute_grid_boxes(SHEET_WIDTH, SHEET_HEIGHT, chars=char_grid(script="en"))
        for entry in boxes:
            x0, y0, x1, y1 = entry["box"]
            char = entry["char"]
            draw.rectangle([x0, y0, x1, y1], outline=0, width=1)
            label_bbox = draw.textbbox((0, 0), char, font=font)
            label_height = label_bbox[3] - label_bbox[1]
            draw.text((x0 + 4, y0 - label_height - 3), char, fill=0, font=font)
    else:
        font = get_bengali_font(size=22)
        boxes = compute_grid_boxes(SHEET_WIDTH, SHEET_HEIGHT, chars=char_grid(script="bn"))
        for entry in boxes:
            x0, y0, x1, y1 = entry["box"]
            char = entry["char"]
            draw.rectangle([x0, y0, x1, y1], outline=0, width=1)
            label = f"\u25CC{char}" if char in BENGALI_MATRAS else char
            label_bbox = draw.textbbox((0, 0), label, font=font)
            label_height = label_bbox[3] - label_bbox[1]
            draw.text((x0 + 8, y0 - label_height - 3), label, fill=0, font=font)

    draw_corner_markers(draw, SHEET_WIDTH, SHEET_HEIGHT)
    draw_orientation_bar(draw, SHEET_WIDTH, SHEET_HEIGHT)

    return img
