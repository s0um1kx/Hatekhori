"""Guideline-sheet structural validation.

Per AGENTS.md §6: check the upload actually looks like a filled
guideline sheet before it goes further into the pipeline. This doubles
as a security check — junk/inappropriate images mostly won't match the
expected shape.

This is a heuristic, not real structural detection (no corner/marker
detection exists yet — that's a fair chunk of what M3's "real" capture
flow, with QR-based perspective correction, is meant to eventually
provide). This part (2b) adds aspect-ratio + ink-density checks; 2c
wires both into the actual upload flow.
"""

import numpy as np
from PIL import Image

from pipeline.metrics import glyph_ink_bbox
from pipeline.preprocess import binarize
from pipeline.segment import crop_glyphs
from pipeline.sheet import SHEET_HEIGHT, SHEET_WIDTH, corner_marker_boxes

MIN_FILLED_BOX_FRACTION = 0.15  # at least 15% of boxes need actual ink

ASPECT_RATIO_TOLERANCE = 0.15  # 15% — generous, since phone photos rarely crop perfectly
MIN_INK_FRACTION = 0.005  # 0.5% — below this, the sheet looks blank
MAX_INK_FRACTION = 0.7  # 70% — above this, looks solid-black/overexposed rather than written-on


class BadSheetShape(Exception):
    """Raised when the photo's proportions don't resemble the guideline sheet."""


def check_aspect_ratio(img: Image.Image) -> None:
    """Reject a photo whose proportions are way off from an A4 sheet.

    Accepts either portrait or landscape orientation (a sideways photo
    is still a valid photo of the sheet), just not something wildly
    off-shape like a square selfie or a panorama.
    """
    expected_ratio = SHEET_WIDTH / SHEET_HEIGHT
    actual_ratio = img.width / img.height

    # Compare against the expected ratio and its reciprocal (landscape).
    ratios = (expected_ratio, 1 / expected_ratio)
    if not any(abs(actual_ratio - r) / r <= ASPECT_RATIO_TOLERANCE for r in ratios):
        raise BadSheetShape(
            "That photo's proportions don't look like a guideline sheet — "
            "make sure it's cropped to just the paper, not the surroundings."
        )


def check_ink_density(img: Image.Image) -> None:
    """Reject a photo that's essentially blank, or essentially solid ink.

    A blank sheet (nothing written yet) and a heavily over/underexposed
    or scribbled-over photo both fail downstream in unhelpful ways —
    catching them here gives a clearer, kinder error up front instead.
    """
    gray = img.convert("L") if img.mode != "L" else img
    binary = binarize(gray)
    arr = np.array(binary)

    ink_fraction = (arr < 128).sum() / arr.size

    if ink_fraction < MIN_INK_FRACTION:
        raise BadSheetShape(
            "That photo looks blank — make sure you've written in the "
            "guideline sheet's boxes before photographing it."
        )

    if ink_fraction > MAX_INK_FRACTION:
        raise BadSheetShape(
            "That photo looks almost entirely dark — check the lighting "
            "and that the photo isn't underexposed or out of focus."
        )


def check_sheet_is_filled(corrected_img: Image.Image) -> None:
    """Reject a sheet where most individual boxes are actually empty.

    Stronger than check_ink_density: that check only looks at the
    page as a whole, which could in principle still pass even if
    nearly every box is blank (stray marks, the corner markers
    themselves, etc. can be enough ink to clear a page-wide
    threshold). This checks each of the 90 boxes individually and
    counts how many actually have handwriting in them.

    Expects an already perspective-corrected, SHEET_WIDTH x
    SHEET_HEIGHT image — call this after perspective_correct(), not on
    the raw upload.
    """
    glyphs = crop_glyphs(corrected_img)
    filled_count = sum(1 for img in glyphs.values() if glyph_ink_bbox(img) is not None)
    fraction_filled = filled_count / len(glyphs)

    if fraction_filled < MIN_FILLED_BOX_FRACTION:
        raise BadSheetShape(
            "Most of this sheet's boxes look empty — make sure you've "
            "written in them before photographing and uploading it."
        )


# Corner-marker detection. See sheet.py for what's drawn on the sheet —
# a solid black square in each of the 4 corners. Detection works on a
# small downscaled thumbnail of each corner region rather than full
# photo resolution: a phone photo can be many megapixels, and a
# pure-Python pixel scan at that size would be slow. Shrinking first
# makes the search trivially fast regardless of input resolution, at
# the cost of some positional precision — acceptable since the result
# feeds a perspective correction (part 3), not a pixel-exact crop.
CORNER_SEARCH_FRACTION = 0.3  # how much of each dimension to search, from each corner
THUMBNAIL_SIZE = 100


