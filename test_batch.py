"""Synthetic handwriting test batch generator for Milestone 1 kill-test.

Generates 5 realistic handwriting capture sheets with varied pens, lighting, and camera angles:
1. Sample 1: Thin, crisp archival gel pen (clean, even lighting).
2. Sample 2: Heavy fountain pen with ink bleed and variable pressure.
3. Sample 3: Mobile phone capture with harsh diagonal shadow gradient.
4. Sample 4: Tilted and perspective-skewed capture on a tabletop background.
5. Sample 5: Casual cursive handwriting with natural slant and baseline jitter.
"""

from __future__ import annotations

import os
import math
import random
from typing import List, Tuple, Dict
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    from template import (
        SHEET_WIDTH,
        SHEET_HEIGHT,
        get_grid_cells,
        generate_template_image,
        CellInfo,
    )
except ImportError:
    from .template import (
        SHEET_WIDTH,
        SHEET_HEIGHT,
        get_grid_cells,
        generate_template_image,
        CellInfo,
    )


FONT_CANDIDATES = {
    "gel_pen": "C:/Windows/Fonts/segoepr.ttf",
    "fountain_pen": "C:/Windows/Fonts/LHANDW.TTF",
    "phone_shadow": "C:/Windows/Fonts/Inkfree.ttf",
    "perspective_tilt": "C:/Windows/Fonts/comic.ttf",
    "casual_slant": "C:/Windows/Fonts/segoesc.ttf",
}


