"""Cell grid segmentation and glyph ink isolation.

Slices rectified sheet into individual character cells, masks out printed template labels/borders,
isolates character strokes, and extracts baseline-referenced glyph patches.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import cv2
import numpy as np

try:
    from template import CellInfo, get_grid_cells
except ImportError:
    from .template import CellInfo, get_grid_cells


@dataclass
class SegmentedGlyph:
    char: str
    cell: CellInfo
    is_empty: bool
    # Binary ink patch for the glyph (True = ink, False = background)
    ink_patch: np.ndarray
    # Offset of patch (patch_x0, patch_y0) within the rectified sheet
    patch_x0: int
    patch_y0: int
    patch_w: int
    patch_h: int
    # Distance from cell baseline to ink bottom (positive if above baseline, negative if descender)
    baseline_offset: float
    # Ink centroid relative to cell
    centroid_x: float
    centroid_y: float


def segment_cells(
    binary_ink: np.ndarray,
    cells: Optional[List[CellInfo]] = None,
) -> Dict[str, SegmentedGlyph]:
    """Segment the rectified binary ink sheet into individual character glyphs.

    Args:
        binary_ink: 2D uint8 array (255 for ink, 0 for background).
        cells: List of CellInfo definitions. Defaults to get_grid_cells().

    Returns:
        Dict mapping character string to SegmentedGlyph.
    """
    if cells is None:
        cells = get_grid_cells()

    results: Dict[str, SegmentedGlyph] = {}

    for cell in cells:
        # Crop cell region with a small inner margin to avoid outer cell borders
        pad = 8
        c_x0 = cell.x0 + pad
        c_y0 = cell.y0 + pad
        c_x1 = cell.x1 - pad
        c_y1 = cell.y1 - pad

        cell_ink = binary_ink[c_y0:c_y1, c_x0:c_x1].copy()

        # Mask out the template prompt label in the top-left of the cell (x: 0..65, y: 0..45)
        label_w = min(65, cell_ink.shape[1])
        label_h = min(45, cell_ink.shape[0])
        cell_ink[0:label_h, 0:label_w] = 0

        # Also mask out 6px border margin to remove any remnants of border lines
        cell_ink[0:4, :] = 0
        cell_ink[-4:, :] = 0
        cell_ink[:, 0:4] = 0
        cell_ink[:, -4:] = 0

        # Connected component analysis to isolate character strokes and drop noise
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            cell_ink, connectivity=8
        )

        valid_components = []
        for label_id in range(1, num_labels):
            area = stats[label_id, cv2.CC_STAT_AREA]
            # Ignore tiny dust specks (< 20 px)
            if area >= 20:
                valid_components.append(label_id)

        if not valid_components:
            # Empty cell
            dummy_patch = np.zeros((10, 10), dtype=bool)
            results[cell.char] = SegmentedGlyph(
                char=cell.char,
                cell=cell,
                is_empty=True,
                ink_patch=dummy_patch,
                patch_x0=c_x0,
                patch_y0=c_y0,
                patch_w=10,
                patch_h=10,
                baseline_offset=0.0,
                centroid_x=float(cell.width / 2),
                centroid_y=float(cell.height / 2),
            )
            continue

        # Create cleaned ink mask for this cell containing only valid components
        clean_cell_ink = np.isin(labels, valid_components).astype(np.uint8) * 255

        # Find tight bounding box of ink within the cell
        ink_coords = cv2.findNonZero(clean_cell_ink)
        if ink_coords is None:
            results[cell.char] = SegmentedGlyph(
                char=cell.char,
                cell=cell,
                is_empty=True,
                ink_patch=np.zeros((10, 10), dtype=bool),
                patch_x0=c_x0,
                patch_y0=c_y0,
                patch_w=10,
                patch_h=10,
                baseline_offset=0.0,
                centroid_x=float(cell.width / 2),
                centroid_y=float(cell.height / 2),
            )
            continue

        rx, ry, rw, rh = cv2.boundingRect(ink_coords)

        # Extract tight patch with a 4-pixel border padding for smooth vector curve closure
        border = 4
        patch_x0 = max(0, rx - border)
        patch_y0 = max(0, ry - border)
        patch_x1 = min(clean_cell_ink.shape[1], rx + rw + border)
        patch_y1 = min(clean_cell_ink.shape[0], ry + rh + border)

        tight_patch = clean_cell_ink[patch_y0:patch_y1, patch_x0:patch_x1] > 0

        # Absolute coordinates on sheet
        abs_patch_x0 = c_x0 + patch_x0
        abs_patch_y0 = c_y0 + patch_y0
        abs_bottom_y = c_y0 + (ry + rh)

        # Baseline offset: difference between cell designated baseline and ink bottom
        # If ink bottom is above cell baseline, offset is positive
        # If ink bottom is below cell baseline (descender like 'g' or 'p'), offset is negative
        baseline_offset = float(cell.baseline_y - abs_bottom_y)

        # Centroid
        M = cv2.moments(clean_cell_ink)
        cx = float(M["m10"] / M["m00"]) if M["m00"] > 0 else float(rw / 2)
        cy = float(M["m01"] / M["m00"]) if M["m00"] > 0 else float(rh / 2)

        results[cell.char] = SegmentedGlyph(
            char=cell.char,
            cell=cell,
            is_empty=False,
            ink_patch=tight_patch,
            patch_x0=abs_patch_x0,
            patch_y0=abs_patch_y0,
            patch_w=tight_patch.shape[1],
            patch_h=tight_patch.shape[0],
            baseline_offset=baseline_offset,
            centroid_x=cx,
            centroid_y=cy,
        )

    return results
