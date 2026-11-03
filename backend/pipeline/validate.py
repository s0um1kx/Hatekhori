"""Is this photo a filled Hatekhori sheet? Four corner markers, then enough written boxes (AGENTS.md §6)."""

import numpy as np
from PIL import Image

from pipeline.metrics import glyph_has_ink, glyph_ink_bbox
from pipeline.sheet import SHEET_HEIGHT, SHEET_WIDTH, corner_marker_boxes, orientation_bar_box

MIN_FILLED_BOX_FRACTION = 0.15  # at least 15% of boxes need actual ink
BAR_MIN_CONTRAST = 70  # gray levels: paper minus bar, for the orientation bar to count as seen
BAR_MIN_MARGIN = 40  # the right rotation must beat the runner-up by this much
NO_BAR_WARNING = (
    "No orientation bar found, so the sheet was assumed to be upright. If it was photographed "
    "sideways or upside-down, letters will land in the wrong boxes."
)
CORNER_WORDS = {"top_left": "top-left", "top_right": "top-right", "bottom_left": "bottom-left", "bottom_right": "bottom-right"}


class BadSheetShape(Exception):
    """The photo is not a usable, filled guideline sheet."""


def check_sheet_is_filled(glyphs: dict) -> None:
    """Reject a sheet where most boxes are empty. `glyphs` is crop_glyphs() output."""
    filled = sum(1 for g in glyphs.values() if glyph_has_ink(g))
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


def _find_marker(region: Image.Image, corner: str = "top_left"):
    """The marker in one corner region, as ("ok", (center_x, center_y, size)) in the region's own
    pixels, ("missing", None) or ("crowded", None). Marker-shaped = a solid, squarish blob of plausible size.
    If multiple blobs exist, we check if one is closest to the expected outer corner. If another blob is
    touching or immediately adjacent to that marker, it is 'crowded'. If other blobs are far away
    (e.g. handwriting inside the guideline boxes), the outer corner marker is accepted."""
    scale = THUMBNAIL_SIZE / max(region.size)
    tw, th = max(1, round(region.width * scale)), max(1, round(region.height * scale))
    mask = _erode(np.array(region.resize((tw, th))) < 128)

    candidates = [
        ((x0 + x1) / 2 / scale, (y0 + y1) / 2 / scale, ((x1 - x0 + 2) * (y1 - y0 + 2)) ** 0.5 / scale)  # +2: undo erosion
        for x0, y0, x1, y1, n in _blobs(mask)
        if x1 - x0 >= 3 and y1 - y0 >= 3 and 0.5 <= (x1 - x0) / (y1 - y0) <= 2.0
        and n / ((x1 - x0) * (y1 - y0)) >= 0.7 and (x1 - x0) * (y1 - y0) <= 0.1 * tw * th
    ]
    if not candidates:
        return "missing", None
    if len(candidates) == 1:
        return "ok", candidates[0]

    # Multiple candidates: determine the corner's origin in region coordinates
    rw, rh = region.size
    ox = 0 if "left" in corner else rw
    oy = 0 if "top" in corner else rh

    candidates.sort(key=lambda c: (c[0] - ox) ** 2 + (c[1] - oy) ** 2)
    best = candidates[0]
    best_size = best[2]

    if len(candidates) > 4:
        return "crowded", None

    for other in candidates[1:]:
        dist = ((best[0] - other[0]) ** 2 + (best[1] - other[1]) ** 2) ** 0.5
        if dist < 2.5 * best_size:
            return "crowded", None

    return "ok", best


def _words(names: list) -> str:
    words = [CORNER_WORDS[n] for n in names]
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]


def to_grayscale_sheet(img: Image.Image) -> Image.Image:
    """Convert image to grayscale, compositing any alpha transparency onto white paper."""
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        rgba = img.convert("RGBA")
        bg.paste(rgba, mask=rgba.split()[3])
        return bg.convert("L")
    return img.convert("L")


