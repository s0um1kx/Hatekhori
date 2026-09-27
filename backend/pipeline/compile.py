"""Compile step: vectors + metrics -> a real .otf font file.

Part 7a added draw_potrace_path. This part (7b) adds build_font, which
assembles all glyphs into an actual font object using fontTools. 7c
wires it into an endpoint.
"""

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen


def draw_potrace_path(pen, trace_path, crop_height: float) -> None:
    """Replay a potrace Path's curves onto a fontTools pen.

    Image coordinates have y increasing downward from the top; font
    coordinates have y increasing upward from the baseline. Per the
    baseline convention set in metrics.py (baseline = bottom of the
    glyph's own crop), flipping is just `crop_height - y`.
    """

    def flip(point):
        return (point.x, crop_height - point.y)

    for curve in trace_path:
        pen.moveTo(flip(curve.start_point))
        for segment in curve.segments:
            if segment.is_corner:
                pen.lineTo(flip(segment.c))
                pen.lineTo(flip(segment.end_point))
            else:
                pen.curveTo(flip(segment.c1), flip(segment.c2), flip(segment.end_point))
        pen.closePath()


def build_font(glyph_entries: dict, units_per_em: int = 1000, family_name: str = "Hatekhori Kill-Test"):
    """Assemble a real .otf font (CFF outlines) from traced glyphs.

    `glyph_entries` is {char: {"path": potrace Path or None,
    "crop_height": int, "advance_width": int}} — a char with path=None
    (no ink found in its box) still gets a real, empty glyph rather
    than being skipped, so the font remains structurally valid.

    Glyph names are systematic ("g000", "g001", ...) rather than the
    character itself, since raw characters aren't guaranteed-safe
    OpenType glyph names — the character-to-glyph mapping lives in the
    cmap instead.

    Units/coordinates are currently raw source pixels, not rescaled to
    a typographic unitsPerEm convention — fine for proving the pipeline
    produces a structurally real font, not yet tuned for correct visual
    proportions.
    """
    glyph_order = [".notdef"]
    cmap = {}
    charstrings = {}
    advance_widths = {}

    for i, (char, data) in enumerate(glyph_entries.items()):
        glyph_name = f"g{i:03d}"
        glyph_order.append(glyph_name)
        cmap[ord(char)] = glyph_name

        advance_width = data["advance_width"]
        pen = T2CharStringPen(advance_width, None)
        if data.get("path") is not None:
            draw_potrace_path(pen, data["path"], data["crop_height"])
        charstrings[glyph_name] = pen.getCharString()
        advance_widths[glyph_name] = advance_width

    notdef_width = units_per_em // 2
    notdef_pen = T2CharStringPen(notdef_width, None)
    charstrings[".notdef"] = notdef_pen.getCharString()
    advance_widths[".notdef"] = notdef_width

    fb = FontBuilder(units_per_em, isTTF=False)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupCFF(
        family_name.replace(" ", ""),
        {"FullName": family_name},
        charstrings,
        {},
    )

    metrics = {name: (width, 0) for name, width in advance_widths.items()}
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=units_per_em, descent=0)
    fb.setupNameTable({"familyName": family_name, "styleName": "Regular"})
    fb.setupOS2(
        sTypoAscender=units_per_em,
        usWinAscent=units_per_em,
        usWinDescent=0,
    )
    fb.setupPost()

    return fb
