# AGENTS.md — Hatekhori (হাতে খড়ি)

Standing instructions for any agent working in this repository. Read this in full before planning or writing any code. If a task request conflicts with anything here, this file wins — flag the conflict instead of silently resolving it.

---

## 1. What This Product Actually Is

**Hatekhori** is an Indic-first digital typeface atelier and handwriting preservation engine. Named after the traditional Bengali ritual marking a child's first step into literacy — holding chalk (*খড়ি*) in hand (*হাতে*) to draw their first letters on a slate — Hatekhori turns real physical handwriting into ownable, installable OpenType (`.otf`) fonts.

- **Indic-First Heart:** Bengali (বাংলা) and Hindi (हिन्दी) are the cultural and technical core of the project.
- **Tri-Script Production Reality:** Bengali (60 cells), Hindi (60 cells), and English (90 cells) are all fully supported first-class scripts across the guideline sheets, validation engine, font compiler, and interactive specimen.
- **Human Authenticity:** The product preserves a person's genuine handwriting. It is strictly not an AI font generator.

---

## 2. Production Status & Engineering Milestones

The initial engineering pipeline kill-test (Milestone 1) has been successfully completed and validated:
- Guideline sheets for Bengali, Hindi, and English are dynamically generated and downloadable.
- File ingest, EXIF scrubbing, 4-corner fiducial detection, perspective keystone correction, Potrace vectorization, and OpenType (`.otf` CFF) compilation are fully operational.
- The two-stage Studio Workbench and live Typographic Specimen are actively deployed.

**Current Objective:** Ongoing craft refinement, edge-case robustness (lighting, varied pens, paper tilt), glyph contour smoothness, and user experience polish across all three scripts.

---

## 3. Format & Architecture

- **Web Application:** Desktop-first with fluid, accessible mobile responsiveness. Not a native app.
- **Stack:** FastAPI backend (`backend/app/main.py`) paired with vanilla HTML5, CSS3, and ES6 JavaScript (`frontend/`). No heavy frontend frameworks or bloated dependencies.
- **Accountless:** No user accounts, no login walls, no registration forms, no tracking cookies.
- **100% Free & Open Source:** Released under the MIT license with no paywalls, checkout flows, or subscription traps.

---

## 4. Locked Brand Palette & Visual Tokens

The brand identity follows an **Unadorned Editorial Typography & Slate-and-Paper Atelier** design language. Never introduce arbitrary colors or gradients.

### Design Tokens (`frontend/style.css`)

#### Light Mode (Paper & Charcoal Ink)
- `--bg: #FFFFFF;` — Page canvas, clean paper surface.
- `--fg: #111111;` — Deep charcoal ink, headings, primary buttons.
- `--muted: #666666;` — Secondary descriptions, metadata readouts.
- `--border: #E5E5E5;` — 1px hairline panel borders and dividers.
- `--subtle: #F7F7F7;` — Inset containers, unselected tabs, subtle card fills.
- `--accent: #111111;` — Primary active states and focus rings.
- `--accent-hover: #333333;`
- `--red: #D2271B;` — Dedicated alert/error/deletion accent.

#### Dark Mode (Chalkboard & Deep Slate)
- `--bg: #0D0D0D;` — Deep slate chalkboard canvas.
- `--fg: #F0F0F0;` — High-contrast chalk-white letterforms.
- `--muted: #888888;` — Chalk dust labels and secondary copy.
- `--border: #242424;` — Dark hairline borders.
- `--subtle: #141414;` — Recessed slate containers.
- `--accent: #F0F0F0;` — Chalk-white buttons and active pill indicators.
- `--accent-hover: #D0D0D0;`
- `--red: #E03529;` — Dark mode alert/error accent.

#### Atmospheric CTA Banner
```css
background: 
  radial-gradient(ellipse 70% 60% at 50% 50%, rgba(38, 38, 38, 0.85) 0%, rgba(13, 13, 13, 0.98) 100%),
  #0D0D0D;
```

#### Typographic Stack
- **Headlines:** `"Instrument Serif", Georgia, serif`
- **Interface & Body:** `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif`
- **Data & Metadata:** `"DM Mono", monospace`
- **Specimen Fonts:** `"Hatekhori Latin"` / `"Kalam"`, `"Hatekhori Bangla"` / `"Tiro Bangla"`, `"Hatekhori Hindi"` / `"Tiro Devanagari Hindi"`.

---

## 5. Layout & Studio Flow

### Surface 1: Landing Page & Showcase (`#landing-view`)
- **Nav:** Brand link, `#how`, `#specimen`, guideline sheet download dropdown (EN 90 cells, BN 60 cells, HI 60 cells), Feedback modal trigger, Privacy modal trigger, `"Launch Studio"` button.
- **Hero:** Display headline in `Instrument Serif`, lead copy, dual CTAs, and atmospheric looping video card (`hatekhori-chalk.mp4`).
- **Interactive Specimen:** Script switcher tabs, active typeface badge (`Hatekhori Bangla`), live interactive `<textarea>`, 2-column character matrix & Unicode glyph inspector (with magnified glyph and `U+0985` codepoint), and 3-card specimen deck (full character set roster, optical scale waterfall 48/32/24/18px, editorial prose readability block).
- **Process:** 3-step grid (`01 Print & write`, `02 Snap a photo`, `03 Install & own`).
- **CTA:** Atmospheric full-bleed banner.
- **Footer:** 4-column sitemap, takedown contact (`soumik.workmail@gmail.com`), and giant architectural `"Hatekhori"` wordmark.

