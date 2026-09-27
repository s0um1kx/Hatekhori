"""Generate the printable guideline sheet.

Usage:
    python -m app.make_sheet [output_path]

Defaults to backend/guideline_sheet.png if no path is given.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.sheet import generate_guideline_sheet


def main() -> None:
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("guideline_sheet.png")

    img = generate_guideline_sheet()
    img.save(output_path, format="PNG")

    print(f"Guideline sheet saved -> {output_path}")
    print("Print at 100% scale / 'Actual size' — NOT 'Fit to page' — on A4 paper.")
    print("Fit-to-page scaling would shift the grid off what the pipeline expects.")


if __name__ == "__main__":
    main()
