"""Photo of a filled sheet -> font file. The whole pipeline, in memory; the API and the CLI both call this."""

from pathlib import Path
import time

from PIL import Image

from pipeline.cleanup import binarize_sheet
from pipeline.compile import build_font
from pipeline.metrics import glyph_ink_bbox
from pipeline.segment import char_grid, crop_glyphs
from pipeline.validate import check_sheet_is_filled, straighten
from pipeline.vectorize import trace_glyph


def make_font(photo: Path, out: Path, script: str = "bn") -> dict:
    """Write the font to `out` (.otf or .ttf). Raises validate.BadSheetShape if the photo isn't a filled Hatekhori sheet."""
    with Image.open(photo) as img:
        sheet, warnings = straighten(img)
    sheet = binarize_sheet(sheet)

    chars = char_grid(script=script)
    glyphs = crop_glyphs(sheet, chars=chars)
    check_sheet_is_filled(glyphs)

    entries, blank = {}, []
    for char in chars:
        glyph = glyphs[char]
        bbox = glyph_ink_bbox(glyph)
        if bbox is None:
            blank.append(char)  # never written: leave it out instead of shipping an empty glyph
            continue
        entries[char] = {
            "path": trace_glyph(glyph),
            "crop_height": glyph.height,
            "crop_width": glyph.width,
            "bbox": bbox,
        }

    s = script.lower()
    if s == "bn":
        family_name = "Hatekhori Bangla"
    elif s == "hi":
        family_name = "Hatekhori Hindi"
    else:
        family_name = "Hatekhori"
    is_ttf = out.suffix.lower() == ".ttf"
    tmp_out = out.with_name(f"{out.name}.{time.time_ns()}.tmp")
    try:
        build_font(entries, units_per_em=1000, is_ttf=is_ttf, family_name=family_name).save(str(tmp_out))
        tmp_out.replace(out)
    finally:
        tmp_out.unlink(missing_ok=True)
    return {"glyph_count": len(entries), "skipped_blank": blank, "warnings": warnings}