### Surface 2: Studio Workbench (`#studio-view`)
- **Top Bar:** `"Back to Overview"` button and segmented stage tabs (`1. Guideline Sheet` ↔ `2. Upload & Studio`).
- **Stage 1 (Guideline Sheet Preparation):**
  - Preview card with registration fiducial corner badge, zoom hint, and full-resolution lightbox modal (`#sheet-lightbox-modal`).
  - Configuration card with script selector pills (English 90 cells, Bengali 60 cells, Hindi 60 cells), printing instructions, download trigger, and transition button (`"Already filled? Go to upload →"`).
- **Stage 2 (Upload & Font Creation Workbench):**
  - *Left Deck:* Script selector, drag-and-drop zone (`#dropzone`), legal consent checkbox, `"Generate Font"` button, and 6-step vector engine progress monitor.
  - *Right Deck (Typography Laboratory):* Standby state with `"Test with Demo Handwriting"` shortcut; active state with `"✓ Font ready"` badge, `"Share Link"` button, `"Download Font (.otf)"` button, font size slider (`18px` to `110px`), `"Copy @font-face"` button, `"Glyph Matrix"` toggle drawer, and live interactive textarea.

---

## 6. Security & Ingest Guardrails (Strict & Non-Negotiable)

*Implemented across `backend/app/main.py`, `backend/pipeline/ingest.py`, and `backend/pipeline/validate.py`.*

1. **Chunked Stream Ingest & 15MB Ceiling:** Uploads are read in 64KB chunks up to `MAX_FILE_SIZE_BYTES = 15_728_640`. Any upload exceeding 15MB is terminated immediately (`HTTP 413`). Unbounded reads are strictly prohibited.
2. **Decompression Bomb Defense:** `Image.MAX_IMAGE_PIXELS = 36_000_000` (36 Megapixels) and maximum pixel dimension of 6,000px per side.
3. **EXIF GPS Scrubbing:** All EXIF, IPTC, and XMP metadata dictionaries are completely stripped on ingest. Orientation is normalized via `ImageOps.exif_transpose()`.
4. **Fiducial Registration & Structural Check:** 4 corner black square fiducial markers must be detected; sheets without valid registration or minimum ink density fail validation before reaching vectorization.
5. **Sliding-Window Rate Limiting:** In-memory rate limiting per client IP:
   - `/ingest`: max 15 requests per 60 seconds.
   - `/generate`: max 6 requests per 60 seconds.
6. **Concurrency Throttling:** `_GENERATE_SEMAPHORE = AsyncBoundedSemaphore(2)` limits parallel font compilations to 2 threads.
7. **Path Traversal Protection:** Request parameters such as `{upload_id}` are strictly typed as standard library `uuid.UUID`. Font download formats are strictly restricted to `"otf"` or `"ttf"`.
8. **Abuse Hash Logging:** Rejected uploads are hashed (SHA-256) and logged in `rejected_hashes.log`. Raw rejected images are never stored.

---

## 7. Data Retention & Privacy Contract

*Must match `docs/privacy-policy.md` and the frontend `#privacy-modal` exactly.*

| Data Category | Retention Limit | Storage Location | Purge Mechanism |
| :--- | :--- | :--- | :--- |
| **Raw Uploaded Photo** | Single processing run | `uploads/{uuid}.img` | Unlinked immediately upon font compilation (max 24h on error). |
| **Compiled Font (.otf)** | 30 days | `output/{uuid}.otf` | Auto-purged by hourly background sweep task. |
| **Consent Record** | Single session | Request lifecycle | Purged together with the submission. |
| **Rejected Upload Hashes** | 90 days | `output/rejected_hashes.log` | SHA-256 hashes only. No image data retained. |
| **Telemetry** | Indefinite | Memory / Aggregated | Strictly anonymized count metrics. |

**Zero AI Model Training:** Uploaded handwriting is never used to train machine learning models — ours, a partner's, or anyone else's.

---

## 8. Voice, Tone, and Copy Rules

- **Warm, Quiet Confidence:** The voice of an editorial craftsperson or bookbinder. Never hypy or corporate.
- **Never Say "AI-Powered":** The value of Hatekhori is that a real human being sat down with a pen and wrote.
- **Considered, Kind Errors:** Provide helpful, actionable feedback when a sheet fails alignment or lighting is poor.
- **No Emojis in Core UI:** Use clean monoline SVG icons with consistent stroke weights.
- **Respect Focus:** Every screen has one clear job; cut duplicate or competing controls.

---

## 9. Non-Goals (Explicit Exclusions)

- No user accounts, passwords, or authentication frameworks.
- No subscription billing, payment gateways, or monetization locks.
- No native mobile app store wrappers (web-first).
- No synthetic AI handwriting generators.
- No English-only companion app families (greeting cards, quote makers). All engineering effort stays focused on handwriting fidelity and Indic script preservation.

---

## 10. Questions and Governance

If a task requires decisions not explicitly codified in this document or companion files, treat it as an open question: formulate options and ask the user rather than making silent assumptions.
