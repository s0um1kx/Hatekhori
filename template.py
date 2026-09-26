"""Guideline sheet layout specification and generator.

Defines the standard A4 English handwriting capture sheet (A-Z, a-z, 0-9, ?, !)
with high-contrast 4-corner fiducial registration markers for homography rectification.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
import numpy as np
from PIL import Image, ImageDraw, ImageFont


# Canonical rectified sheet dimensions (A4 @ 300 DPI)
SHEET_WIDTH = 2480
SHEET_HEIGHT = 3508

# Margin and grid dimensions
MARGIN_X = 140
MARGIN_Y = 180
FIDUCIAL_SIZE = 100  # Outer square size in pixels
FIDUCIAL_INSET = 40  # Distance from page edge

# 8 columns x 8 rows = 64 cells
GRID_COLS = 8
GRID_ROWS = 8

# Cell character mapping (row, col) -> character
CHAR_MAP: List[str] = [
    # Row 0: A - H
    "A", "B", "C", "D", "E", "F", "G", "H",
    # Row 1: I - P
    "I", "J", "K", "L", "M", "N", "O", "P",
    # Row 2: Q - X
    "Q", "R", "S", "T", "U", "V", "W", "X",
    # Row 3: Y, Z, a - f
    "Y", "Z", "a", "b", "c", "d", "e", "f",
    # Row 4: g - n
    "g", "h", "i", "j", "k", "l", "m", "n",
    # Row 5: o - v
    "o", "p", "q", "r", "s", "t", "u", "v",
    # Row 6: w - z, 0 - 3
    "w", "x", "y", "z", "0", "1", "2", "3",
    # Row 7: 4 - 9, ?, !
    "4", "5", "6", "7", "8", "9", "?", "!",
]


@dataclass
class CellInfo:
    char: str
    row: int
    col: int
    x0: int
    y0: int
    x1: int
    y1: int
    baseline_y: int
    x_height_y: int
    cap_height_y: int
    ascender_y: int
    descender_y: int

    @property
    def width(self) -> int:
        return self.x1 - self.x0

    @property
    def height(self) -> int:
        return self.y1 - self.y0


def get_grid_cells() -> List[CellInfo]:
    """Calculate bounding boxes and guideline positions for all 64 cells."""
    grid_x0 = MARGIN_X + 20
    grid_y0 = MARGIN_Y + 120
    grid_x1 = SHEET_WIDTH - MARGIN_X - 20
    grid_y1 = SHEET_HEIGHT - MARGIN_Y - 40

    total_w = grid_x1 - grid_x0
    total_h = grid_y1 - grid_y0

    cell_w = total_w // GRID_COLS
    cell_h = total_h // GRID_ROWS

    cells: List[CellInfo] = []
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            idx = row * GRID_COLS + col
            char = CHAR_MAP[idx]

            c_x0 = grid_x0 + col * cell_w
            c_y0 = grid_y0 + row * cell_h
            c_x1 = c_x0 + cell_w
            c_y1 = c_y0 + cell_h

            # Guideline ratios within each cell:
            # Baseline: 68% down the cell
            # x-height: 48% down the cell
            # Cap-height: 32% down the cell
            # Ascender: 26% down the cell
            # Descender: 82% down the cell
            baseline_y = c_y0 + int(cell_h * 0.68)
            x_height_y = c_y0 + int(cell_h * 0.48)
            cap_height_y = c_y0 + int(cell_h * 0.32)
            ascender_y = c_y0 + int(cell_h * 0.26)
            descender_y = c_y0 + int(cell_h * 0.82)

            cells.append(
                CellInfo(
                    char=char,
                    row=row,
                    col=col,
                    x0=c_x0,
                    y0=c_y0,
                    x1=c_x1,
                    y1=c_y1,
                    baseline_y=baseline_y,
                    x_height_y=x_height_y,
                    cap_height_y=cap_height_y,
                    ascender_y=ascender_y,
                    descender_y=descender_y,
                )
            )
    return cells


def get_fiducial_positions() -> List[Tuple[float, float]]:
    """Return the center coordinates of the 4 corner registration fiducials in canonical image space.

    Order: Top-Left, Top-Right, Bottom-Right, Bottom-Left
    """
    f_size = FIDUCIAL_SIZE
    inset = FIDUCIAL_INSET

    tl = (float(inset + f_size / 2), float(inset + f_size / 2))
    tr = (float(SHEET_WIDTH - inset - f_size / 2), float(inset + f_size / 2))
    br = (float(SHEET_WIDTH - inset - f_size / 2), float(SHEET_HEIGHT - inset - f_size / 2))
    bl = (float(inset + f_size / 2), float(SHEET_HEIGHT - inset - f_size / 2))

    return [tl, tr, br, bl]


def draw_fiducial(draw: ImageDraw.ImageDraw, center_x: int, center_y: int, size: int = FIDUCIAL_SIZE) -> None:
    """Draw a concentric nested square fiducial target.

    Outer black square -> middle white square -> inner black square.
    This pattern produces a distinct nested contour hierarchy with 100% detection reliability.
    """
    half = size // 2
    # Outer black square
    draw.rectangle(
        [center_x - half, center_y - half, center_x + half, center_y + half],
        fill="black",
        outline="black",
    )
    # Middle white square
    m_half = int(half * 0.60)
    draw.rectangle(
        [center_x - m_half, center_y - m_half, center_x + m_half, center_y + m_half],
        fill="white",
        outline="white",
    )
    # Inner black square
    i_half = int(half * 0.28)
    draw.rectangle(
        [center_x - i_half, center_y - i_half, center_x + i_half, center_y + i_half],
        fill="black",
        outline="black",
    )


def generate_template_image(output_path: str | None = None) -> Image.Image:
    """Generate the standardized guideline sheet image (RGB, 300 DPI)."""
    img = Image.new("RGB", (SHEET_WIDTH, SHEET_HEIGHT), color="white")
    draw = ImageDraw.Draw(img)

    # 1. Draw 4 registration fiducials
    fiducials = get_fiducial_positions()
    for cx, cy in fiducials:
        draw_fiducial(draw, int(cx), int(cy), FIDUCIAL_SIZE)

    # 2. Draw Header Title and Instructions
    header_y = FIDUCIAL_INSET + FIDUCIAL_SIZE + 20
    draw.text(
        (SHEET_WIDTH // 2, header_y),
        "HATEKHORI  —  HANDWRITING CAPTURE TEMPLATE (ENGLISH V1)",
        fill=(30, 30, 30),
        anchor="mt",
    )
    draw.text(
        (SHEET_WIDTH // 2, header_y + 36),
        "Write naturally inside each box using a black or dark blue pen. Keep letters within the guideline marks.",
        fill=(120, 120, 120),
        anchor="mt",
    )

    # 3. Draw grid and guideline ticks
    cells = get_grid_cells()
    cell_border_color = (210, 210, 210)
    guide_color = (225, 235, 245)  # Drop-out light tint
    tick_color = (180, 180, 180)
    label_color = (150, 150, 150)

    for cell in cells:
        # Cell border
        draw.rectangle([cell.x0, cell.y0, cell.x1, cell.y1], outline=cell_border_color, width=1)

        # Subtle guideline lines
        draw.line([(cell.x0 + 8, cell.cap_height_y), (cell.x1 - 8, cell.cap_height_y)], fill=guide_color, width=1)
        draw.line([(cell.x0 + 8, cell.x_height_y), (cell.x1 - 8, cell.x_height_y)], fill=guide_color, width=1)
        draw.line([(cell.x0 + 8, cell.baseline_y), (cell.x1 - 8, cell.baseline_y)], fill=guide_color, width=1)

        # Baseline alignment tick marks at cell margins (helps optical alignment without ink interference)
        draw.line([(cell.x0, cell.baseline_y), (cell.x0 + 8, cell.baseline_y)], fill=tick_color, width=2)
        draw.line([(cell.x1 - 8, cell.baseline_y), (cell.x1, cell.baseline_y)], fill=tick_color, width=2)

        # Character prompt label in the upper corner
        draw.text((cell.x0 + 12, cell.y0 + 10), cell.char, fill=label_color)

    # 4. Footer info
    footer_y = SHEET_HEIGHT - MARGIN_Y + 10
    draw.text(
        (SHEET_WIDTH // 2, footer_y),
        "Ensure all 4 corner registration targets are clearly visible and well-lit when capturing photo.",
        fill=(140, 140, 140),
        anchor="mt",
    )

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        img.save(output_path, dpi=(300, 300))

    return img
