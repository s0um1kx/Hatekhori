# Hatekhori (হাতে খড়ি) — Layout & Grid Guidelines

*Companion to `hatekhori-brand-colors.md`, `PRD.md`, and `BRAND.md`. This file documents the layout architecture, responsive grid system, and component patterns for Hatekhori.*

---

## 1. Grid Architecture

Hatekhori is built desktop-first as a designer and developer tool, with a fluid, accessible responsive layout that gracefully scales down to mobile devices.

### Breakpoints & Columns

| Breakpoint | Viewport Width | Columns | Outer Margin | Gutter | Max Content Width |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Desktop** | ≥ 1280px | 12 | 64px | 24px | 1200px |
| **Laptop** | 1024–1279px | 12 | 48px | 20px | Fluid (100%) |
| **Tablet** | 768–1023px | 8 | 32px | 16px | Fluid (100%) |
| **Mobile** | < 768px | 4 | 20px | 12px | Fluid (100%) |

### Strict Spacing Scale

Arbitrary margin and padding values are prohibited. All layout spacing must use the standard scale:
`4px · 8px · 12px · 16px · 24px · 32px · 48px · 64px · 96px · 120px`

- **Touch targets:** Minimum `44 × 44px` with at least `8px` spacing.
- **Micro-labels / tags:** `11px` to `13px` in `var(--font-mono)`.
- **Body text:** `15px` to `16px` with line-height `1.5` to `1.6`.
- **Headlines:** Clamped responsive fluid type (`clamp(36px, 5vw, 64px)` for hero titles).

---

## 2. Core Surface 1: Minimal Landing Page & Type Showcase

The landing page (`#landing-view`) serves as the introduction and live proof of the font engine:

### A. Minimal Navigation (`.nav`)
- Fixed/sticky bar with backdrop blur (`backdrop-filter: blur(12px)`).
- Left: Brand logo `"Hatekhori"` linking to top.
- Center/Right: Navigation links (`#how`, `#specimen`), guideline sheet download dropdown menu, Feedback modal trigger, Privacy & Terms modal trigger.
- Primary Action: `"Launch Studio"` button with animated hover arrow.

### B. Hero Section (`.hero`)
- Two-column grid layout (60% content / 40% media on desktop; stacked single-column on mobile).
- Left: Editorial headline in `Instrument Serif` (`"Turn your handwriting into a real font."`), concise lead description, and dual actions: `"Launch Font Studio"` primary button + `"Download Sheet"` dropdown.
- Right: Atmospheric video card displaying the tactile ritual of chalk writing on slate (`hatekhori-chalk.mp4`).

### C. Interactive Specimen & Laboratory (`#specimen`)
- **Specimen Bar:** Script selector tabs (`English (Latin)`, `Bengali (বাংলা)`, `Hindi (हिन्दी)`) with live Active Typeface Badge (`Hatekhori Bangla`, `Hatekhori Hindi`, or `Hatekhori Latin`).
- **Live Canvas Plate:** Large interactive `<textarea>` preloaded with culturally authentic sample text in the active script, rendered in the corresponding handwritten font.
- **Matrix & Glyph Inspector:** Two-column component pairing an interactive character cell grid with a live Inspector card displaying the magnified glyph (`#big`) and its exact Unicode codepoint (`#cp`, e.g., `U+0985`).
- **Type Specimen Deck (3 Cards):**
  1. *Character Set & Glyph Roster:* Explicit display of all supported letters, consonants, vowels, and matras.
  2. *Optical Scale Waterfall:* Fluid type rendering at 48px, 32px, 24px, and 18px.
  3. *Continuous Prose Readability:* Body paragraph demonstrating rhythm, line height, and text texture.

### D. Process Section (`#how`)
- Three-column grid (`01 Print & write`, `02 Snap a photo`, `03 Install & own`).
- High-contrast step numbering with concise, clear instructions.

### E. Atmospheric CTA Banner (`#cta`)
- Full-bleed dark slate section with radial illumination.
- Direct prompt: `"Make your font today."` with `"Launch Font Studio"` button.

### F. Fathom-Style Footer (`#main-footer`)
- 4-column sitemap grid: Navigation, Guideline Sheets, Resources (GitHub & Spec), Ethics & Legal (Privacy, Data Takedown, Contact).
- Architectural giant `"Hatekhori"` wordmark anchored at the base with generous breathing room.

