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

from pipeline.preprocess import binarize
from pipeline.sheet import SHEET_HEIGHT, SHEET_WIDTH

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
