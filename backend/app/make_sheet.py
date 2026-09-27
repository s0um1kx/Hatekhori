"""Generate the printable guideline sheet, or a synthetic filled-in
version for self-testing the pipeline without a printer.

Usage:
    python -m app.make_sheet [output_path]
    python -m app.make_sheet --synthetic [output_path]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.sheet import generate_guideline_sheet, generate_synthetic_filled_sheet


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_path", nargs="?", default=None)
    parser.add_argument(
        "--synthetic",
        action="store_true",
        help="Generate a filled-in test sheet (system font, not real handwriting) "
        "for self-testing the pipeline without a printer. Not a substitute for "
        "the real kill-test in PRD.md §9.",
    )
    args = parser.parse_args()

    if args.synthetic:
        default_name = "synthetic_filled_sheet.png"
        img = generate_synthetic_filled_sheet()
    else:
        default_name = "guideline_sheet.png"
        img = generate_guideline_sheet()

    output_path = Path(args.output_path) if args.output_path else Path(default_name)
    img.save(output_path, format="PNG")

    print(f"Saved -> {output_path}")
    if args.synthetic:
        print("This is a self-test aid, not the real kill-test (see PRD.md §9).")
        print(f"Run it through: python -m app.cli {output_path}")
    else:
        print("Print at 100% scale / 'Actual size' — NOT 'Fit to page' — on A4 paper.")
        print("Fit-to-page scaling would shift the grid off what the pipeline expects.")


if __name__ == "__main__":
    main()
