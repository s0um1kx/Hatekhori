"""Typography metrics, baseline alignment, and optical kerning engine.

Calculates Left Side Bearings (LSB), Right Side Bearings (RSB), advance widths,
and generates optical kerning tables to eliminate baseline bounce and awkward spacing gaps.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List
import numpy as np

try:
    from vectorize import VectorizedGlyph
except ImportError:
    from .vectorize import VectorizedGlyph


@dataclass
class GlyphMetrics:
    char: str
    lsb: int
    rsb: int
    width: int
    advance_width: int
    min_y: int
    max_y: int
    is_empty: bool


# Canonical kerning pairs that frequently create visual gaps
COMMON_KERNING_PAIRS: Dict[Tuple[str, str], int] = {
    # Uppercase + Uppercase
    ("A", "V"): -70,
    ("A", "W"): -60,
    ("A", "Y"): -75,
    ("A", "T"): -60,
    ("L", "T"): -80,
    ("L", "V"): -75,
    ("L", "W"): -65,
    ("L", "Y"): -80,
    ("P", "A"): -60,
    ("T", "A"): -70,
    ("T", "O"): -45,
    ("V", "A"): -70,
    ("V", "O"): -45,
    ("W", "A"): -60,
    ("W", "O"): -40,
    ("Y", "A"): -75,
    ("Y", "O"): -50,
    # Uppercase + Lowercase
    ("T", "a"): -60,
    ("T", "e"): -60,
    ("T", "o"): -60,
    ("T", "r"): -50,
    ("T", "u"): -50,
    ("T", "w"): -55,
    ("T", "y"): -60,
    ("V", "a"): -55,
    ("V", "e"): -55,
    ("V", "o"): -55,
    ("W", "a"): -50,
    ("W", "e"): -50,
    ("W", "o"): -50,
    ("Y", "a"): -65,
    ("Y", "e"): -65,
    ("Y", "o"): -65,
    ("F", "a"): -40,
    ("F", "e"): -40,
    ("F", "o"): -40,
    ("P", "a"): -35,
    ("P", "e"): -35,
    ("P", "o"): -35,
    # Lowercase + Lowercase
    ("r", "a"): -20,
    ("r", "e"): -20,
    ("r", "o"): -25,
    ("v", "a"): -25,
    ("v", "e"): -25,
    ("v", "o"): -25,
    ("w", "a"): -20,
    ("w", "e"): -20,
    ("w", "o"): -20,
    ("y", "e"): -25,
    ("y", "o"): -25,
}

# Curved/open characters that need slightly tighter side bearings
CURVED_CHARS = set("COQScoeos0869")
OPEN_CHARS = set("AVWTYvwy7?")


def calculate_glyph_metrics(glyph: VectorizedGlyph) -> GlyphMetrics:
    """Calculate optical side bearings and advance width for a vectorized glyph."""
    if glyph.is_empty:
        # Default space/empty width
        if glyph.char == " ":
            return GlyphMetrics(
                char=" ",
                lsb=0,
                rsb=0,
                width=0,
                advance_width=320,
                min_y=0,
                max_y=0,
                is_empty=True,
            )
        return GlyphMetrics(
            char=glyph.char,
            lsb=40,
            rsb=40,
            width=0,
            advance_width=300,
            min_y=0,
            max_y=0,
            is_empty=True,
        )

    w = int(round(glyph.width))
    min_y = int(round(glyph.min_y))
    max_y = int(round(glyph.max_y))

    # Determine optical side bearings
    char = glyph.char
    if char in CURVED_CHARS:
        lsb = 40
        rsb = 40
    elif char in OPEN_CHARS:
        lsb = 30
        rsb = 30
    elif char in ("i", "l", "1", "!", "|", ":", ";"):
        lsb = 55
        rsb = 55
    elif char in (".", ","):
        lsb = 30
        rsb = 40
    else:
        lsb = 50
        rsb = 50

    advance_width = lsb + w + rsb
    # Ensure minimum advance width so narrow letters breathe
    advance_width = max(240, advance_width)

    return GlyphMetrics(
        char=char,
        lsb=lsb,
        rsb=rsb,
        width=w,
        advance_width=advance_width,
        min_y=min_y,
        max_y=max_y,
        is_empty=False,
    )


def compute_metrics_table(
    vectorized_glyphs: Dict[str, VectorizedGlyph]
) -> Tuple[Dict[str, GlyphMetrics], Dict[Tuple[str, str], int]]:
    """Compute metrics for all glyphs and build the optical kerning table."""
    metrics_map: Dict[str, GlyphMetrics] = {}

    for char, vglyph in vectorized_glyphs.items():
        metrics_map[char] = calculate_glyph_metrics(vglyph)

    # Add space character if not present
    if " " not in metrics_map:
        # Calculate space width as roughly 55% of average uppercase width
        avg_w = 550
        non_empty = [m.width for m in metrics_map.values() if not m.is_empty and m.width > 0]
        if non_empty:
            avg_w = int(sum(non_empty) / len(non_empty))
        space_advance = max(260, int(avg_w * 0.55))
        metrics_map[" "] = GlyphMetrics(
            char=" ",
            lsb=0,
            rsb=0,
            width=0,
            advance_width=space_advance,
            min_y=0,
            max_y=0,
            is_empty=True,
        )

    # Filter kerning pairs to only those present in the font
    active_kerning: Dict[Tuple[str, str], int] = {}
    for (first, second), kern_val in COMMON_KERNING_PAIRS.items():
        if first in metrics_map and second in metrics_map:
            active_kerning[(first, second)] = kern_val

    return metrics_map, active_kerning
