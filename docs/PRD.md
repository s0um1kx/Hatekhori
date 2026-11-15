# Hatekhori (হাতে খড়ি) — Product Requirements Document (PRD)

> Version: 2.5 (Final Architecture Specification)  
> Companion Docs: `BRAND.md`, `hatekhori-brand-colors.md`, `hatekhori-layout-grid.md`, `privacy-policy.md`, `SECURITY.md`, `AGENTS.md`.

---

## 1. Executive Summary & Product Vision

**Hatekhori** ("holding the chalk") is an open-source, web-based digital typeface atelier and handwriting preservation engine. Named after the traditional Bengali ritual where a child draws their first letter on a slate, Hatekhori turns real handwriting into an installable, ownable OpenType (`.otf`) font file.

### Primary Objectives
1. **Indic-First Craft:** First-class support for **Bengali (বাংলা)** and **Hindi (हिन्दी)** alongside **English (Latin)**.
2. **Accountless & Privacy-First:** No accounts, no logins, zero behavioral tracking, and **zero AI model training**.
3. **Single Focused Path:** A guided, friction-free two-stage atelier flow: Sheet Preparation → Upload & Creation.
4. **Instant Typographic Utility:** Immediate interactive specimen testing, shareable live preview links, and ready-to-use `@font-face` CSS snippets.

---

## 2. Multi-Script Specifications

Hatekhori standardizes character grids across three supported scripts, formatted for standard A4 paper at 100% scale with four precision corner registration fiducials.

| Script | Grid Dimensions | Total Cells | Included Characters |
| :--- | :--- | :--- | :--- |
| **English (Latin)** | 10 cols × 9 rows | 90 Cells | Uppercase `A–Z`, lowercase `a–z`, numbers `0–9`, basic punctuation (`! ? , . : ; " ' - ( ) / @ # $ % & * + =`). |
| **Bengali (বাংলা)** | 10 cols × 6 rows | 60 Cells | 11 স্বরবর্ণ (Vowels), 39 ব্যঞ্জনবর্ণ ও বিশেষ চিহ্ন (Consonants & Specials: `ঁ ং ঃ ৎ`), 10 কারচিহ্ন (Vowel Signs / Matras: `া ি ী ু ূ ৃ ে ৈ ো ৌ`). |
| **Hindi (हिन्दी)** | 10 cols × 6 rows | 60 Cells | 11 स्वर (Independent Vowels), 39 व्यंजन (Consonants & Specials), 10 मात्राएँ (Dependent Vowel Signs: `ा िर ी ु ू ृ े ै ो ौ`). |

---

## 3. User Experience & Application Architecture

The application is structured into two primary full-width views:

### View 1: Minimal Landing Page & Typographic Showcase (`#landing-view`)
- **Navigation (`.nav`):**
  - Brand identity `"Hatekhori"`.
  - Jump links: `"How it works"`, `"Specimen"`.
  - Guideline sheet download dropdown (English 90 cells, Bengali 60 cells, Hindi 60 cells).
  - Modal action buttons: `"Feedback"`, `"Privacy & Terms"`.
  - Primary CTA: `"Launch Studio"`.
- **Hero Section (`.hero`):**
  - Display title in `Instrument Serif`: `"Turn your handwriting into a real font."`
  - Concise lead copy highlighting multi-script support.
  - Action buttons: `"Launch Font Studio"` primary button + `"Download Sheet"` dropdown.
  - Looping atmospheric video card (`hatekhori-chalk.mp4`) showing chalk writing on slate.
- **Interactive Specimen Section (`#specimen`):**
  - Script selector tabs (`English`, `Bengali`, `Hindi`) with dynamic Active Typeface Badge (`Hatekhori Bangla`, `Hatekhori Hindi`, or `Hatekhori Latin`).
  - Interactive `<textarea>` populated with culturally rich sample text in the active script.
  - Two-column Matrix & Glyph Inspector: clickable character matrix paired with a magnified glyph preview (`#big`) and Unicode hex codepoint (`#cp`, e.g., `U+0985`).
  - Full Typographic Specimen Deck:
    1. *Character Set & Glyph Roster:* Explicit display of all 60–90 supported characters.
    2. *Optical Scale Waterfall:* Responsive rendering at 48px, 32px, 24px, and 18px.
    3. *Continuous Editorial Prose:* Body text readability test demonstrating line rhythm.
