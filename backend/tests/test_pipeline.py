"""Self-check, no pytest needed:  python backend/tests/test_pipeline.py"""

import io
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.chdir(tempfile.mkdtemp())  # uploads/ and output/ are cwd-relative; keep them out of the repo

from fastapi.testclient import TestClient
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from app.main import app
from pipeline.segment import char_grid, compute_grid_boxes
from pipeline.sheet import SHEET_HEIGHT, SHEET_WIDTH, draw_corner_markers, generate_guideline_sheet
from pipeline.validate import _solve_perspective_coeffs

client = TestClient(app)


def filled_sheet() -> Image.Image:
    """A sheet with every box 'written in' (system-independent stand-in for handwriting)."""
    img = Image.new("L", (SHEET_WIDTH, SHEET_HEIGHT), 255)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=80)
    for box, char in zip(compute_grid_boxes(SHEET_WIDTH, SHEET_HEIGHT), char_grid()):
        x0, y0, x1, y1 = box["box"]
        draw.text(((x0 + x1) / 2, (y0 + y1) / 2), char, font=font, fill=0, anchor="mm")
    draw_corner_markers(draw, SHEET_WIDTH, SHEET_HEIGHT)
    return img


def encode(img, fmt="PNG", **kw) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=fmt, **kw)
    return buf.getvalue()


def upload(data: bytes):
    return client.post("/ingest", files={"file": ("x", data, "application/octet-stream")})


def make_id(data: bytes) -> str:
    r = upload(data)
    assert r.status_code == 200, r.text
    return r.json()["id"]


def test_full_flow():
    uid = make_id(encode(filled_sheet()))
    r = client.post(f"/generate/{uid}")
    assert r.status_code == 200, r.text
    font = client.get(f"/download-font/{uid}")
    assert font.headers["content-disposition"].startswith("attachment")
    assert "content-disposition" not in client.get(f"/download-font/{uid}?inline=true").headers
    Path("f.otf").write_bytes(font.content)
    assert len(TTFont("f.otf").getBestCmap()) == r.json()["glyph_count"] + 1  # + generated space
    assert os.listdir("uploads") == [], "raw photo must be deleted after use"
    assert os.listdir("output") == [f"{uid}.otf"], "one file per font, nothing else"


def test_tall_photo_still_accepted():
    quad = [(30, 190), (1050, 175), (1060, 1720), (20, 1705)]  # 9:16 frame, slightly skewed
    corners = [(0, 0), (SHEET_WIDTH, 0), (SHEET_WIDTH, SHEET_HEIGHT), (0, SHEET_HEIGHT)]
    coeffs = _solve_perspective_coeffs(corners, quad)
    photo = filled_sheet().transform((1080, 1920), Image.PERSPECTIVE, coeffs, Image.BICUBIC, fillcolor=200)
    uid = make_id(encode(photo))
    assert client.post(f"/generate/{uid}").status_code == 200


def test_screenshot_clutter_accepted():
    """A screenshot of the sheet: dark title bar on top, thick black frame lines down both sides."""
    shot = Image.new("L", (660, 900), 235)
    shot.paste(filled_sheet().resize((604, 854)), (28, 40))
    draw = ImageDraw.Draw(shot)
    draw.rectangle([0, 0, 660, 32], fill=57)
    draw.rectangle([18, 0, 22, 900], fill=5)
    draw.rectangle([640, 0, 644, 900], fill=5)
    uid = make_id(encode(shot))
    assert client.post(f"/generate/{uid}").status_code == 200


def test_rejections():
    for name, data in {
        "not an image": b"definitely not an image",
        "heic stub": b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00mif1heic" + b"x" * 64,
    }.items():
        assert upload(data).status_code == 400, name
    for name, img in {
        "blank sheet": generate_guideline_sheet(),
        "noise": Image.effect_noise((1240, 1754), 80),
    }.items():
        uid = make_id(encode(img))
        r = client.post(f"/generate/{uid}")
        assert r.status_code == 400, (name, r.status_code)
        assert not Path(f"uploads/{uid}.img").exists(), "failed photo must not linger"


def test_exif_stripped():
    exif = Image.Exif()
    exif[0x010F] = "SecretCameraMaker"
    data = encode(Image.new("RGB", (400, 300), "white"), "JPEG", exif=exif.tobytes())
    assert b"SecretCameraMaker" in data, "test input must actually carry metadata"
    uid = make_id(data)
    assert b"SecretCameraMaker" not in Path(f"uploads/{uid}.img").read_bytes()
    Path(f"uploads/{uid}.img").unlink()


def test_ids_are_not_wildcards():
    uid = make_id(encode(filled_sheet()))
    assert client.post("/generate/*").status_code == 422
    assert client.get("/download-font/..%5C..%5Cx").status_code == 422
    assert client.post(f"/generate/{uid}").status_code == 200, "other uploads must be untouched"


def test_oversize_dimensions_rejected():
    assert upload(encode(Image.new("L", (6001, 10)))).status_code == 400


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
