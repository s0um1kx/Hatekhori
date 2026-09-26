"""Preprocess step: grayscale -> binarize -> deskew, in that order.

This part only adds grayscale. Binarize is 3b, deskew is 3c, and 3d wires
all three into an endpoint.
"""

from PIL import Image


def to_grayscale(img: Image.Image) -> Image.Image:
    return img.convert("L")
