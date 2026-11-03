"""Self-check, no pytest needed:  python backend/tests/test_pipeline.py"""

import io
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
test_tmp = tempfile.mkdtemp()
os.environ["HATEKHORI_DATA_DIR"] = test_tmp
os.chdir(test_tmp)  # uploads/ and output/ are anchored to test_tmp; keep them out of the repo

import numpy as np
from fastapi.testclient import TestClient
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from app.main import _GENERATE_SEMAPHORE, _get_guideline_sheet_bytes, app
from pipeline.segment import char_grid, compute_grid_boxes, crop_glyphs
from pipeline.sheet import (
    SHEET_HEIGHT,
    SHEET_WIDTH,
    corner_marker_boxes,
    draw_corner_markers,
    draw_orientation_bar,
    generate_guideline_sheet,
    get_bengali_font,
)
from pipeline.cleanup import binarize_sheet, sweep
from pipeline.compile import build_font
from pipeline.metrics import glyph_ink_bbox
from pipeline.validate import BadSheetShape, _solve_perspective_coeffs, find_corner_markers, straighten
from pipeline.vectorize import trace_glyph

client = TestClient(app)


def filled_sheet(bar: bool = True) -> Image.Image:
    """A sheet with every box 'written in' (system-independent stand-in for handwriting).
    bar=False imitates a sheet printed before the orientation bar existed."""
    img = Image.new("L", (SHEET_WIDTH, SHEET_HEIGHT), 255)
    draw = ImageDraw.Draw(img)
    font = get_bengali_font(size=60)
    for box, char in zip(compute_grid_boxes(SHEET_WIDTH, SHEET_HEIGHT), char_grid()):
        x0, y0, x1, y1 = box["box"]
        draw.text(((x0 + x1) / 2, (y0 + y1) / 2), char, font=font, fill=0, anchor="mm")
    draw_corner_markers(draw, SHEET_WIDTH, SHEET_HEIGHT)
    if bar:
        draw_orientation_bar(draw, SHEET_WIDTH, SHEET_HEIGHT)
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


def boxes_in_right_place(photo: Image.Image) -> int:
    """How many of the sheet's boxes hold the same ink as the upright original."""
    def crops(img):
        sheet, _ = straighten(img)
        return crop_glyphs(sheet.point(lambda p: 0 if p < 128 else 255))
    want, got = crops(filled_sheet()), crops(photo)

    def overlap(a, b):
        a, b = np.array(a) < 128, np.array(b) < 128
        return (a & b).sum() / max(1, (a | b).sum())
    return sum(1 for c in char_grid() if overlap(want[c], got[c]) > 0.4)


def test_rotated_sheets_are_straightened():
    for degrees in (0, 90, 180, 270):
        photo = filled_sheet().rotate(degrees, expand=True)
        assert boxes_in_right_place(photo) >= 55, f"rotated {degrees} degrees"
        uid = make_id(encode(photo))
        r = client.post(f"/generate/{uid}")
        assert r.status_code == 200 and r.json()["warnings"] == [], degrees


def test_phone_photo_with_rotate_flag():
    exif = Image.Exif()
    exif[0x0112] = 6  # "turn me 90 degrees clockwise to display upright", pixels stored sideways
    uid = make_id(encode(filled_sheet().rotate(90, expand=True).convert("RGB"), "JPEG", exif=exif.tobytes()))
    with Image.open(f"uploads/{uid}.img") as stored:  # closed before /generate deletes it (Windows won't delete an open file)
        assert stored.width < stored.height, "the rotate flag must be applied at upload"
    assert client.post(f"/generate/{uid}").json()["warnings"] == []


def test_sheet_without_orientation_bar_still_accepted_with_warning():
    uid = make_id(encode(filled_sheet(bar=False)))
    r = client.post(f"/generate/{uid}")
    assert r.status_code == 200 and "orientation" in r.json()["warnings"][0]


def detail(photo: Image.Image) -> str:
    uid = make_id(encode(photo))
    r = client.post(f"/generate/{uid}")
    assert r.status_code == 400, r.text
    return r.json()["detail"]


def test_messages_name_the_corner_at_fault():
    boxes = corner_marker_boxes(SHEET_WIDTH, SHEET_HEIGHT)

    one = filled_sheet()
    ImageDraw.Draw(one).rectangle(boxes["bottom_right"], fill=255)
    assert "bottom-right corner square." in detail(one)

    two = filled_sheet()
    for name in ("top_left", "bottom_left"):
        ImageDraw.Draw(two).rectangle(boxes[name], fill=255)
    assert "top-left and bottom-left corner squares" in detail(two)

    crowded = filled_sheet()
    ImageDraw.Draw(crowded).rectangle([75, 22, 105, 52], fill=0)  # a dark blob next to the top-left square
    assert "very near the top-left corner square" in detail(crowded)

    assert "No corner squares found" in detail(Image.effect_noise((1240, 1754), 80))