- **Process Section (`#how`):**
  - 3-step grid: `01 Print & write` → `02 Snap a photo` → `03 Install & own`.
- **Atmospheric CTA Banner (`#cta`):**
  - Full-bleed dark slate section inviting the user to build their font immediately.
- **Fathom-Style Footer (`#main-footer`):**
  - 4-column sitemap: Navigation, Guideline Sheets, Resources, Ethics & Legal.
  - Prominent data takedown contact: `soumik.workmail@gmail.com`.
  - Architectural giant `"Hatekhori"` wordmark.

---

### View 2: Studio Workbench (`#studio-view`)

A distraction-free, two-stage creation workbench:

#### Stage 1: Guideline Sheet Preparation (`#stage-sheet-panel`)
- **Visual Preview Plate:** High-resolution card displaying the selected guideline sheet with corner fiducial badge and `"Preview Full Size ↗"` hover overlay. Clicking opens the full-screen zoom lightbox modal (`#sheet-lightbox-modal`).
- **Configuration Box:**
  - Language selector pills: `English (Latin)`, `Bengali (বাংলা)`, `Hindi (हिन्दी)`.
  - Printing criteria checklist: Standard A4 at 100% scale (no "fit to page"), dark ink pen, flat paper with all 4 corner markers clearly visible.
  - Action buttons: Primary `"Download Sheet"` + outline `"Already filled? Go to upload →"`.

#### Stage 2: Font Creation Workbench (`#stage-workbench-panel`)
- **Left Deck (Upload & Engine Progress):**
  - *Script Language Selector:* Radio pill switcher (`English`, `Bengali`, `Hindi`) with automatic script detection fallback.
  - *Dropzone (`#dropzone`):* Drag-and-drop or file browser supporting JPG, PNG, and HEIC. Displays live preview with change and remove actions.
  - *Legal Consent Checkbox:* Non-identity provenance certification ("I certify this is my own handwriting and I have the right to submit it").
  - *Action Button:* `"Generate Font"` button (enabled only when both photo and consent are provided).
  - *Vector Engine Monitor (`#step-progress`):* Real-time progress pulse detailing the 6 backend pipeline phases:
    1. Ingesting scan and removing photo metadata
    2. Locating corner alignment markers
    3. Straightening and aligning page
    4. Isolating individual letter cells
    5. Tracing ink strokes into vector outlines
    6. Building installable OpenType font tables
- **Right Deck (Typography Laboratory & Live Font Tester):**
  - *Standby Empty State:* Clear instructional state with a `"Test with Demo Handwriting"` shortcut for immediate previewing.
  - *Active Result State (`#step-result`):*
    - Top bar: `"✓ Font ready"` status badge, `"Share Link"` button (copies unique live URL), and `"Download Font (.otf)"` primary button.
    - Specimen toolbar: Font size slider (`18px` to `110px`), `"Copy @font-face"` CSS helper, and `"Glyph Matrix"` toggle drawer.
    - Live Canvas Plate: Interactive editable `<textarea>` rendering typed text in the freshly compiled user font.
    - Glyph Matrix Drawer: Expandable grid of extracted individual glyphs that can be clicked to insert directly into the canvas.

---

## 4. Technical Pipeline Specifications

### Ingest & Image Normalization (`pipeline/ingest.py`)
- **Chunked Stream Ingest:** Reads incoming uploads in 64KB chunks up to an absolute ceiling of 15MB (`MAX_FILE_SIZE_BYTES`). Aborts with `HTTP 413` if exceeded.
- **Decompression Bomb Protection:** Hard cap of `Image.MAX_IMAGE_PIXELS = 36_000_000` (36 Megapixels) and maximum pixel dimension of 6,000px per side.
- **EXIF Metadata Scrubbing:** All EXIF, IPTC, and XMP metadata dictionaries are completely stripped on ingest. Orientation is normalized via `ImageOps.exif_transpose()`.

