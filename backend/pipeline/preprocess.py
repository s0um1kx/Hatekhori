"""Preprocess step: grayscale -> binarize -> deskew, in that order.

This part adds grayscale and binarize. Deskew is 3c, and 3d wires all
three into an endpoint.
"""

from PIL import Image


def to_grayscale(img: Image.Image) -> Image.Image:
    return img.convert("L")


def binarize(img: Image.Image, threshold: int = 128) -> Image.Image:
    """Push every pixel to pure black or pure white.

    Expects a grayscale image. Anything darker than `threshold` becomes
    ink (black); everything else becomes paper (white). This threshold
    is a placeholder — real handwriting-photo lighting varies enough
    that it'll likely need to become adaptive once real Milestone 1
    photos are run through it.
    """
    gray = img.convert("L") if img.mode != "L" else img
    return gray.point(lambda p: 0 if p < threshold else 255)
