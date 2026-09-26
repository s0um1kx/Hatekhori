"""TrueType font compilation engine for Hatekhori.

Compiles vectorized glyph outlines, typography metrics, and kerning tables into
fully standard, installable TrueType (.ttf) font files using FontTools.
"""

from __future__ import annotations

import datetime
from typing import Dict, Tuple, Optional, List
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import newTable
from fontTools.ttLib.tables._k_e_r_n import KernTable_format_0

try:
    from vectorize import VectorizedGlyph
    from metrics import GlyphMetrics
except ImportError:
    from .vectorize import VectorizedGlyph
    from .metrics import GlyphMetrics


def char_to_glyph_name(char: str) -> str:
    """Map character to standard OpenType / TrueType glyph name."""
    if char == " ":
        return "space"
    if char == "?":
        return "question"
    if char == "!":
        return "exclam"

    digit_names = {
        "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
        "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
    }
    if char in digit_names:
        return digit_names[char]

    return char


def build_notdef_glyph() -> any:
    """Build a standard .notdef glyph (rectangular frame)."""
    pen = TTGlyphPen(None)
    # Outer rectangle
    pen.moveTo((80, 0))
    pen.lineTo((80, 700))
    pen.lineTo((420, 700))
    pen.lineTo((420, 0))
    pen.closePath()
    # Inner cutout (reverse winding)
    pen.moveTo((140, 60))
    pen.lineTo((360, 60))
    pen.lineTo((360, 640))
    pen.lineTo((140, 640))
    pen.closePath()
    return pen.glyph()


def compile_font(
    vectorized_glyphs: Dict[str, VectorizedGlyph],
    metrics_map: Dict[str, GlyphMetrics],
    kerning_pairs: Optional[Dict[Tuple[str, str], int]] = None,
    output_path: str = "hatekhori_output.ttf",
    family_name: str = "Hatekhori Validation",
    style_name: str = "Regular",
    provenance_note: str = "Hatekhori Atelier Milestone 1 Internal Validation",
) -> str:
    """Compile vectorized glyphs and metrics into a complete TrueType font file (.ttf).

    Args:
        vectorized_glyphs: Map of character -> VectorizedGlyph
        metrics_map: Map of character -> GlyphMetrics
        kerning_pairs: Map of (char1, char2) -> kerning offset
        output_path: Target .ttf filepath
        family_name: Font family name
        style_name: Subfamily / style name
        provenance_note: Provenance string for metadata

    Returns:
        output_path on successful compilation
    """
    builder = FontBuilder(unitsPerEm=1000, isTTF=True)

    # 1. Glyph ordering
    glyph_order = [".notdef", "space"]
    char_list = sorted([c for c in vectorized_glyphs.keys() if c != " "])
    for c in char_list:
        gname = char_to_glyph_name(c)
        if gname not in glyph_order:
            glyph_order.append(gname)

    builder.setupGlyphOrder(glyph_order)

    # 2. Character mapping (Unicode cmap)
    cmap: Dict[int, str] = {ord(" "): "space"}
    for c in char_list:
        cmap[ord(c)] = char_to_glyph_name(c)
    builder.setupCharacterMap(cmap)

    # 3. Glyph outlines (glyf / loca)
    glyphs = {}
    glyphs[".notdef"] = build_notdef_glyph()

    # Empty space glyph
    space_pen = TTGlyphPen(None)
    glyphs["space"] = space_pen.glyph()

    for c in char_list:
        gname = char_to_glyph_name(c)
        vglyph = vectorized_glyphs[c]
        metric = metrics_map.get(c)
        pen = TTGlyphPen(None)

        if not vglyph.is_empty and vglyph.contours:
            lsb_offset = metric.lsb if metric else 50
            vglyph.draw_to_pen(pen, offset_x=lsb_offset, offset_y=0.0)
            glyphs[gname] = pen.glyph()
        else:
            glyphs[gname] = pen.glyph()

    builder.setupGlyf(glyphs)

    # 4. Horizontal Metrics (hmtx)
    h_metrics = {
        ".notdef": (500, 80),
        "space": (metrics_map[" "].advance_width if " " in metrics_map else 320, 0),
    }

    for c in char_list:
        gname = char_to_glyph_name(c)
        metric = metrics_map.get(c)
        if metric:
            h_metrics[gname] = (metric.advance_width, metric.lsb)
        else:
            h_metrics[gname] = (500, 50)

    builder.setupHorizontalMetrics(h_metrics)

    # 5. Horizontal Header (hhea)
    builder.setupHorizontalHeader(
        ascent=800,
        descent=-200,
        lineGap=200,
    )

    # 6. OS/2 Table (Standard typography parameters)
    builder.setupOS2(
        sTypoAscender=800,
        sTypoDescender=-200,
        sTypoLineGap=200,
        usWinAscent=800,
        usWinDescent=200,
        sxHeight=500,
        sCapHeight=700,
        weightClass=400,
        widthClass=5,
    )

    # 7. Name Table (Metadata & Provenance per AGENTS.md §4)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d")
    postscript_name = f"{family_name.replace(' ', '')}-{style_name}"
    name_strings = {
        "familyName": family_name,
        "styleName": style_name,
        "fullName": f"{family_name} {style_name}",
        "psName": postscript_name,
        "version": f"Version 0.100; {now_str}",
        "uniqueFontIdentifier": f"{postscript_name}:{now_str}",
        "manufacturer": "Hatekhori",
        "description": provenance_note,
    }
    builder.setupNameTable(name_strings)

    # 8. PostScript table (post)
    builder.setupPost()

    # 9. Kerning table (kern)
    if kerning_pairs:
        # Convert character pairs to glyph name pairs
        kern_dict = {}
        for (c1, c2), val in kerning_pairs.items():
            g1 = char_to_glyph_name(c1)
            g2 = char_to_glyph_name(c2)
            if g1 in glyph_order and g2 in glyph_order:
                kern_dict[(g1, g2)] = val

        if kern_dict:
            kern_table = newTable("kern")
            kern_table.version = 0
            subtable = KernTable_format_0()
            subtable.version = 0
            subtable.coverage = 1
            subtable.kernTable = kern_dict
            kern_table.kernTables = [subtable]
            builder.font["kern"] = kern_table

    # Save font
    builder.save(output_path)
    return output_path
