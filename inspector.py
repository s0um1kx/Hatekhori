"""Interactive proof sheet and kill-test inspection harness for Hatekhori.

Generates a standalone, dependency-free HTML inspection report adhering to:
- Locked brand palette: #F2ECE1 (stage), #0034D3 (ink primary), #003087 (ink deep), #99CCFF (tint).
- AGENTS.md §5: Fixed Human / Machine toggle control.
  - Human mode: natural specimen text, editorial mockups, live typing at 16/24/48/72px.
  - Machine mode: raw vector paths, Bézier control points, and guideline overlays.
"""

from __future__ import annotations

import os
import base64
import json
from typing import List, Dict, Any, Tuple

try:
    from vectorize import VectorizedGlyph
    from metrics import GlyphMetrics
except ImportError:
    from .vectorize import VectorizedGlyph
    from .metrics import GlyphMetrics


def _encode_font_base64(ttf_path: str) -> str:
    """Read a TTF file and return base64 data URI."""
    with open(ttf_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:font/ttf;base64,{b64}"


def generate_proof_sheet(
    sample_reports: List[Dict[str, Any]],
    output_html_path: str = "proof_sheet.html",
) -> str:
    """Generate the interactive HTML proof sheet for human review.

    Args:
        sample_reports: List of dicts with keys:
            - 'id': str
            - 'title': str
            - 'description': str
            - 'ttf_path': str
            - 'vectorized_glyphs': Dict[str, VectorizedGlyph]
            - 'metrics_map': Dict[str, GlyphMetrics]
            - 'kerning_count': int
        output_html_path: Path to write the output HTML file

    Returns:
        output_html_path
    """
    # Build per-sample font-face CSS and glyph data
    font_faces_css = []
    samples_data = []

    for idx, report in enumerate(sample_reports):
        font_id = f"HatekhoriTest_{report['id']}"
        ttf_data_uri = _encode_font_base64(report["ttf_path"])

        font_faces_css.append(f"""
        @font-face {{
            font-family: '{font_id}';
            src: url('{ttf_data_uri}') format('truetype');
            font-weight: normal;
            font-style: normal;
        }}
        """)

        # Extract SVG paths for Machine mode
        glyphs_svg = []
        chars_order = sorted(list(report["vectorized_glyphs"].keys()))
        for char in chars_order:
            vg: VectorizedGlyph = report["vectorized_glyphs"][char]
            metric: GlyphMetrics = report["metrics_map"].get(char)
            if vg.is_empty:
                continue

            # In font coordinates (1000 UPM):
            # Viewbox: x from -50 to 1050, y from -300 to 900 (total height 1200)
            # In SVG, y is downward, so SVG Y = 900 - font_y
            lsb = metric.lsb if metric else 50
            adv = metric.advance_width if metric else 600

            paths_d = []
            for contour in vg.contours:
                d = contour.to_svg_path(offset_x=lsb, offset_y=0.0, flip_y=True, view_h=900.0)
                paths_d.append(d)

            glyphs_svg.append({
                "char": char,
                "svg_d": " ".join(paths_d),
                "lsb": lsb,
                "advance": adv,
                "width": metric.width if metric else int(vg.width),
                "min_y": metric.min_y if metric else int(vg.min_y),
                "max_y": metric.max_y if metric else int(vg.max_y),
                "baseline_svg_y": 900.0,            # y = 0
                "x_height_svg_y": 900.0 - 500.0,    # y = 500 -> 400
                "cap_height_svg_y": 900.0 - 700.0,  # y = 700 -> 200
                "ascender_svg_y": 900.0 - 800.0,    # y = 800 -> 100
                "descender_svg_y": 900.0 - (-200.0),# y = -200 -> 1100
            })

        samples_data.append({
            "id": report["id"],
            "fontFamily": font_id,
            "title": report["title"],
            "description": report["description"],
            "ttfName": os.path.basename(report["ttf_path"]),
            "glyphCount": len([g for g in report["vectorized_glyphs"].values() if not g.is_empty]),
            "kerningCount": report.get("kerning_count", 0),
            "glyphs": glyphs_svg,
        })

    samples_json = json.dumps(samples_data)
    font_css = "\n".join(font_faces_css)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hatekhori — Milestone 1 Pipeline Kill-Test Proof Sheet</title>
    <style>
        {font_css}

        :root {{
            --stage: #F2ECE1;
            --ink-primary: #0034D3;
            --ink-deep: #003087;
            --tint: #99CCFF;
            --tint-quiet: rgba(153, 204, 255, 0.25);
            --line-subtle: rgba(0, 52, 211, 0.2);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--stage);
            color: var(--ink-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
            min-height: 100vh;
            padding: 0;
            margin: 0;
            display: flex;
            flex-direction: column;
        }}

        /* Header bar */
        header {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: var(--stage);
            border-bottom: 1px solid var(--line-subtle);
            padding: 16px 48px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .brand-title {{
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.5px;
            color: var(--ink-deep);
            display: flex;
            align-items: baseline;
            gap: 12px;
        }}

        .brand-tag {{
            font-size: 13px;
            font-weight: 500;
            color: var(--ink-primary);
            opacity: 0.8;
            letter-spacing: 0.5px;
        }}

        /* Human / Machine Toggle */
        .toggle-container {{
            display: flex;
            align-items: center;
            border: 1px solid var(--ink-primary);
            border-radius: 4px;
            overflow: hidden;
            background: var(--stage);
        }}

        .toggle-btn {{
            background: transparent;
            border: none;
            padding: 8px 20px;
            font-size: 14px;
            font-weight: 600;
            color: var(--ink-primary);
            cursor: pointer;
            transition: all 0.15s ease;
        }}

        .toggle-btn.active {{
            background: var(--ink-primary);
            color: var(--stage);
        }}

        .toggle-btn:not(.active):hover {{
            background: var(--tint-quiet);
        }}

        /* Main layout */
        main {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 32px 48px 64px 48px;
            width: 100%;
        }}

        /* Sample selector tabs */
        .tabs-row {{
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            border-bottom: 1px solid var(--line-subtle);
            padding-bottom: 12px;
            overflow-x: auto;
        }}

        .tab-btn {{
            background: transparent;
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 600;
            color: var(--ink-primary);
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.15s ease;
        }}

        .tab-btn:hover {{
            background: var(--tint-quiet);
        }}

        .tab-btn.active {{
            border-color: var(--ink-primary);
            background: var(--tint);
            color: var(--ink-deep);
        }}

        /* Sample metadata banner */
        .sample-meta {{
            padding: 16px 20px;
            border: 1px solid var(--line-subtle);
            border-radius: 4px;
            margin-bottom: 32px;
            background: rgba(255, 255, 255, 0.4);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .sample-title {{
            font-size: 18px;
            font-weight: 700;
            color: var(--ink-deep);
            margin-bottom: 4px;
        }}

        .sample-desc {{
            font-size: 14px;
            opacity: 0.85;
        }}

        .meta-stats {{
            display: flex;
            gap: 24px;
            text-align: right;
            font-size: 13px;
        }}

        .stat-val {{
            font-weight: 700;
            font-size: 16px;
            color: var(--ink-deep);
        }}

        /* Human View */
        .human-view {{
            display: flex;
            flex-direction: column;
            gap: 32px;
        }}

        .specimen-card {{
            border: 1px solid var(--line-subtle);
            padding: 24px;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.4);
        }}

        .card-label {{
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: var(--ink-deep);
            opacity: 0.7;
            margin-bottom: 12px;
            border-bottom: 1px solid var(--line-subtle);
            padding-bottom: 4px;
        }}

        .size-row {{
            margin-bottom: 24px;
        }}

        .size-label {{
            font-size: 12px;
            opacity: 0.6;
            margin-bottom: 4px;
            font-family: monospace;
        }}

        .specimen-text {{
            line-height: 1.3;
            word-break: break-word;
        }}

        .text-72 {{ font-size: 72px; }}
        .text-48 {{ font-size: 48px; }}
        .text-24 {{ font-size: 24px; }}
        .text-16 {{ font-size: 16px; line-height: 1.5; }}

        /* Interactive typing box */
        .interactive-box {{
            width: 100%;
            min-height: 120px;
            background: transparent;
            border: 1px dashed var(--ink-primary);
            border-radius: 4px;
            padding: 16px;
            font-size: 28px;
            color: var(--ink-primary);
            outline: none;
            resize: vertical;
        }}

        /* Machine View */
        .machine-view {{
            display: none;
            flex-direction: column;
            gap: 24px;
        }}

        .machine-legend {{
            display: flex;
            gap: 24px;
            font-size: 13px;
            padding: 12px 16px;
            border: 1px solid var(--line-subtle);
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.4);
            align-items: center;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .legend-color {{
            width: 16px;
            height: 3px;
            border-radius: 2px;
        }}

        .glyph-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
            gap: 12px;
        }}

        .glyph-cell {{
            border: 1px solid var(--line-subtle);
            border-radius: 4px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.6);
            display: flex;
            flex-direction: column;
            align-items: center;
            transition: all 0.15s ease;
        }}

        .glyph-cell:hover {{
            border-color: var(--ink-primary);
            background: #fff;
        }}

        .cell-char-label {{
            font-size: 12px;
            font-weight: 700;
            color: var(--ink-deep);
            align-self: flex-start;
            margin-bottom: 4px;
        }}

        .glyph-svg-wrap {{
            width: 110px;
            height: 130px;
        }}

        .glyph-meta-text {{
            font-size: 10px;
            color: var(--ink-deep);
            opacity: 0.7;
            font-family: monospace;
            margin-top: 6px;
            align-self: flex-start;
        }}

        /* Kill-test rubric banner */
        .rubric-card {{
            border: 1px solid var(--ink-deep);
            border-radius: 4px;
            padding: 20px;
            background: rgba(153, 204, 255, 0.15);
            margin-top: 48px;
        }}

        .rubric-title {{
            font-size: 15px;
            font-weight: 700;
            color: var(--ink-deep);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .rubric-list {{
            font-size: 14px;
            line-height: 1.6;
            padding-left: 20px;
        }}

        .rubric-list li {{
            margin-bottom: 4px;
        }}
    </style>
</head>
<body>
    <header>
        <div class="brand-title">
            Hatekhori (হাতে খড়ি)
            <span class="brand-tag">Milestone 1 — Pipeline Kill-Test Proof Sheet</span>
        </div>
        <div class="toggle-container">
            <button id="btnHuman" class="toggle-btn active" onclick="setMode('human')">Human</button>
            <button id="btnMachine" class="toggle-btn" onclick="setMode('machine')">Machine</button>
        </div>
    </header>

    <main>
        <!-- Sample selector tabs -->
        <div class="tabs-row" id="tabsRow"></div>

        <!-- Sample metadata -->
        <div class="sample-meta" id="sampleMeta">
            <div>
                <div class="sample-title" id="sampleTitle"></div>
                <div class="sample-desc" id="sampleDesc"></div>
            </div>
            <div class="meta-stats">
                <div>
                    <div class="stat-val" id="statGlyphs">0</div>
                    <div>Glyphs Extracted</div>
                </div>
                <div>
                    <div class="stat-val" id="statKern">0</div>
                    <div>Kerning Pairs</div>
                </div>
                <div>
                    <div class="stat-val" id="statFile">0</div>
                    <div>Output File</div>
                </div>
            </div>
        </div>

        <!-- Human View -->
        <div class="human-view" id="humanView">
            <div class="specimen-card">
                <div class="card-label">Interactive Specimen Tester (Type your own text)</div>
                <textarea id="interactiveText" class="interactive-box" rows="2" placeholder="Type here to test kerning and baseline harmony...">The quick brown fox jumps over the lazy dog. 0123456789 ?!</textarea>
            </div>

            <div class="specimen-card">
                <div class="card-label">Scale & Hierarchy Test (16px, 24px, 48px, 72px)</div>
                
                <div class="size-row">
                    <div class="size-label">72px — Headline Scale</div>
                    <div class="specimen-text text-72 current-font">Hatekhori 2026</div>
                </div>

                <div class="size-row">
                    <div class="size-label">48px — Pangram Inspection</div>
                    <div class="specimen-text text-48 current-font">Pack my box with five dozen liquor jugs.</div>
                </div>

                <div class="size-row">
                    <div class="size-label">24px — Subhead / Sentence Reading</div>
                    <div class="specimen-text text-24 current-font">A quick movement of the pencil reveals honest handwriting without robotic uniformity. All uppercase characters ABCDEFGHIJKLMNOPQRSTUVWXYZ and lowercase abcdefghijklmnopqrstuvwxyz stand alongside 0123456789.</div>
                </div>

                <div class="size-row">
                    <div class="size-label">16px — Body Text Legibility (Kill-Test Threshold)</div>
                    <div class="specimen-text text-16 current-font">This test answers the decisive question of Milestone 1: does the font read harmoniously at standard text size, or does baseline bounce, jagged contours, or erratic spacing degrade it into a ransom note? A true atelier preserves the human stroke while honoring typographic rhythm.</div>
                </div>
            </div>
        </div>

        <!-- Machine View -->
        <div class="machine-view" id="machineView">
            <div class="machine-legend">
                <strong style="color: var(--ink-deep);">Guideline System:</strong>
                <div class="legend-item"><div class="legend-color" style="background: #003087;"></div> Baseline (y = 0)</div>
                <div class="legend-item"><div class="legend-color" style="background: #99CCFF;"></div> x-Height (y = 500)</div>
                <div class="legend-item"><div class="legend-color" style="background: #0034D3;"></div> Cap-Height (y = 700)</div>
                <div class="legend-item"><div class="legend-color" style="background: rgba(0, 52, 211, 0.4);"></div> Ascender / Descender (+800 / -200)</div>
            </div>

            <div class="glyph-grid" id="glyphGrid"></div>
        </div>

        <!-- Kill-test Verdict Rubric Notice -->
        <div class="rubric-card">
            <div class="rubric-title">Milestone 1 Kill-Test Decision Rubric</div>
            <ul class="rubric-list">
                <li><strong>Baseline Stability:</strong> Do characters sit evenly on the virtual line, or do letters bounce unpredictably?</li>
                <li><strong>Scale Proportions:</strong> Are lowercase letters (e.g. 'e', 'o') proportionally sized relative to ascenders ('b', 'd') and capitals?</li>
                <li><strong>Descender Depth:</strong> Do letters with descenders ('g', 'p', 'y', 'q', 'j') extend naturally below the baseline?</li>
                <li><strong>Contour Smoothness:</strong> Are Bézier curves natural and continuous, or pixelated and stepped?</li>
                <li><strong>Spacing & Harmony:</strong> Is letter rhythm legible and pleasing across sentences and paragraphs?</li>
            </ul>
        </div>
    </main>

    <script>
        const samples = {samples_json};
        let currentSampleIdx = 0;
        let currentMode = 'human';

        function init() {{
            renderTabs();
            selectSample(0);
        }}

        function setMode(mode) {{
            currentMode = mode;
            document.getElementById('btnHuman').classList.toggle('active', mode === 'human');
            document.getElementById('btnMachine').classList.toggle('active', mode === 'machine');

            document.getElementById('humanView').style.display = mode === 'human' ? 'flex' : 'none';
            document.getElementById('machineView').style.display = mode === 'machine' ? 'flex' : 'none';
        }}

        function renderTabs() {{
            const tabsRow = document.getElementById('tabsRow');
            tabsRow.innerHTML = '';
            samples.forEach((sample, i) => {{
                const btn = document.createElement('button');
                btn.className = 'tab-btn' + (i === 0 ? ' active' : '');
                btn.textContent = sample.title;
                btn.onclick = () => selectSample(i);
                tabsRow.appendChild(btn);
            }});
        }}

        function selectSample(idx) {{
            currentSampleIdx = idx;
            const sample = samples[idx];

            // Update tab button styles
            const tabBtns = document.querySelectorAll('.tab-btn');
            tabBtns.forEach((btn, i) => btn.classList.toggle('active', i === idx));

            // Update metadata
            document.getElementById('sampleTitle').textContent = sample.title;
            document.getElementById('sampleDesc').textContent = sample.description;
            document.getElementById('statGlyphs').textContent = sample.glyphCount;
            document.getElementById('statKern').textContent = sample.kerningCount;
            document.getElementById('statFile').textContent = sample.ttfName;

            // Update font family on specimen elements
            const fontEls = document.querySelectorAll('.current-font, #interactiveText');
            fontEls.forEach(el => {{
                el.style.fontFamily = `"${{sample.fontFamily}}", sans-serif`;
            }});

            // Render Machine glyph grid
            renderGlyphGrid(sample);
        }}

        function renderGlyphGrid(sample) {{
            const grid = document.getElementById('glyphGrid');
            grid.innerHTML = '';

            sample.glyphs.forEach(g => {{
                const cell = document.createElement('div');
                cell.className = 'glyph-cell';

                // SVG coordinates:
                // ViewBox: x from -40 to 1040 (width 1080), y from 0 to 1200
                const svgW = 1080;
                const svgH = 1200;

                const base_y = g.baseline_svg_y;
                const x_y = g.x_height_svg_y;
                const cap_y = g.cap_height_svg_y;
                const asc_y = g.ascender_svg_y;
                const desc_y = g.descender_svg_y;

                cell.innerHTML = `
                    <div class="cell-char-label">${{g.char}}</div>
                    <div class="glyph-svg-wrap">
                        <svg viewBox="-40 0 ${{svgW}} ${{svgH}}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
                            <!-- Guideline lines -->
                            <line x1="-40" y1="${{asc_y}}" x2="${{svgW}}" y2="${{asc_y}}" stroke="rgba(0, 52, 211, 0.3)" stroke-width="6" stroke-dasharray="8 8" />
                            <line x1="-40" y1="${{cap_y}}" x2="${{svgW}}" y2="${{cap_y}}" stroke="#0034D3" stroke-width="8" stroke-dasharray="10 10" />
                            <line x1="-40" y1="${{x_y}}" x2="${{svgW}}" y2="${{x_y}}" stroke="#99CCFF" stroke-width="8" stroke-dasharray="8 8" />
                            <line x1="-40" y1="${{base_y}}" x2="${{svgW}}" y2="${{base_y}}" stroke="#003087" stroke-width="12" />
                            <line x1="-40" y1="${{desc_y}}" x2="${{svgW}}" y2="${{desc_y}}" stroke="rgba(0, 52, 211, 0.3)" stroke-width="6" stroke-dasharray="8 8" />
                            
                            <!-- Advance width marker -->
                            <line x1="${{g.advance}}" y1="0" x2="${{g.advance}}" y2="${{svgH}}" stroke="rgba(0, 48, 135, 0.2)" stroke-width="6" />

                            <!-- Glyph Vector Outline -->
                            <path d="${{g.svg_d}}" fill="#0034D3" fill-rule="nonzero" opacity="0.9" />
                        </svg>
                    </div>
                    <div class="glyph-meta-text">Adv: ${{g.advance}} | LSB: ${{g.lsb}}</div>
                `;
                grid.appendChild(cell);
            }});
        }}

        window.onload = init;
    </script>
</body>
</html>
"""

    os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_html_path