### Structural Alignment & Validation (`pipeline/validate.py`)
- **Fiducial Registration:** Detects 4 solid black square fiducial markers at the page corners.
- **Perspective Keystone Correction:** Calculates four-point homography transform to warp and deskew tilted or angled phone captures into a perfect rectangle.
- **Ink Density Check:** Verifies minimum dark-pixel coverage across cell coordinates to reject blank or unwritten sheets.

### Vectorization & Font Compilation (`pipeline/vectorize.py`, `pipeline/compile.py`)
- **Tracing:** Sub-pixel contour tracing using Potrace to convert raster ink marks into smooth Bézier curves.
- **Metrics Calculation:** Automatically calculates baseline, ascent, descent, and advance width based on cell geometry.
- **OpenType Compilation:** Compiles standard TrueType / OpenType (`.otf` CFF) binary tables, including `head`, `hhea`, `maxp`, `OS/2`, `hmtx`, `cmap`, and `CFF `.

---

## 5. Security Architecture & Threat Model

*Detailed comprehensively in `SECURITY.md`.*

1. **Denial of Service (DoS):**
   - Sliding-window rate limiter per client IP: 15 req/min on `/ingest`, 6 req/min on `/generate`.
   - Concurrency semaphore (`_GENERATE_SEMAPHORE = AsyncBoundedSemaphore(2)`) restricts parallel CPU-intensive vectorization to 2 threads.
2. **Path Traversal Protection:**
   - Route parameters (`{upload_id}`) are strictly typed as standard library `uuid.UUID`.
   - Download format parameter is strictly restricted to `"otf"` or `"ttf"`.
3. **Abuse Tracking:**
   - Rejected uploads are hashed (SHA-256) and recorded in `rejected_hashes.log`. Raw rejected images are never retained.
4. **Browser Security Headers:**
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `Referrer-Policy: strict-origin-when-cross-origin`
   - Strict `Content-Security-Policy` and `Permissions-Policy`.

---

## 6. Data Lifecycle & Privacy Contract

*Detailed comprehensively in `privacy-policy.md`.*

| Data Category | Purpose | Retention Window | Purge Mechanism |
| :--- | :--- | :--- | :--- |
| **Raw Uploaded Photo** | Process into font | Single compilation run | Unlinked immediately upon font compilation; unlinked within 24h on error. |
| **Generated Font (.otf)** | User download & testing | 30 days from creation | Purged permanently by hourly background sweep task. |
| **Submission Consent** | Legal certification | Single session | Purged together with the underlying submission. |
| **Rejected Upload Hashes**| Abuse prevention | Rolling 90-day window | SHA-256 hashes only. No image data retained. |
| **Telemetry** | Health monitoring | Indefinite | Strictly anonymized count numbers. |

**Zero Model Training:** Uploaded handwriting is never used to train machine learning models — ours, a partner's, or anyone else's.

---

## 7. Business Model & Governance

- **100% Free & Open Source:** Released under the MIT license on [GitHub](https://github.com/s0um1kx/Hatekhori).
- **No Monetization Layer:** No checkout, no paid tiers, no subscription traps.
- **Takedown & Inquiries:** Managed directly by the author via `soumik.workmail@gmail.com`.

---

## 8. Explicit Non-Goals

1. **No User Accounts:** No registration, no login walls, no user database.
2. **No Generic AI Font Generation:** Hatekhori exclusively digitizes a person's real, physical handwriting.
3. **No Native App Store Wrappers:** Desktop-first, fully responsive web application.
4. **No Feature Parity Battles with Latin-Only Utilities:** We do not build English-only companion apps (greeting card generators, quote makers, etc.). All engineering focus remains on handwriting fidelity and Indic script preservation.
