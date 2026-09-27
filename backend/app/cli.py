"""Command-line entrypoint for the Milestone 1 pipeline.

Runs ingest -> preprocess -> segment -> vectorize -> metrics -> compile
on a single image file, instead of five separate API calls through
Swagger UI.

Usage:
    python -m app.cli path/to/photo.jpg
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image

from pipeline.compile import build_font
from pipeline.ingest import save_upload
from pipeline.metrics import compute_global_metrics, glyph_ink_bbox, side_bearings
from pipeline.preprocess import run_preprocess
from pipeline.segment import char_grid, crop_glyphs
from pipeline.vectorize import path_to_svg, trace_glyph

OUTPUT_DIR = Path("output")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a photo through the Hatekhori M1 pipeline.")
    parser.add_argument("image_path", type=Path, help="Path to a photo of the guideline sheet")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)

    file_bytes = args.image_path.read_bytes()
    ingest_result = save_upload(file_bytes, args.image_path.name)
    upload_id = ingest_result["id"]
    print(f"[1/6] Ingested -> id={upload_id}")

    with Image.open(ingest_result["stored_path"]) as img:
        cleaned = run_preprocess(img)
        preprocessed_path = OUTPUT_DIR / f"{upload_id}_preprocessed.png"
        cleaned.save(preprocessed_path, format="PNG")
    print(f"[2/6] Preprocessed -> {preprocessed_path}")

    glyphs_dir = OUTPUT_DIR / upload_id / "glyphs"
    glyphs_dir.mkdir(parents=True, exist_ok=True)
    glyphs = crop_glyphs(cleaned)
    for index, char in enumerate(char_grid()):
        glyphs[char].save(glyphs_dir / f"{index:02d}_{char}.png", format="PNG")
    print(f"[3/6] Segmented -> {glyphs_dir} ({len(glyphs)} glyphs)")

    vectors_dir = OUTPUT_DIR / upload_id / "vectors"
    vectors_dir.mkdir(parents=True, exist_ok=True)
    glyph_entries = {}
    per_glyph_metrics = {}
    for index, char in enumerate(char_grid()):
        glyph_path = glyphs_dir / f"{index:02d}_{char}.png"
        with Image.open(glyph_path) as img:
            trace_path = trace_glyph(img)
            svg = path_to_svg(trace_path, img.width, img.height)
            (vectors_dir / f"{index:02d}_{char}.svg").write_text(svg, encoding="utf-8")

            bbox = glyph_ink_bbox(img)
            bearings = side_bearings(img, bbox)
            per_glyph_metrics[char] = {"bbox": bbox, "crop_height": img.height, **bearings}
            glyph_entries[char] = {
                "path": trace_path,
                "crop_height": img.height,
                "advance_width": bearings["advance_width"],
            }
    print(f"[4/6] Vectorized -> {vectors_dir}")

    global_metrics = compute_global_metrics(per_glyph_metrics)
    metrics_result = {"id": upload_id, "global": global_metrics, "glyphs": per_glyph_metrics}
    metrics_path = OUTPUT_DIR / upload_id / "metrics.json"
    metrics_path.write_text(json.dumps(metrics_result, indent=2), encoding="utf-8")
    print(f"[5/6] Metrics -> {metrics_path}")

    font_builder = build_font(glyph_entries, units_per_em=1000, family_name="Hatekhori Kill-Test")
    font_path = OUTPUT_DIR / upload_id / "font.otf"
    font_builder.save(str(font_path))
    print(f"[6/6] Compiled -> {font_path}")

    print()
    print(f"Done. Font: {font_path}")


if __name__ == "__main__":
    main()
