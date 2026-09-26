"""Vectorization engine for Hatekhori glyphs.

Traces segmented raster ink patches into smooth Bézier curves using Potrace,
transforms coordinates from image space to font units (1000 UPM, baseline at y=0),
and handles conversion to TrueType quadratic curves via Cu2QuPen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
import potrace
from fontTools.pens.cu2quPen import Cu2QuPen

try:
    from template import CellInfo
    from segment import SegmentedGlyph
except ImportError:
    from .template import CellInfo
    from .segment import SegmentedGlyph


@dataclass
class VectorSegment:
    is_corner: bool
    end_point: Tuple[float, float]
    c: Optional[Tuple[float, float]] = None
    c1: Optional[Tuple[float, float]] = None
    c2: Optional[Tuple[float, float]] = None


@dataclass
class VectorContour:
    start_point: Tuple[float, float]
    segments: List[VectorSegment] = field(default_factory=list)
    is_hole: bool = False

    def to_svg_path(self, offset_x: float = 0.0, offset_y: float = 0.0, flip_y: bool = False, view_h: float = 1000.0) -> str:
        """Convert contour to an SVG path d-attribute string."""
        def tx(x: float) -> float:
            return x + offset_x

        def ty(y: float) -> float:
            if flip_y:
                return view_h - (y + offset_y)
            return y + offset_y

        sx, sy = self.start_point
        cmds = [f"M {tx(sx):.2f} {ty(sy):.2f}"]

        for seg in self.segments:
            if seg.is_corner and seg.c is not None:
                cx, cy = seg.c
                ex, ey = seg.end_point
                cmds.append(f"L {tx(cx):.2f} {ty(cy):.2f}")
                cmds.append(f"L {tx(ex):.2f} {ty(ey):.2f}")
            elif seg.c1 is not None and seg.c2 is not None:
                c1x, c1y = seg.c1
                c2x, c2y = seg.c2
                ex, ey = seg.end_point
                cmds.append(f"C {tx(c1x):.2f} {ty(c1y):.2f} {tx(c2x):.2f} {ty(c2y):.2f} {tx(ex):.2f} {ty(ey):.2f}")
            else:
                ex, ey = seg.end_point
                cmds.append(f"L {tx(ex):.2f} {ty(ey):.2f}")

        cmds.append("Z")
        return " ".join(cmds)


@dataclass
class VectorizedGlyph:
    char: str
    contours: List[VectorContour] = field(default_factory=list)
    min_x: float = 0.0
    max_x: float = 0.0
    min_y: float = 0.0
    max_y: float = 0.0
    is_empty: bool = True
    cell: Optional[CellInfo] = None
    scale: float = 1.0

    @property
    def width(self) -> float:
        return max(0.0, self.max_x - self.min_x)

    @property
    def height(self) -> float:
        return max(0.0, self.max_y - self.min_y)

    def draw_to_pen(self, pen: Any, offset_x: float = 0.0, offset_y: float = 0.0) -> None:
        """Draw glyph contours onto a FontTools pen, converting cubic curves to quadratic."""
        cu_pen = Cu2QuPen(pen, max_err=1.0)
        for contour in self.contours:
            sx = contour.start_point[0] + offset_x
            sy = contour.start_point[1] + offset_y
            cu_pen.moveTo((sx, sy))

            for seg in contour.segments:
                if seg.is_corner and seg.c is not None:
                    cx = seg.c[0] + offset_x
                    cy = seg.c[1] + offset_y
                    ex = seg.end_point[0] + offset_x
                    ey = seg.end_point[1] + offset_y
                    cu_pen.lineTo((cx, cy))
                    cu_pen.lineTo((ex, ey))
                elif seg.c1 is not None and seg.c2 is not None:
                    c1x = seg.c1[0] + offset_x
                    c1y = seg.c1[1] + offset_y
                    c2x = seg.c2[0] + offset_x
                    c2y = seg.c2[1] + offset_y
                    ex = seg.end_point[0] + offset_x
                    ey = seg.end_point[1] + offset_y
                    cu_pen.curveTo((c1x, c1y), (c2x, c2y), (ex, ey))
                else:
                    ex = seg.end_point[0] + offset_x
                    ey = seg.end_point[1] + offset_y
                    cu_pen.lineTo((ex, ey))

            cu_pen.closePath()


def vectorize_glyph(glyph: SegmentedGlyph) -> VectorizedGlyph:
    """Vectorize a single segmented glyph using Potrace curve fitting.

    Maps cell guidelines to 1000 UPM font coordinate space:
    - Baseline guideline maps to y = 0
    - Ascender guideline maps to y = 800
    - Descenders naturally map below y = 0 to negative values (e.g. -200)
    """
    if glyph.is_empty or glyph.ink_patch is None or glyph.patch_w <= 0 or glyph.patch_h <= 0:
        return VectorizedGlyph(char=glyph.char, is_empty=True, cell=glyph.cell)

    # Typographic ascender distance in 1000 UPM font space is 800 units
    ascender_dist_px = max(10.0, float(glyph.cell.baseline_y - glyph.cell.ascender_y))
    scale = 800.0 / ascender_dist_px

    # In Potrace, 0 represents foreground when background is 1
    # ink_patch has 255 for ink, 0 for background
    bmp = potrace.Bitmap(glyph.ink_patch == 0)
    path = bmp.trace(
        turdsize=3,
        turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY,
        alphamax=1.0,
        opticurve=True,
        opttolerance=0.2,
    )

    h, w = glyph.ink_patch.shape
    contours: List[VectorContour] = []
    all_x: List[float] = []
    all_y: List[float] = []

    for curve in path.curves:
        # Check if curve is the image border bounding box
        curve_pts = [curve.start_point] + [
            seg.end_point if not seg.is_corner else seg.end_point
            for seg in curve.segments
        ]
        xs = [p.x for p in curve_pts]
        ys = [p.y for p in curve_pts]
        min_px, max_px = min(xs), max(xs)
        min_py, max_py = min(ys), max(ys)

        if min_px <= 0.5 and max_px >= w - 0.5 and min_py <= 0.5 and max_py >= h - 0.5:
            continue

        # Skip tiny noise specs
        area = (max_px - min_px) * (max_py - min_py)
        if area < 6.0:
            continue

        def to_font_coords(px: float, py: float) -> Tuple[float, float]:
            # Absolute position on rectified sheet
            abs_x = glyph.patch_x0 + px
            abs_y = glyph.patch_y0 + py
            # Font X: relative to glyph patch left edge
            fx = px * scale
            # Font Y: baseline guideline is y = 0, y increases upward
            fy = (glyph.cell.baseline_y - abs_y) * scale
            return fx, fy

        start_pt = to_font_coords(curve.start_point.x, curve.start_point.y)
        all_x.append(start_pt[0])
        all_y.append(start_pt[1])

        segments: List[VectorSegment] = []
        for seg in curve.segments:
            end_pt = to_font_coords(seg.end_point.x, seg.end_point.y)
            all_x.append(end_pt[0])
            all_y.append(end_pt[1])

            if seg.is_corner:
                c_pt = to_font_coords(seg.c.x, seg.c.y)
                all_x.append(c_pt[0])
                all_y.append(c_pt[1])
                segments.append(VectorSegment(is_corner=True, end_point=end_pt, c=c_pt))
            else:
                c1_pt = to_font_coords(seg.c1.x, seg.c1.y)
                c2_pt = to_font_coords(seg.c2.x, seg.c2.y)
                all_x.extend([c1_pt[0], c2_pt[0]])
                all_y.extend([c1_pt[1], c2_pt[1]])
                segments.append(VectorSegment(is_corner=False, end_point=end_pt, c1=c1_pt, c2=c2_pt))

        contours.append(VectorContour(start_point=start_pt, segments=segments))

    if not contours or not all_x:
        return VectorizedGlyph(char=glyph.char, is_empty=True, cell=glyph.cell, scale=scale)

    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    # Normalize contours so ink left edge starts at x = 0
    normalized_contours: List[VectorContour] = []
    for contour in contours:
        sx = contour.start_point[0] - min_x
        sy = contour.start_point[1]
        norm_segments: List[VectorSegment] = []
        for seg in contour.segments:
            ex = seg.end_point[0] - min_x
            ey = seg.end_point[1]
            if seg.is_corner and seg.c is not None:
                cx = seg.c[0] - min_x
                cy = seg.c[1]
                norm_segments.append(VectorSegment(is_corner=True, end_point=(ex, ey), c=(cx, cy)))
            elif seg.c1 is not None and seg.c2 is not None:
                c1x = seg.c1[0] - min_x
                c1y = seg.c1[1]
                c2x = seg.c2[0] - min_x
                c2y = seg.c2[1]
                norm_segments.append(VectorSegment(is_corner=False, end_point=(ex, ey), c1=(c1x, c1y), c2=(c2x, c2y)))
            else:
                norm_segments.append(VectorSegment(is_corner=False, end_point=(ex, ey)))
        normalized_contours.append(VectorContour(start_point=(sx, sy), segments=norm_segments))

    return VectorizedGlyph(
        char=glyph.char,
        contours=normalized_contours,
        min_x=0.0,
        max_x=max_x - min_x,
        min_y=min_y,
        max_y=max_y,
        is_empty=False,
        cell=glyph.cell,
        scale=scale,
    )


def vectorize_all_glyphs(segmented: Dict[str, SegmentedGlyph]) -> Dict[str, VectorizedGlyph]:
    """Vectorize a full collection of segmented glyphs."""
    vectorized: Dict[str, VectorizedGlyph] = {}
    for char, glyph in segmented.items():
        vectorized[char] = vectorize_glyph(glyph)
    return vectorized
