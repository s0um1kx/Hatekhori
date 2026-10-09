"""Count conjunct frequency in a plain-text corpus, to scope the glyph set
by measurement instead of by an unsourced coverage claim.

A "conjunct" here is the Unicode sequence  C (virama C)+  — two or more
consonants joined by a virama (hasanta in Bengali). Counting is by
OCCURRENCE in running text (not unique words), because the question we
care about is: "if the font draws these N conjuncts properly, what share
of conjuncts a reader actually meets will render as a true conjunct?"

Everything not captured degrades gracefully to separate letters with a
visible virama (see gsub_spike.py), so coverage is a dial, not a cliff.

Usage (from backend/):
    python experiments/conjunct_counter.py corpus.txt --script bengali
    python experiments/conjunct_counter.py corpus.txt --script devanagari --csv out/hindi.csv

Use text from SEVERAL sources. A corpus from one outlet or one subject
skews which conjuncts look common.

The category split (reph / ra-phala / ya-phala / other) is an
approximate grouping for scoping, not a statement of typographic rules.
"""

import argparse
import csv
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

SCRIPTS = {
    "bengali": {
        "consonants": "\u0995-\u09B9\u09DC\u09DD\u09DF",
        "virama": "\u09CD",
        "nukta": "\u09BC",
        "ra": "\u09B0",
        "ya": "\u09AF",
    },
    "devanagari": {
        "consonants": "\u0915-\u0939\u0958-\u095F",
        "virama": "\u094D",
        "nukta": "\u093C",
        "ra": "\u0930",
        "ya": "\u092F",
    },
}

COVERAGE_POINTS = [10, 25, 50, 100, 150, 200, 300]


def _patterns(cfg: dict):
    unit = f"[{cfg['consonants']}]{cfg['nukta']}?"
    conjunct = re.compile(f"{unit}(?:{cfg['virama']}{unit})+")
    return re.compile(unit), conjunct


def count_conjuncts(text: str, script: str) -> Counter:
    cfg = SCRIPTS[script]
    _, conjunct_re = _patterns(cfg)
    # NFC splits letters like ড় into base + nukta; the patterns allow an
    # optional nukta, so the same letter is never counted two ways.
    text = unicodedata.normalize("NFC", text)
    return Counter(conjunct_re.findall(text))


def categorize(seq: str, script: str) -> str:
    cfg = SCRIPTS[script]
    unit_re, _ = _patterns(cfg)
    units = unit_re.findall(seq)
    first, last = units[0], units[-1]
    if first == cfg["ra"]:
        return "reph"
    if last == cfg["ra"]:
        return "ra-phala"
    if last == cfg["ya"]:
        return "ya-phala"
    return "other"


def codepoints(seq: str) -> str:
    return " ".join(f"U+{ord(c):04X}" for c in seq)


def report(counter: Counter, script: str, csv_path: Path | None) -> None:
    total = sum(counter.values())
    if total == 0:
        print("No conjuncts found — is this the right --script for this text?")
        return

    ranked = counter.most_common()
    by_cat = Counter()
    distinct_by_cat = Counter()
    for seq, n in ranked:
        cat = categorize(seq, script)
        by_cat[cat] += n
        distinct_by_cat[cat] += 1

    print(f"Total conjunct occurrences: {total:,}   distinct: {len(ranked):,}\n")
    print("By category (approximate grouping):")
    for cat in ("reph", "ra-phala", "ya-phala", "other"):
        share = by_cat[cat] / total * 100
        print(f"  {cat:9} {by_cat[cat]:>9,} occurrences ({share:5.1f}%)   {distinct_by_cat[cat]:>4} distinct")

    print("\nCoverage if the top-N distinct conjuncts are drawn as true conjuncts:")
    running, idx = 0, 0
    for n_target in COVERAGE_POINTS:
        if n_target > len(ranked):
            break
        while idx < n_target:
            running += ranked[idx][1]
            idx += 1
        print(f"  top {n_target:>3}: {running / total * 100:5.1f}% of conjunct occurrences")

    print("\nTop 30:")
    running = 0
    for rank, (seq, n) in enumerate(ranked[:30], start=1):
        running += n
        print(f"  {rank:>3}. {seq}  {n:>8,}  {n / total * 100:5.2f}%  cum {running / total * 100:5.1f}%  [{categorize(seq, script)}]  {codepoints(seq)}")

    if csv_path:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["rank", "conjunct", "codepoints", "count", "share_pct", "cumulative_pct", "category"])
            running = 0
            for rank, (seq, n) in enumerate(ranked, start=1):
                running += n
                w.writerow([rank, seq, codepoints(seq), n, f"{n / total * 100:.4f}", f"{running / total * 100:.2f}", categorize(seq, script)])
        print(f"\nFull ranked list written to {csv_path}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("corpus", type=Path, help="UTF-8 plain-text file")
    parser.add_argument("--script", choices=sorted(SCRIPTS), default="bengali")
    parser.add_argument("--csv", type=Path, default=None, help="write the full ranked list here")
    args = parser.parse_args()

    text = args.corpus.read_text(encoding="utf-8", errors="ignore")
    report(count_conjuncts(text, args.script), args.script, args.csv)


if __name__ == "__main__":
    main()
