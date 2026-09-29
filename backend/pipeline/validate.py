"""Guideline-sheet structural validation.

Per AGENTS.md §6: check the upload actually looks like a filled
guideline sheet before it goes further into the pipeline. This doubles
as a security check — junk/inappropriate images mostly won't match the
expected shape.

This is a heuristic, not real structural detection (no corner/marker
detection exists yet — that's a fair chunk of what M3's "real" capture
flow, with QR-based perspective correction, is meant to eventually
provide). This part (2a) only adds the aspect-ratio check.
"""

from PIL import Image

from pipeline.sheet import SHEET_HEIGHT, SHEET_WIDTH

ASPECT_RATIO_TOLERANCE = 0.15  # 15% — generous, since phone photos rarely crop perfectly


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
