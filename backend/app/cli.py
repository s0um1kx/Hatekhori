"""Command-line entrypoint for the Milestone 1 pipeline.

Runs ingest -> preprocess -> segment -> vectorize -> metrics -> compile
on a single image file, instead of five separate API calls through
Swagger UI. This part (8a) wires ingest + preprocess; 8b adds the rest
and prints a final summary.

Usage:
    python -m app.cli path/to/photo.jpg
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image

from pipeline.ingest import save_upload
from pipeline.preprocess import run_preprocess

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


if __name__ == "__main__":
    main()