def find_corner_markers(img: Image.Image) -> dict:
    """Locate the 4 corner markers: {corner_name: (x, y)} in the photo's own pixels.
    Raises BadSheetShape, naming the corner(s) at fault, if they can't all be found."""
    gray = to_grayscale_sheet(img)
    width, height = gray.size
    sw, sh = int(width * CORNER_SEARCH_FRACTION), int(height * CORNER_SEARCH_FRACTION)
    regions = {
        "top_left": (0, 0, sw, sh),
        "top_right": (width - sw, 0, width, sh),
        "bottom_left": (0, height - sh, sw, height),
        "bottom_right": (width - sw, height - sh, width, height),
    }

    results = {name: _find_marker(gray.crop(box), name) for name, box in regions.items()}
    ok = {name: value for name, (status, value) in results.items() if status == "ok"}
    missing = [name for name, (status, _) in results.items() if status == "missing"]
    crowded = [name for name, (status, _) in results.items() if status == "crowded"]

    if not ok:
        raise BadSheetShape(
            "No corner squares found, so this doesn't look like a Hatekhori guideline sheet. If it is one, move "
            "closer so the sheet fills most of the photo, with all four black corner squares in view."
        )
    if missing:
        raise BadSheetShape(
            f"Couldn't find the {_words(missing)} corner square{'s' if len(missing) > 1 else ''}. "
            "Make sure all four black corner squares are fully in the photo, not covered, and that the sheet "
            "fills most of the photo."
        )
    if crowded:
        raise BadSheetShape(
            f"Something else dark is touching or very near the {_words(crowded)} corner square"
            f"{'s' if len(crowded) > 1 else ''} (a finger, a shadow, the edge of the table). "
            "Move it out of the frame and try again."
        )
    sizes = [value[2] for value in ok.values()]
    if max(sizes) / min(sizes) > MAX_MARKER_SIZE_RATIO:
        raise BadSheetShape(
            "The four corner squares look very different in size. "
            "Hold the camera straight above the sheet, not at a steep angle."
        )
    return {name: (regions[name][0] + value[0], regions[name][1] + value[1]) for name, value in ok.items()}


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
    try:
        return np.linalg.solve(a, b).tolist()
    except np.linalg.LinAlgError:
        raise BadSheetShape(
            "Could not align sheet perspective — make sure the sheet is flat, not folded, "
            "and all four corner squares are clearly visible."
        )


CORNER_ORDER = ["top_left", "top_right", "bottom_right", "bottom_left"]


def perspective_correct(img: Image.Image, marker_centers: dict, turns: int = 0) -> Image.Image:
    """Warp a photo so its 4 detected markers land on the canonical sheet's markers, giving a
    SHEET_WIDTH x SHEET_HEIGHT image that segment.py's grid math can crop directly.
    `turns` assigns the photo's corners to the sheet's corners rotated by that many quarter turns
    (0 = the photo is upright), which is how a sideways or upside-down sheet gets straightened."""
    canonical_centers = {
        name: ((x0 + x1) / 2, (y0 + y1) / 2)
        for name, (x0, y0, x1, y1) in corner_marker_boxes(SHEET_WIDTH, SHEET_HEIGHT).items()
    }
    source_points = [marker_centers[name] for name in CORNER_ORDER]
    target_points = [canonical_centers[CORNER_ORDER[(i + turns) % 4]] for i in range(4)]

    coeffs = _solve_perspective_coeffs(source_points, target_points)
    return img.transform((SHEET_WIDTH, SHEET_HEIGHT), Image.PERSPECTIVE, coeffs, Image.BICUBIC)


def _bar_contrast(sheet: Image.Image) -> float:
    """How much darker the orientation bar's spot is than the paper just above and below it."""
    x0, y0, x1, y1 = orientation_bar_box(SHEET_WIDTH, SHEET_HEIGHT)
    a = np.asarray(sheet, dtype=float)
    bar = a[y0 + 2 : y1 - 1, x0:x1].mean()
    around = np.concatenate([a[y0 - 26 : y0 - 8, x0:x1].ravel(), a[y1 + 8 : y1 + 26, x0:x1].ravel()]).mean()
    return around - bar


def straighten(img: Image.Image):
    """(upright grayscale sheet at SHEET_WIDTH x SHEET_HEIGHT, warnings). Tries all four rotations and
    keeps the one whose orientation bar lands at the top. A sheet with no bar (an older print, or a
    covered bar) is assumed upright, with a warning, since there is nothing to tell it apart by."""
    gray = to_grayscale_sheet(img)
    markers = find_corner_markers(gray)
    sheets = [perspective_correct(gray, markers, turns) for turns in range(4)]
    scores = [_bar_contrast(sheet) for sheet in sheets]
    best = int(np.argmax(scores))
    runner_up = max(score for i, score in enumerate(scores) if i != best)
    if scores[best] >= BAR_MIN_CONTRAST and scores[best] - runner_up >= BAR_MIN_MARGIN:
        return sheets[best], []
    return sheets[0], [NO_BAR_WARNING]
