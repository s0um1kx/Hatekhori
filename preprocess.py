"""Image preprocessing, fiducial detection, homography perspective warp, and binarization.

Rectifies scanned or photographed guideline sheets to canonical 2480x3508 A4 coordinates,
normalizes illumination, and produces clean binary ink maps.
"""

from __future__ import annotations

from typing import List, Tuple, Optional
import cv2
import numpy as np
from PIL import Image

try:
    from template import (
        SHEET_WIDTH,
        SHEET_HEIGHT,
        FIDUCIAL_SIZE,
        get_fiducial_positions,
    )
    from ingest import IngestError
except ImportError:
    from .template import (
        SHEET_WIDTH,
        SHEET_HEIGHT,
        FIDUCIAL_SIZE,
        get_fiducial_positions,
    )
    from .ingest import IngestError


class StructuralValidationError(IngestError):
    """Raised when the uploaded image does not structurally match a Hatekhori guideline sheet."""
    pass


def order_quad_points(pts: np.ndarray) -> np.ndarray:
    """Order 4 points clockwise starting from Top-Left: [TL, TR, BR, BL].

    pts is shape (4, 2).
    """
    pts = np.array(pts, dtype=np.float32)
    rect = np.zeros((4, 2), dtype=np.float32)

    # Sum of x + y: Top-Left has minimum sum, Bottom-Right has maximum sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # Difference of y - x: Top-Right has minimum diff, Bottom-Left has maximum diff
    diff = pts[:, 1] - pts[:, 0]
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def find_fiducial_corners(gray: np.ndarray) -> np.ndarray:
    """Detect the 4 concentric square registration fiducials in the image.

    Returns:
        np.ndarray of shape (4, 2) in clockwise order [TL, TR, BR, BL].
    Raises:
        StructuralValidationError if 4 clear corner markers are not found.
    """
    h, w = gray.shape

    # Adaptive binarization to find candidate markers
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 8
    )

    # Find contours and parent-child hierarchy
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if hierarchy is None or len(contours) < 4:
        raise StructuralValidationError(
            "Fewer than 4 contours found",
            "We could not locate all four corner alignment targets on this sheet. Please make sure the entire printed sheet is visible, well-lit, and uncropped.",
        )

    hierarchy = hierarchy[0]
    candidate_centers: List[Tuple[float, float, float]] = []  # (cx, cy, area)

    # Search for nested square patterns: outer contour with child and grandchild
    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area < 200 or area > (w * h * 0.1):
            continue

        # Check aspect ratio and squareness
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)

        x, y, cw, ch = cv2.boundingRect(cnt)
        aspect = float(cw) / float(ch) if ch > 0 else 0
        if 0.70 <= aspect <= 1.40 and len(approx) in (4, 5, 6, 8):
            # Check hierarchy: does it have a child contour?
            child_idx = hierarchy[i][2]
            if child_idx != -1:
                # Target has nested rings!
                M = cv2.moments(cnt)
                if M["m00"] > 0:
                    cx = float(M["m10"] / M["m00"])
                    cy = float(M["m01"] / M["m00"])
                    candidate_centers.append((cx, cy, area))

    # If strict nested search found fewer than 4 (e.g. in heavy blur), fall back to corner region search
    if len(candidate_centers) < 4:
        # Search in the 4 corner quadrants of the image
        quadrants = [
            (0, 0, w // 3, h // 3),                 # TL
            (2 * w // 3, 0, w, h // 3),             # TR
            (2 * w // 3, 2 * h // 3, w, h),         # BR
            (0, 2 * h // 3, w // 3, h),             # BL
        ]
        quad_candidates: List[Tuple[float, float]] = []

        for qx0, qy0, qx1, qy1 in quadrants:
            best_center = None
            best_score = -1.0
            for i, cnt in enumerate(contours):
                area = cv2.contourArea(cnt)
                if area < 150 or area > (w * h * 0.05):
                    continue
                M = cv2.moments(cnt)
                if M["m00"] == 0:
                    continue
                cx = float(M["m10"] / M["m00"])
                cy = float(M["m01"] / M["m00"])
                if qx0 <= cx <= qx1 and qy0 <= cy <= qy1:
                    peri = cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
                    x, y, cw, ch = cv2.boundingRect(cnt)
                    aspect = float(cw) / float(ch) if ch > 0 else 0
                    if 0.65 <= aspect <= 1.50 and len(approx) >= 4:
                        score = area
                        if score > best_score:
                            best_score = score
                            best_center = (cx, cy)
            if best_center:
                quad_candidates.append(best_center)

        if len(quad_candidates) == 4:
            return order_quad_points(np.array(quad_candidates, dtype=np.float32))

        raise StructuralValidationError(
            f"Found only {len(candidate_centers)} fiducial markers",
            "We could not locate all four corner alignment targets on this sheet. Please make sure all four corner squares are visible and uncropped.",
        )

    # We have candidates. Cluster or assign one best candidate to each of the 4 image quadrants.
    quadrants = [
        ("TL", 0, 0, w // 2, h // 2),
        ("TR", w // 2, 0, w, h // 2),
        ("BR", w // 2, h // 2, w, h),
        ("BL", 0, h // 2, w // 2, h),
    ]

    selected_points: List[Tuple[float, float]] = []
    for name, qx0, qy0, qx1, qy1 in quadrants:
        in_quad = [c for c in candidate_centers if qx0 <= c[0] <= qx1 and qy0 <= c[1] <= qy1]
        if not in_quad:
            raise StructuralValidationError(
                f"Missing fiducial marker in {name} corner",
                f"The corner target at the {name} of the sheet could not be detected. Please ensure all four corners are clearly framed.",
            )
        # Select the candidate closest to the true corner
        if name == "TL":
            best = min(in_quad, key=lambda c: c[0]**2 + c[1]**2)
        elif name == "TR":
            best = min(in_quad, key=lambda c: (w - c[0])**2 + c[1]**2)
        elif name == "BR":
            best = min(in_quad, key=lambda c: (w - c[0])**2 + (h - c[1])**2)
        else:  # BL
            best = min(in_quad, key=lambda c: c[0]**2 + (h - c[1])**2)
        selected_points.append((best[0], best[1]))

    return order_quad_points(np.array(selected_points, dtype=np.float32))


def rectify_perspective(image_bgr: np.ndarray, src_corners: np.ndarray) -> np.ndarray:
    """Warp input photo using perspective homography to canonical A4 sheet dimensions."""
    canonical_corners = np.array(get_fiducial_positions(), dtype=np.float32)
    # Order: [TL, TR, BR, BL]
    canonical_ordered = order_quad_points(canonical_corners)

    H_matrix = cv2.getPerspectiveTransform(src_corners, canonical_ordered)
    rectified = cv2.warpPerspective(
        image_bgr,
        H_matrix,
        (SHEET_WIDTH, SHEET_HEIGHT),
        flags=cv2.INTER_LANCZOS4,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return rectified


def flatten_illumination(gray: np.ndarray) -> np.ndarray:
    """Remove uneven shadows and lighting gradients across the sheet using morphological background division."""
    # Morphological closing with a large kernel estimates the paper background illumination
    kernel_size = 51
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    background = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

    # Division normalization: (gray / background) * 255
    # Avoid zero division
    norm = cv2.divide(gray, np.maximum(background, 1), scale=255)
    return norm


def binarize_ink(gray_normalized: np.ndarray) -> np.ndarray:
    """Produce a crisp binary ink mask (255 for ink strokes, 0 for paper background).

    Uses adaptive Gaussian thresholding followed by connected component noise suppression.
    """
    # Invert so ink is foreground (high value)
    ink_mask = cv2.adaptiveThreshold(
        gray_normalized,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=31,
        C=12,
    )

    # Remove isolated 1-2 pixel noise specks using small morphological opening
    clean_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(ink_mask, cv2.MORPH_OPEN, clean_kernel)

    return cleaned


def preprocess_sheet(
    image: Image.Image | np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Execute complete preprocessing pipeline:
    1. Grayscale conversion.
    2. Fiducial corner localization.
    3. 4-point homography perspective warp.
    4. Shadow removal / illumination flattening.
    5. High-fidelity adaptive ink binarization.

    Returns:
        (rectified_bgr, rectified_gray_normalized, binary_ink_mask)
    """
    if isinstance(image, Image.Image):
        # Convert PIL to BGR numpy array
        img_np = np.array(image.convert("RGB"))
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    else:
        img_bgr = image

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 1. Detect fiducials
    corners = find_fiducial_corners(gray)

    # 2. Rectify perspective
    rectified_bgr = rectify_perspective(img_bgr, corners)
    rectified_gray = cv2.cvtColor(rectified_bgr, cv2.COLOR_BGR2GRAY)

    # 3. Flatten illumination
    normalized_gray = flatten_illumination(rectified_gray)

    # 4. Adaptive binarization
    binary_ink = binarize_ink(normalized_gray)

    return rectified_bgr, normalized_gray, binary_ink