def _get_font(style: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONT_CANDIDATES.get(style, "C:/Windows/Fonts/segoepr.ttf")
    if not os.path.exists(path):
        # Fallback to any available font
        for fallback in FONT_CANDIDATES.values():
            if os.path.exists(fallback):
                path = fallback
                break
    return ImageFont.truetype(path, size=size)


def _render_chars_on_sheet(
    base_sheet: Image.Image,
    font: ImageFont.FreeTypeFont,
    ink_color: Tuple[int, int, int],
    jitter_baseline: int = 0,
    jitter_x: int = 0,
) -> Image.Image:
    """Draw handwriting characters inside all 64 cells of the guideline sheet."""
    sheet = base_sheet.copy()
    draw = ImageDraw.Draw(sheet)
    cells = get_grid_cells()

    random.seed(42)  # Deterministic test generation

    for cell in cells:
        cx = cell.x0 + cell.width // 2
        cy = cell.baseline_y

        if jitter_x > 0:
            cx += random.randint(-jitter_x, jitter_x)
        if jitter_baseline > 0:
            cy += random.randint(-jitter_baseline, jitter_baseline)

        # Draw character anchored at middle-baseline
        draw.text((cx, cy), cell.char, font=font, fill=ink_color, anchor="ms")

    return sheet


def generate_sample_1_gel_pen(output_path: str) -> str:
    """Sample 1: Thin, crisp archival black gel pen on pristine paper."""
    base = generate_template_image()
    font = _get_font("gel_pen", size=140)
    sheet = _render_chars_on_sheet(base, font, ink_color=(20, 25, 35))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    sheet.save(output_path, quality=95)
    return output_path


def generate_sample_2_fountain_pen(output_path: str) -> str:
    """Sample 2: Heavy fountain pen with rich blue ink bleed and pooling."""
    base = generate_template_image()
    font = _get_font("fountain_pen", size=130)
    # Deep royal blue ink
    sheet = _render_chars_on_sheet(base, font, ink_color=(15, 35, 110))

    # Simulate ink bleed/feathering with slight dilation
    img_np = np.array(sheet)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    _, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Dilate ink slightly (1px)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    dilated_mask = cv2.dilate(mask, kernel, iterations=1)

    # Blend dilated ink into original image
    ink_color = np.array([20, 45, 120], dtype=np.uint8)
    img_np[dilated_mask > 0] = (
        0.7 * img_np[dilated_mask > 0] + 0.3 * ink_color
    ).astype(np.uint8)

    result = Image.fromarray(img_np)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    result.save(output_path, quality=95)
    return output_path


def generate_sample_3_phone_shadow(output_path: str) -> str:
    """Sample 3: Mobile phone camera capture with a strong diagonal shadow gradient."""
    base = generate_template_image()
    font = _get_font("phone_shadow", size=145)
    sheet = _render_chars_on_sheet(base, font, ink_color=(30, 30, 40))

    # Apply diagonal lighting shadow gradient (bright top-right, dark bottom-left)
    w, h = sheet.size
    img_np = np.array(sheet, dtype=np.float32)

    # Create 2D gradient mesh
    y_coords, x_coords = np.mgrid[:h, :w]
    # Normalized diagonal from top-right (1.0) to bottom-left (0.42)
    diag = (x_coords / w) * 0.4 + (1.0 - (y_coords / h)) * 0.4 + 0.35
    gradient = np.clip(diag, 0.40, 1.0)[:, :, np.newaxis]

    shadowed = np.clip(img_np * gradient, 0, 255).astype(np.uint8)
    result = Image.fromarray(shadowed)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    result.save(output_path, quality=92)
    return output_path


def generate_sample_4_perspective_tilt(output_path: str) -> str:
    """Sample 4: Guideline sheet photographed on a table with 10-degree tilt and perspective keystone."""
    base = generate_template_image()
    font = _get_font("perspective_tilt", size=135)
    sheet = _render_chars_on_sheet(base, font, ink_color=(25, 45, 100))

    # Canvas dimensions representing tabletop photo
    canvas_w, canvas_h = 3200, 4200
    sheet_np = np.array(sheet)

    # Define 4 source corners of canonical sheet
    src_pts = np.array([
        [0, 0],
        [SHEET_WIDTH, 0],
        [SHEET_WIDTH, SHEET_HEIGHT],
        [0, SHEET_HEIGHT],
    ], dtype=np.float32)

    # Define 4 target points with perspective warp and 9-degree rotation
    # Placed with margins on the larger canvas
    pad_x, pad_y = 350, 350
    dst_pts = np.array([
        [pad_x + 120, pad_y + 80],                      # TL: shifted right/down
        [canvas_w - pad_x - 180, pad_y + 20],            # TR: slightly higher
        [canvas_w - pad_x - 60, canvas_h - pad_y - 80],  # BR: shifted
        [pad_x + 40, canvas_h - pad_y - 120],            # BL: shifted
    ], dtype=np.float32)

    # Compute homography
    H = cv2.getPerspectiveTransform(src_pts, dst_pts)

    # Table background color (warm wood/desk tone: #D8CEBE)
    table_bg = np.full((canvas_h, canvas_w, 3), (190, 206, 216), dtype=np.uint8)

    # Warp sheet onto canvas
    warped = cv2.warpPerspective(
        sheet_np, H, (canvas_w, canvas_h),
        flags=cv2.INTER_LANCZOS4,
        borderMode=cv2.BORDER_TRANSPARENT,
    )

    # Mask warped content over table background
    gray_warped = cv2.cvtColor(warped, cv2.COLOR_RGB2GRAY)
    mask = (gray_warped > 0)[:, :, np.newaxis]
    composite = np.where(mask, warped, table_bg)

    result = Image.fromarray(composite)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    result.save(output_path, quality=92)
    return output_path


def generate_sample_5_casual_slant(output_path: str) -> str:
    """Sample 5: Casual cursive handwriting with natural letter slant and baseline jitter."""
    base = generate_template_image()
    font = _get_font("casual_slant", size=135)
    # Slight baseline and horizontal jitter to simulate casual hand
    sheet = _render_chars_on_sheet(
        base,
        font,
        ink_color=(25, 25, 30),
        jitter_baseline=4,
        jitter_x=3,
    )

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    sheet.save(output_path, quality=95)
    return output_path


def generate_all_samples(output_dir: str = "test_samples") -> Dict[str, str]:
    """Generate all 5 test samples and return dict of sample_name -> file_path."""
    os.makedirs(output_dir, exist_ok=True)

    samples = {
        "sample_1_gel_pen": os.path.join(output_dir, "sample_1_gel_pen.jpg"),
        "sample_2_fountain_pen": os.path.join(output_dir, "sample_2_fountain_pen.jpg"),
        "sample_3_phone_shadow": os.path.join(output_dir, "sample_3_phone_shadow.jpg"),
        "sample_4_perspective_tilt": os.path.join(output_dir, "sample_4_perspective_tilt.jpg"),
        "sample_5_casual_slant": os.path.join(output_dir, "sample_5_casual_slant.jpg"),
    }

    print("Generating Sample 1 (Gel Pen)...")
    generate_sample_1_gel_pen(samples["sample_1_gel_pen"])

    print("Generating Sample 2 (Fountain Pen Bleed)...")
    generate_sample_2_fountain_pen(samples["sample_2_fountain_pen"])

    print("Generating Sample 3 (Phone Shadow Gradient)...")
    generate_sample_3_phone_shadow(samples["sample_3_phone_shadow"])

    print("Generating Sample 4 (Perspective Tilt on Table)...")
    generate_sample_4_perspective_tilt(samples["sample_4_perspective_tilt"])

    print("Generating Sample 5 (Casual Slant)...")
    generate_sample_5_casual_slant(samples["sample_5_casual_slant"])

    print("All 5 test samples successfully generated in:", output_dir)
    return samples


if __name__ == "__main__":
    generate_all_samples()
