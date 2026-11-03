"""Compile step: vectors + metrics -> a real OpenType (.otf) or TrueType (.ttf) font file.

Supports both CFF outlines (.otf) and TrueType quadratic curves (.ttf),
computing proportional advance widths and optical metrics from ink bounding boxes.
"""

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen


def draw_potrace_path(
    pen,
    trace_path,
    baseline_y: float,
    min_x: float = 0.0,
    lsb: float = 0.0,
    scale: float = 1.0,
) -> None:
    """Replay a potrace Path's curves onto a fontTools pen.

    - Horizontal: (point.x - min_x) * scale + lsb (proportional optical placement).
    - Vertical: (baseline_y - point.y) * scale (standard font baseline alignment).
    """

    def transform_pt(point):
        x = (point.x - min_x) * scale + lsb
        y = (baseline_y - point.y) * scale
        return (x, y)

    for curve in trace_path:
        pen.moveTo(transform_pt(curve.start_point))
        for segment in curve.segments:
            if segment.is_corner:
                pen.lineTo(transform_pt(segment.c))
                pen.lineTo(transform_pt(segment.end_point))
            else:
                pen.curveTo(
                    transform_pt(segment.c1),
                    transform_pt(segment.c2),
                    transform_pt(segment.end_point),
                )
        pen.closePath()


def build_font(
    glyph_entries: dict,
    units_per_em: int = 1000,
    is_ttf: bool = False,
    family_name: str = "Hatekhori",
):
    """Assemble a real font from traced glyphs with proportional optical metrics.

    When `is_ttf=True`, outputs quadratic TrueType outlines (.ttf).
    When `is_ttf=False` (default), outputs cubic CFF outlines (.otf).
    """
    BOX_TO_EM_FRACTION = 0.85
    ascent = 800
    descent = -200

    glyph_order = [".notdef"]
    cmap = {}
    cff_charstrings = {}
    tt_glyphs = {}
    advance_widths = {}
    lsb_values = {}

    for i, (char, data) in enumerate(glyph_entries.items()):
        glyph_name = f"g{i:03d}"
        glyph_order.append(glyph_name)
        cmap[ord(char)] = glyph_name

        crop_height = data["crop_height"]
        crop_width = data.get("crop_width", crop_height)
        scale = (units_per_em * BOX_TO_EM_FRACTION) / crop_height if crop_height else 1.0
        baseline_y = crop_height * 0.78

        bbox = data.get("bbox")
        if bbox is not None:
            min_x, min_y, max_x, max_y = bbox
            ink_w = max_x - min_x
            lsb = max(30.0, min(80.0, ink_w * scale * 0.12))
            advance_width = round(ink_w * scale + 2 * lsb)
        else:
            min_x = 0.0
            lsb = 40.0
            advance_width = round(crop_width * scale * 0.5)

        lsb_values[glyph_name] = round(lsb)

        if is_ttf:
            tt_pen = TTGlyphPen(None)
            if data.get("path") is not None:
                cu_pen = Cu2QuPen(tt_pen, max_err=1.0)
                draw_potrace_path(cu_pen, data["path"], baseline_y=baseline_y, min_x=min_x, lsb=lsb, scale=scale)
            tt_glyphs[glyph_name] = tt_pen.glyph()
        else:
            t2_pen = T2CharStringPen(advance_width, None)
            if data.get("path") is not None:
                draw_potrace_path(t2_pen, data["path"], baseline_y=baseline_y, min_x=min_x, lsb=lsb, scale=scale)
            cff_charstrings[glyph_name] = t2_pen.getCharString()

        advance_widths[glyph_name] = advance_width

    notdef_width = units_per_em // 2
    lsb_values[".notdef"] = 0
    if is_ttf:
        tt_glyphs[".notdef"] = TTGlyphPen(None).glyph()
    else:
        cff_charstrings[".notdef"] = T2CharStringPen(notdef_width, None).getCharString()
    advance_widths[".notdef"] = notdef_width

    space_width = units_per_em // 3
    lsb_values["space"] = 0
    glyph_order.append("space")
    cmap[ord(" ")] = "space"
    if is_ttf:
        tt_glyphs["space"] = TTGlyphPen(None).glyph()
    else:
        cff_charstrings["space"] = T2CharStringPen(space_width, None).getCharString()
    advance_widths["space"] = space_width

    fb = FontBuilder(units_per_em, isTTF=is_ttf)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)

    if is_ttf:
        fb.setupGlyf(tt_glyphs)
    else:
        fb.setupCFF(
            family_name.replace(" ", ""),
            {"FullName": family_name},
            cff_charstrings,
            {},
        )

    metrics = {name: (width, lsb_values.get(name, 0)) for name, width in advance_widths.items()}
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ascent, descent=descent)

    ps_name = family_name.replace(" ", "")
    fb.setupNameTable(
        {
            "familyName": family_name,
            "styleName": "Regular",
            "uniqueFontIdentifier": f"Hatekhori:{ps_name}:1.0",
            "fullName": family_name,
            "psName": ps_name,
            "version": "Version 1.0",
        }
    )
    fb.setupOS2(
        sTypoAscender=ascent,
        sTypoDescender=descent,
        usWinAscent=ascent,
        usWinDescent=abs(descent),
    )
    fb.setupPost()

    return fb
