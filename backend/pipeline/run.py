"""Photo of a filled sheet -> font file. The whole pipeline, in memory; the API and the CLI both call this."""

from pathlib import Path

from PIL import Image

from pipeline.compile import build_font
from pipeline.metrics import glyph_ink_bbox
from pipeline.segment import char_grid, crop_glyphs
from pipeline.validate import check_sheet_is_filled, find_corner_markers, perspective_correct
from pipeline.vectorize import trace_glyph


def make_font(photo: Path, out: Path) -> dict:
    """Write the font to `out`. Raises validate.BadSheetShape if the photo isn't a filled Hatekhori sheet."""
    with Image.open(photo) as img:
        sheet = perspective_correct(img, find_corner_markers(img))
    sheet = sheet.convert("L").point(lambda p: 0 if p < 128 else 255)  # pure black ink on white paper

    glyphs = crop_glyphs(sheet)
    check_sheet_is_filled(glyphs)

    entries, blank = {}, []
    for char in char_grid():
        glyph = glyphs[char]
        if glyph_ink_bbox(glyph) is None:
            blank.append(char)  # never written: leave it out instead of shipping an empty glyph
            continue
        entries[char] = {"path": trace_glyph(glyph), "crop_height": glyph.height, "advance_width": glyph.width}

    build_font(entries, units_per_em=1000, family_name="Hatekhori Kill-Test").save(str(out))
    return {"glyph_count": len(entries), "skipped_blank": blank}
