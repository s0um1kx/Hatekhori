# HATEKHORI: YOUR REAL HANDWRITING AS A FONT

A 20-second product launch film for **Hatekhori (হাতে খড়ি)** — the Indic-first digital typeface atelier and handwriting preservation engine. Built entirely in code with zero pre-rendered motion graphics or stock templates. A continuous, single-shape morphing composition where the tactile heritage of chalk on slate and pen on paper evolves into an installable, ownable OpenType (`.otf`) font for Bengali, Hindi, and English.

## Inputs
- **Product Name**: Hatekhori (হাতে খড়ি)
- **Brand Tokens**: 
  - Slate Dark Mode: `--bg: #0D0D0D`, `--fg: #F0F0F0`, `--muted: #888888`, `--border: #242424`, `--subtle: #141414`
  - Paper Light Mode: `--paper-bg: #FFFFFF`, `--ink: #111111`, `--paper-border: #E5E5E5`
  - Accent: High-contrast chalk white (`#F0F0F0`) and crimson alert (`#D2271B` / `#E03529`)
- **Typography**: `Instrument Serif` (editorial display), `DM Mono` (codepoint metadata & metrics), `Tiro Bangla` / `Hatekhori Bangla` (specimen).
- **Assets from Repository**:
  - Vector Brand Marks: `frontend/logo/logo-white.svg`, `frontend/logo/logo-symbol-white.svg`
  - Authentic Compiled Fonts: `frontend/hatekhori-bengali.otf`, `frontend/hatekhori-hindi.otf`, `frontend/hatekhori.otf`
  - Real Guideline Sheets: `frontend/guideline-sheet-bengali.png`, `frontend/guideline-sheet-english.png`, `frontend/guideline-sheet-hindi.png`
  - Physical Chalk Video/Poster: `frontend/hatekhori-chalk-poster.jpg`
- **Real Features Highlighted**:
  1. The A4 Multi-Script Guideline Sheet (Bangla 60 cells, Hindi 60 cells, English 90 cells with 4 corner alignment markers).
  2. Privacy-first photo ingest: Zero AI training, EXIF metadata scrubbing, automatic perspective rectification.
  3. Continuous vector curve extraction: Turning physical ink into digital Bézier glyph paths (`U+0985` / অ).
  4. Interactive Specimen Workbench: Live typing across scripts, optical size waterfall (48px → 18px), and one-click `.otf` export.

## Direction & Motion Philosophy
- **One Shape, Never Cut**: The entire film takes place inside a single morphing hero frame (`#stage-shell`). It begins as an intimate slate tile, expands into the A4 guideline sheet, folds into the studio workbench, morphs into the interactive specimen canvas, and resolves into the final `.otf` font package card.
- **Physical closed-form springs**: No arbitrary CSS transitions or linear interpolation. Every layout morph and element entrance uses analytical damped harmonic oscillators (`spring(t, t0, response, damping)`).
- **Tactile pointer**: A custom precision cursor guides every interaction, exhibiting realistic press scaling (`press(t, t0)`), hover micro-reactions, and drag tension.
- **Blur content transitions**: As the shell morphs between stages, previous contents exit with directional blur and opacity decay before new UI elements spring into place.
- **Sound & Rhythm**: Master clock pinned to 120 BPM (0.50s per beat). 40 beats total (20.0 seconds). Every visual transformation, script switch, and keypress lands squarely on a musical beat. The primary climax (the font compilation drop) explodes on Beat 21.

## Structure (Beat by Beat)

| Beat | Time (s) | Scene / Action | Hero Shell Transformation | Director Note |
| :--- | :--- | :--- | :--- | :--- |
| **B1–B4** | 0.0s–2.0s | **The Hook: Slate to Code**<br>Chalk texture reveals Hatekhori wordmark & subtitle: *"Turn your handwriting into a real font."* | Compact slate card (720×440, r: 24px) | Grounded cultural identity; establishing the slate stone ritual. |
| **B5–B8** | 2.0s–4.0s | **The Sheet: Multi-Script Craft**<br>Cursor clicks *"Download Sheet"*. Shell expands into an A4 grid showing Bengali (60 cells) and English (90 cells) with corner alignment marks. | Morphs into A4 Sheet Ratio (640×880, r: 16px, paper white) | Tangible paper touchpoint. Shows it starts with a physical pen. |
| **B9–B14** | 4.0s–7.0s | **The Ingest: Private Vectorization**<br>Handwritten filled sheet drops in. Corner crosshairs lock on. Scanline sweeps downward; EXIF is scrubbed; zero-AI privacy shield pulses. | Studio Workbench Window (1120×760, r: 20px, slate) | High-tech precision meets artisan paper. |
| **B15–B20** | 7.0s–10.0s | **The Extraction: Stroke to Bézier**<br>Cell zoom into Bengali vowel **অ** (`U+0985`). Raw ink raster dissolves into smooth mathematical vector control points and tangents. Progress bar hits 100%. | Macro Focus Plate (600×600, r: 20px) | Shows the craftsmanship: not a raster image, a real OpenType glyph. |
| **B21–B28** | 10.0s–14.0s | **The Climax (The Drop): Interactive Specimen**<br>**DROP HIT.** Status: *"✓ Font ready"*. Live cursor types in user's handwriting: *"আমার বাংলা ভাষা"*, switches tab to Hindi *"मेरी लिखावट"*, then English *"Hatekhori Atelier"*. | Wide Atelier Specimen Deck (1200×780, r: 20px) | High-energy typing reveal. The font is real, alive, and typing. |
| **B29–B34** | 14.0s–17.0s | **The Waterfall: Optical Scale**<br>Camera glides down the specimen waterfall: 48px headline → 32px subhead → 18px body prose. Proportions remain flawless. | Fluid Specimen Stage (1120×820, r: 20px) | Proves typographic rigor and readability. |
| **B35–B40** | 17.0s–20.0s | **The Resolution & Loop**<br>Cursor clicks *"Download Font (.otf)"*. Shell condenses into an elegant font specimen card with `.otf` file badge and final lockup: *"Own your hand. Bengali, Hindi, English."* Returns seamlessly to initial state. | Compact Font Card (680×380, r: 24px) | The loop closes frame-accurately. Complete ownership, zero subscription. |

## Build Specifications
- **Dimensions**: Square 1440 × 1440 (adaptable to 1920 × 1080 landscape or 1080 × 1920 mobile reel)
- **Framerate**: 60 FPS deterministic render
- **Animation Engine**: Pure `seek(t)` pipeline in `src/` using `core.js`, `device.js`, `scenes.js`
- **Zero External Dependencies**: All typography, SVGs, and audio bundled locally into `assets.js`
- **Verification**: Zero console errors, zero clocks/timers/randomness, seamless loop validation via `check.mjs`

## Status
- **Current Step**: Step 0 (Brief & Plan Prepared)
- **Done**: Repository code audited; brand guidelines and fonts located; creative brief & beat map written.
- **Next**: User approval on creative brief and choice of visual style (Chalk & Slate vs. Paper & Charcoal).
- **Open**: User confirmation to proceed to Step 3 (Build).
