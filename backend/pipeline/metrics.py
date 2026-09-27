"""Metrics step: baseline, x-height, side-bearings, spacing.

This part (6a) only adds ink-bounding-box detection, the building block
everything else in this file is computed from. Side-bearings come in
6b, global font metrics (baseline/x-height) in 6c's wiring.
"""

import numpy as np
from PIL import Image


def glyph_ink_bbox(img: Image.Image) -> tuple[int, int, int, int] | None:
    """Return (left, top, right, bottom) of the ink pixels in a glyph crop.

    Expects a binarized image (0 = ink, 255 = paper), as produced by
    preprocess.binarize. Returns None if the crop has no ink at all
    (e.g. an empty guideline-sheet box, or — as expected right now —
    a crop that landed on blank paper because the grid geometry isn't
    validated against a real sheet yet).
    """
    arr = np.array(img.convert("L") if img.mode != "L" else img)
    ys, xs = np.where(arr < 128)

    if len(xs) == 0:
        return None

    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def side_bearings(img: Image.Image, bbox: tuple[int, int, int, int] | None) -> dict:
    """Compute left/right spacing and advance width for a glyph crop.

    `bbox` is the ink bounding box from glyph_ink_bbox — pass None
    through for an empty crop and this returns zeroed-out spacing
    rather than raising, so a blank box doesn't break metrics for the
    rest of the sheet.
    """
    if bbox is None:
        return {
            "left_bearing": 0,
            "right_bearing": 0,
            "ink_width": 0,
            "advance_width": img.width,
        }

    left, _, right, _ = bbox
    return {
        "left_bearing": left,
        "right_bearing": img.width - right,
        "ink_width": right - left,
        "advance_width": img.width,
    }


def compute_global_metrics(per_glyph: dict) -> dict:
    """Derive baseline/x-height/cap-height from specific reference glyphs.

    `per_glyph` is {char: {"bbox": ink_bbox_or_None, "crop_height": int}}.

    Baseline is assumed to sit at the bottom of each glyph's own box —
    a simplifying assumption, since there's no real printed guideline
    sheet yet with actual baseline rules to measure against (M3 is
    still unbuilt; see PRD.md §11 open questions). x-height and
    cap-height are measured off 'x' and 'H' specifically, so if either
    of those boxes came out blank (very likely right now, since the
    grid geometry isn't validated against a real photo), those values
    come back None rather than a wrong number.
    """

    def distance_from_baseline(char: str):
        entry = per_glyph.get(char)
        if not entry or entry["bbox"] is None:
            return None
        ink_top = entry["bbox"][1]
        return entry["crop_height"] - ink_top

    return {
        "baseline_convention": "bottom of each glyph's own box",
        "x_height": distance_from_baseline("x"),
        "cap_height": distance_from_baseline("H"),
    }