def _find_largest_dark_blob(region: Image.Image) -> tuple[tuple[int, int, int, int], int] | None:
    """Return (bounding_box, pixel_count) of the largest connected dark
    blob in `region`, in that image's own pixel coordinates, or None if
    there's no ink at all. Pixel count (vs. bounding-box area) is what
    lets callers check "solidity" — how filled-in the box actually is.
    """
    gray = region.convert("L") if region.mode != "L" else region
    arr = np.array(gray) < 128  # True = dark/ink
    h, w = arr.shape
    visited = np.zeros_like(arr, dtype=bool)

    best_box = None
    best_size = 0

    for start_y in range(h):
        for start_x in range(w):
            if not arr[start_y, start_x] or visited[start_y, start_x]:
                continue

            stack = [(start_y, start_x)]
            visited[start_y, start_x] = True
            min_x = max_x = start_x
            min_y = max_y = start_y
            size = 0

            while stack:
                cy, cx = stack.pop()
                size += 1
                min_x, max_x = min(min_x, cx), max(max_x, cx)
                min_y, max_y = min(min_y, cy), max(max_y, cy)
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and arr[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        stack.append((ny, nx))

            if size > best_size:
                best_size = size
                best_box = (min_x, min_y, max_x + 1, max_y + 1)

    return (best_box, best_size) if best_box is not None else None


def find_corner_markers(img: Image.Image) -> dict:
    """Locate all 4 corner markers in an uploaded photo.

    Returns {corner_name: (x, y)} center points in the ORIGINAL image's
    pixel coordinates. Raises BadSheetShape if any corner's marker
    can't be found or doesn't look marker-shaped — this is what
    actually rejects a non-sheet photo (a selfie, a random object),
    since aspect-ratio/ink-density checks alone are too permissive.
    """
    gray = img.convert("L") if img.mode != "L" else img
    width, height = gray.size
    search_w = int(width * CORNER_SEARCH_FRACTION)
    search_h = int(height * CORNER_SEARCH_FRACTION)

    regions = {
        "top_left": (0, 0, search_w, search_h),
        "top_right": (width - search_w, 0, width, search_h),
        "bottom_left": (0, height - search_h, search_w, height),
        "bottom_right": (width - search_w, height - search_h, width, height),
    }

    centers = {}
    for name, box in regions.items():
        region = gray.crop(box)
        scale_x = THUMBNAIL_SIZE / region.width
        scale_y = THUMBNAIL_SIZE / region.height
        thumb = region.resize((THUMBNAIL_SIZE, THUMBNAIL_SIZE))

        result = _find_largest_dark_blob(thumb)
        if result is not None:
            (bx0, by0, bx1, by1), pixel_count = result
            blob_w, blob_h = bx1 - bx0, by1 - by0
            bbox_area = blob_w * blob_h
            aspect = blob_w / blob_h if blob_h else 0
            area_fraction = bbox_area / (THUMBNAIL_SIZE * THUMBNAIL_SIZE)
            solidity = pixel_count / bbox_area if bbox_area else 0
        else:
            aspect = area_fraction = solidity = 0

        # Roughly square, roughly marker-sized, and — the key
        # discriminator — solid: a real marker is a filled black
        # square (~90%+ of its own bounding box is ink), whereas noise
        # or ordinary photo content (hair, shadows, clutter) forms
        # irregular, sparser blobs even when their bounding box happens
        # to be square-ish and similarly sized.
        is_valid_marker = (
            result is not None
            and 0.4 <= aspect <= 2.5
            and 0.001 <= area_fraction <= 0.35
            and solidity >= 0.75
        )
        if not is_valid_marker:
            raise BadSheetShape(
                "Couldn't find this sheet's corner markers — make sure "
                "you're using a printed Hatekhori guideline sheet, with "
                "all four corners visible in the photo."
            )

        bx0, by0, bx1, by1 = result[0]
        center_x = box[0] + (bx0 + bx1) / 2 / scale_x
        center_y = box[1] + (by0 + by1) / 2 / scale_y
        centers[name] = (center_x, center_y)

    return centers


def _solve_perspective_coeffs(source_points: list, target_points: list) -> list:
    """Solve the 8 coefficients PIL's Image.transform(..., PERSPECTIVE, ...)
    needs so that each pixel at `target_points[i]` (in the OUTPUT image)
    samples from `source_points[i]` (in the INPUT image) — i.e. maps
    output coordinates back to input coordinates, which is the
    direction PIL's own transform expects.
    """
    matrix = []
    for (sx, sy), (tx, ty) in zip(source_points, target_points):
        matrix.append([tx, ty, 1, 0, 0, 0, -sx * tx, -sx * ty])
        matrix.append([0, 0, 0, tx, ty, 1, -sy * tx, -sy * ty])

    a = np.array(matrix, dtype=np.float64)
    b = np.array(source_points, dtype=np.float64).reshape(8)
    return np.linalg.solve(a, b).tolist()


def perspective_correct(img: Image.Image, marker_centers: dict) -> Image.Image:
    """Warp a photo so its 4 detected marker positions land exactly on
    the canonical sheet's marker positions, producing a SHEET_WIDTH x
    SHEET_HEIGHT image that segment.py's grid math can crop directly —
    without the person needing to crop the photo tight themselves.
    """
    canonical_boxes = corner_marker_boxes(SHEET_WIDTH, SHEET_HEIGHT)
    canonical_centers = {
        name: ((x0 + x1) / 2, (y0 + y1) / 2) for name, (x0, y0, x1, y1) in canonical_boxes.items()
    }

    order = ["top_left", "top_right", "bottom_right", "bottom_left"]
    source_points = [marker_centers[name] for name in order]
    target_points = [canonical_centers[name] for name in order]

    coeffs = _solve_perspective_coeffs(source_points, target_points)
    return img.transform((SHEET_WIDTH, SHEET_HEIGHT), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