def test_handwriting_in_corner_box_accepted():
    sheet = filled_sheet()
    ImageDraw.Draw(sheet).rectangle([90, 120, 130, 160], fill=0)
    markers = find_corner_markers(sheet)
    assert len(markers) == 4 and "top_left" in markers


def test_collinear_perspective_raises_bad_sheet():
    source = [(0, 0), (10, 10), (20, 20), (30, 30)]
    target = [(0, 0), (100, 0), (100, 100), (0, 100)]
    try:
        _solve_perspective_coeffs(source, target)
        assert False, "collinear points must raise BadSheetShape"
    except BadSheetShape as e:
        assert "perspective" in str(e).lower()


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


def test_proportional_metrics():
    sheet = filled_sheet()
    crops = crop_glyphs(sheet)
    entries = {}
    for char in ("া", "ক", "ঋ"):
        g = crops[char]
        entries[char] = {
            "path": trace_glyph(g),
            "crop_height": g.height,
            "crop_width": g.width,
            "bbox": glyph_ink_bbox(g),
        }
    font_path = Path("proportional_test.otf")
    build_font(entries, units_per_em=1000, family_name="Hatekhori Bangla").save(str(font_path))
    tf = TTFont(str(font_path))
    hmtx = tf["hmtx"]
    cmap = tf["cmap"].getBestCmap()
    w_matra = hmtx[cmap[ord("া")]][0]
    w_ka = hmtx[cmap[ord("ক")]][0]
    w_ri = hmtx[cmap[ord("ঋ")]][0]
    assert w_matra < w_ka, f"expected matra ({w_matra}) to be narrower than 'ক' ({w_ka})"
    font_path.unlink(missing_ok=True)


def test_opencv_cleanup_and_ttf_export():
    orig = np.array(filled_sheet(), dtype=float)
    h, w = orig.shape
    shadowed = np.clip(orig * (np.linspace(80, 240, h)[:, None] / 240.0), 0, 255).astype(np.uint8)
    cleaned = binarize_sheet(Image.fromarray(shadowed, mode="L"))
    crops = crop_glyphs(cleaned)
    assert sum(1 for g in crops.values() if glyph_ink_bbox(g) is not None) >= 55

    ttf_path = Path("test_out.ttf")
    entries = {
        "ক": {
            "path": trace_glyph(crops["ক"]),
            "crop_height": crops["ক"].height,
            "crop_width": crops["ক"].width,
            "bbox": glyph_ink_bbox(crops["ক"]),
        }
    }
    build_font(entries, is_ttf=True).save(str(ttf_path))
    tf = TTFont(str(ttf_path))
    assert "glyf" in tf, "TrueType font must include glyf table"
    ttf_path.unlink(missing_ok=True)


def test_cleanup_quota_and_lru():
    sweep_dir = Path(tempfile.mkdtemp())
    f1 = sweep_dir / "oldest.txt"
    f2 = sweep_dir / "middle.txt"
    f3 = sweep_dir / "newest.txt"

    f1.write_bytes(b"a" * 100)
    f2.write_bytes(b"b" * 100)
    f3.write_bytes(b"c" * 100)

    now = time.time()
    os.utime(f1, (now - 200, now - 200))
    os.utime(f2, (now - 100, now - 100))
    os.utime(f3, (now, now))

    # Age sweep: max_age 150s removes f1 (200s old)
    sweep(sweep_dir, max_age_s=150)
    assert not f1.exists(), "oldest file beyond max_age must be deleted"
    assert f2.exists() and f3.exists(), "newer files must survive age cutoff"

    # Count quota: max_files=1 evicts f2 (oldest survivor), keeping only f3
    sweep(sweep_dir, max_age_s=1000, max_files=1)
    assert not f2.exists(), "oldest surviving file must be evicted by max_files cap"
    assert f3.exists()

    # Byte quota: write 2 files of 80 bytes; with max_bytes=100, oldest is evicted
    f4 = sweep_dir / "byte_old.txt"
    f5 = sweep_dir / "byte_new.txt"
    f4.write_bytes(b"x" * 80)
    f5.write_bytes(b"y" * 80)
    os.utime(f4, (now + 10, now + 10))
    os.utime(f5, (now + 20, now + 20))
    sweep(sweep_dir, max_age_s=1000, max_bytes=100)
    assert not f4.exists(), "oldest file must be evicted to satisfy max_bytes cap"
    assert f5.exists()


