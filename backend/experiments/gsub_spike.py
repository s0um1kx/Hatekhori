"""Spike: can a font we build turn a Bengali conjunct into ONE glyph?

Why this exists: our compile step (pipeline/compile.py) produces a cmap
and glyph outlines, but no OpenType layout rules at all. For Bengali and
Devanagari that isn't enough: typing ক + ্ + ষ produces three separate
glyphs unless the font carries a GSUB rule that swaps the sequence for a
single conjunct glyph. Before designing a 100+ box guideline sheet around
conjuncts, this proves the mechanism works end to end, using throwaway
geometric placeholder glyphs instead of handwriting.

Run from backend/:
    python experiments/gsub_spike.py

Writes experiments/out/spike.otf and experiments/out/spike.html. Open the
HTML in Chrome: the "conjunct" rows should show ONE tall combined shape.
If uharfbuzz is installed, the shaping result is also checked right here.
"""

from pathlib import Path

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen

UPM = 1000
OUT_DIR = Path(__file__).parent / "out"

# Placeholder shapes, each a list of polygons. Real handwriting glyphs
# replace these later; the point here is only to tell them apart by eye.
SQUARE = [[(100, 0), (500, 0), (500, 400), (100, 400)]]
TRIANGLE = [[(100, 0), (500, 0), (300, 400)]]
DIAMOND = [[(300, 0), (500, 200), (300, 400), (100, 200)]]
DOT = [[(150, 0), (250, 0), (250, 100), (150, 100)]]
# Conjuncts are visibly different: stacked, taller shapes.
KA_SSA = [[(100, 0), (500, 0), (500, 300), (100, 300)], [(100, 300), (500, 300), (300, 700)]]
KA_TA = [[(100, 0), (500, 0), (500, 300), (100, 300)], [(300, 300), (500, 500), (300, 700), (100, 500)]]

# name -> (unicode codepoint or None, advance width, shape)
GLYPHS = {
    ".notdef": (None, 500, []),
    "space": (0x20, 300, []),
    "ka_bn": (0x0995, 600, SQUARE),
    "ssa_bn": (0x09B7, 600, TRIANGLE),
    "ta_bn": (0x09A4, 600, DIAMOND),
    "virama_bn": (0x09CD, 300, DOT),
    "ka_ssa_bn": (None, 600, KA_SSA),
    "ka_ta_bn": (None, 600, KA_TA),
}

FEATURES = """
languagesystem DFLT dflt;
languagesystem beng dflt;
languagesystem bng2 dflt;

# ক্ষ is an "akhand" conjunct in Bengali, so it belongs in akhn.
feature akhn {
    sub ka_bn virama_bn ssa_bn by ka_ssa_bn;
} akhn;

# Ordinary conjuncts go in cjct.
feature cjct {
    sub ka_bn virama_bn ta_bn by ka_ta_bn;
} cjct;
"""


def build() -> Path:
    glyph_order = list(GLYPHS)
    cmap = {cp: name for name, (cp, _, _) in GLYPHS.items() if cp is not None}

    charstrings = {}
    metrics = {}
    for name, (_, width, polygons) in GLYPHS.items():
        pen = T2CharStringPen(width, None)
        for poly in polygons:
            pen.moveTo(poly[0])
            for point in poly[1:]:
                pen.lineTo(point)
            pen.closePath()
        charstrings[name] = pen.getCharString()
        metrics[name] = (width, 0)

    fb = FontBuilder(UPM, isTTF=False)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupCFF("GsubSpike", {"FullName": "GSUB Spike"}, charstrings, {})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable(
        {
            "familyName": "GSUB Spike",
            "styleName": "Regular",
            "uniqueFontIdentifier": "Hatekhori:GsubSpike:1.0",
            "fullName": "GSUB Spike",
            "psName": "GsubSpike",
            "version": "Version 1.0",
        }
    )
    fb.setupOS2()
    fb.setupPost()

    addOpenTypeFeaturesFromString(fb.font, FEATURES)

    OUT_DIR.mkdir(exist_ok=True)
    font_path = OUT_DIR / "spike.otf"
    fb.save(str(font_path))
    return font_path


# (label, text, expected glyph names after shaping)
CASES = [
    ("conjunct ক্ষ  -> one glyph", "\u0995\u09CD\u09B7", ["ka_ssa_bn"]),
    ("conjunct ক্ত  -> one glyph", "\u0995\u09CD\u09A4", ["ka_ta_bn"]),
    ("no virama কষ  -> unchanged", "\u0995\u09B7", ["ka_bn", "ssa_bn"]),
    ("not provided ত্ষ -> fallback", "\u09A4\u09CD\u09B7", None),
    ("lone halant ক্ -> fallback", "\u0995\u09CD", None),
]


def verify(font_path: Path) -> None:
    try:
        import uharfbuzz as hb
    except ImportError:
        print("uharfbuzz not installed - skipping in-script check.")
        print("Open experiments/out/spike.html in Chrome to verify visually.")
        return

    hb_font = hb.Font(hb.Face(hb.Blob.from_file_path(str(font_path))))
    for label, text, expected in CASES:
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(hb_font, buf, {})
        names = [hb_font.glyph_to_string(i.codepoint) for i in buf.glyph_infos]
        if expected is None:
            print(f"INFO  {label}: {names}")
        else:
            status = "PASS" if names == expected else "FAIL"
            print(f"{status}  {label}: {names} (expected {expected})")


def write_html() -> None:
    rows = "\n".join(
        f'<tr><td>{label}</td><td class="t">{text}</td></tr>' for label, text, _ in CASES
    )
    html = f"""<!DOCTYPE html>
<meta charset="utf-8">
<title>GSUB spike</title>
<style>
@font-face {{ font-family: "GsubSpike"; src: url("spike.otf"); }}
body {{ font-family: sans-serif; padding: 24px; }}
td {{ padding: 8px 16px; border-bottom: 1px solid #ccc; }}
.t {{ font-family: "GsubSpike"; font-size: 96px; }}
</style>
<p>If conjunct shaping works, the first two rows show ONE tall combined shape
(not a square followed by a dot followed by another shape).</p>
<table>
{rows}
</table>
"""
    (OUT_DIR / "spike.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    path = build()
    write_html()
    print(f"Built {path}")
    verify(path)
