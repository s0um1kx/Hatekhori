"""Command-line interface and test runner for Hatekhori.

Milestone 1 Pipeline Kill-Test CLI:
- template: Generate blank guideline sheet
- process: Run end-to-end pipeline on any photo/scan to produce a .ttf
- test-batch: Generate 5 varied handwriting samples, run pipeline, and output interactive proof sheet
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Dict, Any, List

try:
    from template import generate_template_image
    from ingest import load_and_sanitize_image, IngestError
    from preprocess import preprocess_sheet, StructuralValidationError
    from segment import segment_cells
    from vectorize import vectorize_all_glyphs
    from metrics import compute_metrics_table
    from compiler import compile_font
    from test_batch import generate_all_samples
    from inspector import generate_proof_sheet
except ImportError:
    from .template import generate_template_image
    from .ingest import load_and_sanitize_image, IngestError
    from .preprocess import preprocess_sheet, StructuralValidationError
    from .segment import segment_cells
    from .vectorize import vectorize_all_glyphs
    from .metrics import compute_metrics_table
    from .compiler import compile_font
    from .test_batch import generate_all_samples
    from .inspector import generate_proof_sheet


def process_image(
    image_path: str,
    output_ttf_path: str,
    family_name: str = "Hatekhori Validation",
    provenance: str = "Hatekhori Atelier Milestone 1 Internal Validation",
) -> Dict[str, Any]:
    """Execute end-to-end handwriting-to-font pipeline on a single image."""
    t0 = time.time()

    # 1. Ingest & Guardrails (AGENTS.md §6)
    sanitized_img, meta = load_and_sanitize_image(image_path)

    # 2. Preprocess & Rectify
    rect_bgr, norm_gray, binary_ink = preprocess_sheet(sanitized_img)

    # 3. Segment Cells
    segmented_glyphs = segment_cells(binary_ink)

    # 4. Vectorize Outlines
    vectorized_glyphs = vectorize_all_glyphs(segmented_glyphs)

    # 5. Extract Metrics & Kerning
    metrics_map, kerning_pairs = compute_metrics_table(vectorized_glyphs)

    # 6. Compile TrueType Font
    compile_font(
        vectorized_glyphs,
        metrics_map,
        kerning_pairs,
        output_path=output_ttf_path,
        family_name=family_name,
        provenance_note=provenance,
    )

    elapsed = time.time() - t0
    non_empty = [g for g in vectorized_glyphs.values() if not g.is_empty]

    return {
        "output_ttf": output_ttf_path,
        "elapsed_seconds": elapsed,
        "total_glyphs": len(vectorized_glyphs),
        "extracted_glyphs": len(non_empty),
        "kerning_pairs_count": len(kerning_pairs),
        "vectorized_glyphs": vectorized_glyphs,
        "metrics_map": metrics_map,
        "kerning_pairs": kerning_pairs,
    }


def cmd_template(args: argparse.Namespace) -> None:
    output = args.output or "template_guideline_sheet.png"
    print(f"Generating guideline capture template -> {output}...")
    generate_template_image(output)
    print(f"Successfully saved guideline template to {output}")


def cmd_process(args: argparse.Namespace) -> None:
    input_path = args.input
    output_ttf = args.output or "output.ttf"
    family = args.family or "Hatekhori Validation"

    print(f"Processing handwriting sheet: {input_path}")
    try:
        res = process_image(input_path, output_ttf, family_name=family)
        print(f"Font successfully compiled to: {res['output_ttf']}")
        print(f"  - Extracted glyphs: {res['extracted_glyphs']} / {res['total_glyphs']}")
        print(f"  - Kerning pairs: {res['kerning_pairs_count']}")
        print(f"  - Processing time: {res['elapsed_seconds']:.2f}s")
    except IngestError as e:
        print(f"Ingest Error: {e.kind_reason}", file=sys.stderr)
        sys.exit(1)
    except StructuralValidationError as e:
        print(f"Validation Error: {e.kind_reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Pipeline Failure: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_test_batch(args: argparse.Namespace) -> None:
    batch_dir = args.output_dir or "test_batch_output"
    proof_path = args.proof or os.path.join(batch_dir, "proof_sheet.html")
    os.makedirs(batch_dir, exist_ok=True)

    print("=" * 70)
    print("HATEKHORI MILESTONE 1 — PIPELINE KILL-TEST SUITE")
    print("=" * 70)

    # 1. Generate 5 varied handwriting test images
    samples_dir = os.path.join(batch_dir, "samples")
    print("\n[Step 1/3] Synthesizing 5 varied test handwriting sheets...")
    sample_files = generate_all_samples(samples_dir)

    sample_meta = {
        "sample_1_gel_pen": {
            "title": "Sample 1: Crisp Gel Pen",
            "desc": "Thin, uniform strokes on clean paper under balanced lighting.",
        },
        "sample_2_fountain_pen": {
            "title": "Sample 2: Fountain Pen Bleed",
            "desc": "Rich blue ink with variable stroke pressure and paper feathering.",
        },
        "sample_3_phone_shadow": {
            "title": "Sample 3: Phone Shadow Gradient",
            "desc": "Harsh diagonal lighting shadow cast across sheet simulating mobile capture.",
        },
        "sample_4_perspective_tilt": {
            "title": "Sample 4: Table Perspective Tilt",
            "desc": "Photographed at a 10-degree tilt on a tabletop background requiring homography.",
        },
        "sample_5_casual_slant": {
            "title": "Sample 5: Casual Slant & Jitter",
            "desc": "Casual handwriting with natural cursive slant and baseline variation.",
        },
    }

    # 2. Run full pipeline on each sample
    print("\n[Step 2/3] Running end-to-end pipeline on all 5 samples...")
    reports = []
    summary_table = []

    for key, img_path in sample_files.items():
        meta = sample_meta[key]
        font_out = os.path.join(batch_dir, f"{key}.ttf")
        print(f"  -> Running pipeline on {meta['title']}...")

        t_start = time.time()
        res = process_image(
            img_path,
            font_out,
            family_name=f"Hatekhori {meta['title'].split(':')[1].strip()}",
        )
        t_elapsed = time.time() - t_start

        reports.append({
            "id": key,
            "title": meta["title"],
            "description": meta["desc"],
            "ttf_path": font_out,
            "vectorized_glyphs": res["vectorized_glyphs"],
            "metrics_map": res["metrics_map"],
            "kerning_count": res["kerning_pairs_count"],
        })

        summary_table.append((
            meta["title"],
            f"{res['extracted_glyphs']} / 64",
            f"{res['kerning_pairs_count']}",
            f"{t_elapsed:.2f}s",
            "OK",
        ))

    # 3. Generate interactive proof sheet
    print(f"\n[Step 3/3] Generating interactive HTML proof sheet -> {proof_path}...")
    generate_proof_sheet(reports, proof_path)

    # Print summary
    print("\n" + "=" * 70)
    print("BATCH RUN RESULTS SUMMARY")
    print("=" * 70)
    print(f"{'Sample Name':<35} | {'Glyphs':<10} | {'Kern Pairs':<12} | {'Time':<8} | {'Status'}")
    print("-" * 75)
    for row in summary_table:
        print(f"{row[0]:<35} | {row[1]:<10} | {row[2]:<12} | {row[3]:<8} | {row[4]}")
    print("=" * 75)
    print(f"\nInteractive Proof Sheet ready at:\n  file:///{os.path.abspath(proof_path).replace(os.sep, '/')}")
    print("\nOpen the HTML proof sheet in any browser to inspect the Human / Machine views")
    print("and evaluate the kill-test verdict.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Hatekhori — Handwriting-to-Font Pipeline Engine (Milestone 1)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Template generator
    tmpl_parser = subparsers.add_parser("template", help="Generate blank guideline capture sheet")
    tmpl_parser.add_argument("-o", "--output", help="Output image file path (PNG)")

    # Single image processor
    proc_parser = subparsers.add_parser("process", help="Process handwriting image to TTF font")
    proc_parser.add_argument("input", help="Input image path (JPG/PNG)")
    proc_parser.add_argument("-o", "--output", help="Output TTF file path")
    proc_parser.add_argument("-f", "--family", help="Font family name")

    # Batch test suite
    batch_parser = subparsers.add_parser("test-batch", help="Run varied 5-sample kill-test batch")
    batch_parser.add_argument("-d", "--output-dir", help="Output directory for generated fonts and samples")
    batch_parser.add_argument("-p", "--proof", help="Output HTML proof sheet path")

    args = parser.parse_args()

    if args.command == "template":
        cmd_template(args)
    elif args.command == "process":
        cmd_process(args)
    elif args.command == "test-batch":
        cmd_test_batch(args)


if __name__ == "__main__":
    main()