def test_guideline_sheet_cached():
    b1_bn = _get_guideline_sheet_bytes("bn")
    b2_bn = _get_guideline_sheet_bytes("bn")
    assert b1_bn.startswith(b"\x89PNG\r\n\x1a\n"), "must be valid PNG bytes"
    assert b1_bn is b2_bn, "bengali sheet bytes must be cached in memory"

    b1_en = _get_guideline_sheet_bytes("en")
    b2_en = _get_guideline_sheet_bytes("en")
    assert b1_en.startswith(b"\x89PNG\r\n\x1a\n"), "must be valid PNG bytes"
    assert b1_en is b2_en, "english sheet bytes must be cached in memory"
    assert b1_bn != b1_en, "bengali and english sheets must differ"


def test_generate_semaphore():
    assert _GENERATE_SEMAPHORE.acquire(blocking=False)
    assert _GENERATE_SEMAPHORE.acquire(blocking=False)
    assert not _GENERATE_SEMAPHORE.acquire(blocking=False)
    _GENERATE_SEMAPHORE.release()
    _GENERATE_SEMAPHORE.release()


def test_transparent_png_handled():
    sheet = filled_sheet().convert("RGBA")
    data = np.array(sheet)
    data[:10, :, 3] = 0  # top 10px transparent
    rgba = Image.fromarray(data, mode="RGBA")
    markers = find_corner_markers(rgba)
    assert len(markers) == 4, "transparent margins must not block corner detection"


def test_windows_permission_error_in_sweep():
    sweep_dir = Path(tempfile.mkdtemp())
    locked = sweep_dir / "locked.txt"
    unlocked = sweep_dir / "unlocked.txt"
    locked.write_bytes(b"locked")
    unlocked.write_bytes(b"unlocked")
    now = time.time()
    os.utime(locked, (now - 200, now - 200))
    os.utime(unlocked, (now - 200, now - 200))

    with open(locked, "rb"):
        sweep(sweep_dir, max_age_s=100)
    assert not unlocked.exists(), "unlocked file must be unlinked even if another file is locked"


def test_truetype_hmtx_lsb_matches_glyf_xmin():
    crops = crop_glyphs(filled_sheet())
    entries = {
        "ক": {
            "path": trace_glyph(crops["ক"]),
            "crop_height": crops["ক"].height,
            "crop_width": crops["ক"].width,
            "bbox": glyph_ink_bbox(crops["ক"]),
        }
    }
    ttf_path = Path("lsb_test.ttf")
    build_font(entries, is_ttf=True).save(str(ttf_path))
    tf = TTFont(str(ttf_path))
    hmtx = tf["hmtx"]
    cmap = tf["cmap"].getBestCmap()
    glyph_name = cmap[ord("ক")]
    hmtx_lsb = hmtx[glyph_name][1]
    glyf_xmin = tf["glyf"][glyph_name].xMin
    assert abs(hmtx_lsb - glyf_xmin) <= 1, f"hmtx LSB ({hmtx_lsb}) must match glyf xMin ({glyf_xmin})"
    ttf_path.unlink(missing_ok=True)


def test_bengali_primary_alphabet_and_matras():
    chars = char_grid()
    assert len(chars) == 60, f"expected 60 Bengali characters, got {len(chars)}"

    # 11 স্বরবর্ণ
    vowels = ["অ", "আ", "ই", "ঈ", "উ", "ঊ", "ঋ", "এ", "ঐ", "ও", "ঔ"]
    for v in vowels:
        assert v in chars, f"missing vowel {v}"

    # 39 ব্যঞ্জনবর্ণ
    consonants = [
        "ক", "খ", "গ", "ঘ", "ঙ", "চ", "ছ", "জ", "ঝ", "ঞ",
        "ট", "ঠ", "ড", "ঢ", "ণ", "ত", "থ", "দ", "ধ", "ন",
        "প", "ফ", "ব", "ভ", "ম", "য", "র", "ল", "শ", "ষ",
        "স", "হ", "ড়", "ঢ়", "য়", "ৎ", "ং", "ঃ", "ঁ"
    ]
    for c in consonants:
        assert c in chars, f"missing consonant {c}"

    # 10 কারচিহ্ন
    matras = ["া", "ি", "ী", "ু", "ূ", "ৃ", "ে", "ৈ", "ো", "ৌ"]
    for m in matras:
        assert m in chars, f"missing matra {m}"

    # Verify font compiler produces valid cmap for all 60 characters
    entries = {
        c: {
            "path": None,
            "crop_height": 140,
            "crop_width": 175,
            "bbox": (10, 10, 100, 100),
        }
        for c in chars
    }
    font_path = Path("bn_full_test.otf")
    build_font(entries, family_name="Hatekhori Bangla").save(str(font_path))
    tf = TTFont(str(font_path))
    cmap = tf["cmap"].getBestCmap()
    for c in chars:
        assert ord(c) in cmap, f"character {c} (U+{ord(c):04X}) must be in cmap"
    assert ord(" ") in cmap, "space must be in cmap"
    font_path.unlink(missing_ok=True)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