---

## 3. Core Surface 2: Studio Workbench (`#studio-view`)

The studio operates as an **Atelier Two-Stage Flow**, keeping each step focused and distraction-free:

### Top Navigation & Stage Switcher
- Left: `"Back to Overview"` button returning to the landing view.
- Center: Segmented stage tabs (`1. Guideline Sheet` ↔ `2. Upload & Studio`).

### Stage 1: Guideline Sheet Preparation (`#stage-sheet-panel`)
Two-column atelier layout:
- **Left (Preview Plate):** High-resolution visual card of the guideline sheet with registration fiducial corner badge and `"Preview Full Size ↗"` hover overlay. Clicking opens the lightbox modal.
- **Right (Configuration Box):**
  - Step eyebrow: `Step 1: Download guideline sheet`.
  - Language sheet selector pills: `English (Latin)` (90 cells), `Bengali (বাংলা)` (60 cells), `Hindi (हिन्दी)` (60 cells).
  - Guidelines card: 100% scale printing instruction, dark ink pen recommendation, flat paper alignment rule.
  - Action buttons: Primary `"Download Sheet"` + outline `"Already filled? Go to upload →"`.

### Stage 2: Font Creation Workbench (`#stage-workbench-panel`)
Split-pane workshop layout:
- **Left Deck (Upload & Pipeline Monitor):**
  - *Upload Card:* Sheet language switcher pills, drag-and-drop zone (`#dropzone`) supporting JPG/PNG with file preview and change/remove actions.
  - *Consent Checkbox:* Legal certification checkbox ("I certify this is my own handwriting and I have the right to submit it").
  - *Compile Action:* `"Generate Font"` button (disabled until file and consent are verified).
  - *Progress Monitor (`#step-progress`):* Real-time 6-step vector engine pipeline indicator:
    1. Ingesting scan and removing photo metadata
    2. Locating corner alignment markers
    3. Straightening and aligning page
    4. Isolating individual letter cells
    5. Tracing ink strokes into vector outlines
    6. Building installable OpenType font tables
- **Right Deck (Typography Laboratory & Live Font Tester):**
  - *Standby Empty State:* Friendly invitation to upload a sheet, with `"Test with Demo Handwriting"` option for immediate evaluation.
  - *Active Result State (`#step-result`):*
    - Top bar: `"✓ Font ready"` badge, `"Share Link"` button (copies unique live URL), `"Download Font (.otf)"` primary button.
    - Specimen toolbar: Font size slider (`18px` to `110px`), `"Copy @font-face"` CSS helper, and `"Glyph Matrix"` drawer toggle.
    - Interactive Canvas Plate: Live `<textarea>` rendering typed text in the freshly compiled user font.
    - Glyph Matrix Drawer: Expandable grid of extracted individual glyphs that can be clicked to insert directly into the canvas.

---

## 4. Modal Design Patterns

All modals follow standard accessible dialog mechanics:
- Screen-filling backdrop with blur (`rgba(0,0,0,0.65)`).
- Centered card with maximum width `680px` (`920px` for sheet lightbox).
- Trapped keyboard focus and `Escape` key close listener.
- Click-outside-to-dismiss behavior.

1. **Feedback & Bug Report Modal (`#feedback-modal`):**
   - Category selector, message input with character count, optional contact info, and auto-detected diagnostics (active script, upload ID, error log).
2. **Privacy Policy Modal (`#privacy-modal`):**
   - Clean tabular display of the 30-day font retention schedule, zero AI training commitment, and deletion procedures.
3. **Guideline Sheet Zoom Lightbox (`#sheet-lightbox-modal`):**
   - Full-fidelity inspection view of the A4 grid with printing tips and direct download trigger.

---

## 5. Layout Do / Don't

### Do
- Ensure hairline borders (`1px solid var(--border)`) are used instead of heavy drop shadows.
- Keep the two-stage studio separation clean — users prepare their paper first, then upload.
- Ensure the interactive specimen is immediately functional upon page load with fallback and sample fonts.

### Don't
- Never crowd multiple conflicting primary CTAs into one viewport.
- Never let long lines of body copy exceed `65ch` in editorial sections.
- Never use multi-colored status bars; keep progress indicators in monochrome ink and muted tones.
