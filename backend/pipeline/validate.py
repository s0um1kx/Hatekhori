"""Is this photo a filled Hatekhori sheet? Four corner markers, then enough written boxes (AGENTS.md §6)."""

import numpy as np
from PIL import Image

from pipeline.metrics import glyph_ink_bbox
from pipeline.sheet import SHEET_HEIGHT, SHEET_WIDTH, corner_marker_boxes

MIN_FILLED_BOX_FRACTION = 0.15  # at least 15% of boxes need actual ink


class BadSheetShape(Exception):
    """The photo is not a usable, filled guideline sheet."""


def check_sheet_is_filled(glyphs: dict) -> None:
    """Reject a sheet where most boxes are empty. `glyphs` is crop_glyphs() output."""
    filled = sum(1 for g in glyphs.values() if glyph_ink_bbox(g) is not None)
    if filled / len(glyphs) < MIN_FILLED_BOX_FRACTION:
        raise BadSheetShape(
            "Most of this sheet's boxes look empty — make sure you've "
            "written in them before photographing and uploading it."
        )


# Corner-marker detection. The sheet has a solid black square in each corner (sheet.py).
# Each corner region is shrunk to a small thumbnail first: a phone photo can be many
# megapixels and a pure-Python pixel scan at that size is slow.
CORNER_SEARCH_FRACTION = 0.3  # how much of each dimension to search, from each corner
THUMBNAIL_SIZE = 128  # longest side of a corner thumbnail
MAX_MARKER_SIZE_RATIO = 2.5  # the four markers should look about the same size


def _erode(mask: np.ndarray) -> np.ndarray:
    """3x3 erosion. Wipes out lines thinner than 3px, so a frame line or edge next to a
    marker can't merge with it; a solid square just shrinks by one pixel per side."""
    h, w = mask.shape
    padded = np.pad(mask, 1)
    out = np.ones_like(mask)
    for dy in range(3):
        for dx in range(3):
            out &= padded[dy : dy + h, dx : dx + w]
    return out


def _blobs(mask: np.ndarray):
    """Yield (x0, y0, x1, y1, pixel_count) for every 4-connected blob in a boolean mask."""
    h, w = mask.shape
    seen = np.zeros_like(mask)
    for sy in range(h):
        for sx in range(w):
            if not mask[sy, sx] or seen[sy, sx]:
                continue
            stack, seen[sy, sx] = [(sy, sx)], True
            x0 = x1 = sx
            y0 = y1 = sy
            n = 0
            while stack:
                y, x = stack.pop()
                n += 1
                x0, x1, y0, y1 = min(x0, x), max(x1, x), min(y0, y), max(y1, y)
                for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
            yield x0, y0, x1 + 1, y1 + 1, n


def _find_marker(region: Image.Image):
    """The marker in one corner region: (center_x, center_y, size) in the region's own
    pixels, or None. Marker-shaped = a solid, squarish blob of plausible size. There must be
    exactly ONE: bars, frame lines and handwriting don't qualify, but textured clutter
    (grass, brick) is full of such blobs, so several candidates means this isn't a clean sheet."""
    scale = THUMBNAIL_SIZE / max(region.size)
    tw, th = max(1, round(region.width * scale)), max(1, round(region.height * scale))
    mask = _erode(np.array(region.resize((tw, th))) < 128)

    candidates = [
        ((x0 + x1) / 2 / scale, (y0 + y1) / 2 / scale, ((x1 - x0 + 2) * (y1 - y0 + 2)) ** 0.5 / scale)  # +2: undo erosion
        for x0, y0, x1, y1, n in _blobs(mask)
        if x1 - x0 >= 3 and y1 - y0 >= 3 and 0.5 <= (x1 - x0) / (y1 - y0) <= 2.0
        and n / ((x1 - x0) * (y1 - y0)) >= 0.7 and (x1 - x0) * (y1 - y0) <= 0.1 * tw * th
    ]
    return candidates[0] if len(candidates) == 1 else None


def find_corner_markers(img: Image.Image) -> dict:
    """Locate the 4 corner markers: {corner_name: (x, y)} in the photo's own pixels.
    Raises BadSheetShape if any is missing — this is what rejects a non-sheet photo."""
    gray = img.convert("L")
    width, height = gray.size
    sw, sh = int(width * CORNER_SEARCH_FRACTION), int(height * CORNER_SEARCH_FRACTION)
    regions = {
        "top_left": (0, 0, sw, sh),
        "top_right": (width - sw, 0, width, sh),
        "bottom_left": (0, height - sh, sw, height),
        "bottom_right": (width - sw, height - sh, width, height),
    }

    found = {name: _find_marker(gray.crop(box)) for name, box in regions.items()}
    sizes = [f[2] for f in found.values() if f]
    if len(sizes) < 4 or max(sizes) / min(sizes) > MAX_MARKER_SIZE_RATIO:
        raise BadSheetShape(
            "Couldn't find this sheet's corner markers — make sure "
            "you're using a printed Hatekhori guideline sheet, with "
            "all four corners visible in the photo."
        )
    return {name: (regions[name][0] + f[0], regions[name][1] + f[1]) for name, f in found.items()}


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
