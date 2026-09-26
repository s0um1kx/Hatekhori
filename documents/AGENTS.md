# AGENTS.md — Hatekhori (হাতে খড়ি)

Standing instructions for any agent working in this repo. Read this in full before planning or writing any code. If a task request conflicts with anything here, this file wins — flag the conflict instead of silently resolving it.

---

## 1. What this product actually is

Hatekhori turns a person's real handwriting into an installable, ownable font. **It is not a font-tool-that-added-Bengali-later. It is a Bengali/Hindi handwriting-preservation atelier that happens to validate its engineering in English first, privately.**

Do not treat English as the product at any point in scaffolding, copy, routing, or default script selection. If a script picker, onboarding flow, or marketing string defaults to English, that's a bug against this doc.

## 2. Build order — the single most important constraint

- **Internally first:** the pipeline (capture → cleanup → vectorize → metrics → font export) is built and validated in **English** (~60–90 glyphs, cheap to iterate). This is never shown, linked, deployed publicly, or referenced in marketing copy as "the product."
- **Publicly first:** the first script an outside user ever sees is **Bengali and/or Hindi**.
- Do not build any public-facing route, landing page, or marketing surface around the English pipeline. It lives behind no public link at all during Milestone 1.

## 3. Current milestone — read this before writing UI code

**Milestone 1 is a pipeline kill-test, not a website.**

Goal: take a small batch of real, varied handwriting photos (different pens, lighting, neatness) through capture → vectorize → metrics → font export, in English, and answer one question: *does the output look like a font a designer would use, or a ransom note?*

- **Pass →** build the real guideline-sheet UI/capture flow (still private, still English), then start Bengali/Hindi glyph-set scoping.
- **Fail →** stop. Do not write more UI code. Fix vectorization/metrics first.

Do not skip ahead to polished screens, onboarding, or marketing pages before this test passes. If asked to "build the app," scope the first deliverable to this kill-test unless told otherwise.

## 4. Format & scope

- Website, not a native app. Desktop-first (this is a designer/developer tool); mobile is secondary.
- Single capture flow only — no "Quick Mode" vs "Precision Mode" split. One well-designed guideline sheet, one path, for both English (internal) and Bengali/Hindi (public).
- No accounts, no login, no signup wall, anywhere in the core flow. There is no payment gateway and no re-download-to-a-paying-user problem, so there is no structural reason for identity. Provenance (name, date) is a plain form field at export time, not an account system.
- No payment gateway for now. Project is open source, no checkout, no license key, no paid tier. If monetization is revisited later, the only acceptable model is **one-time payment, never subscription** — do not scaffold subscription billing "just in case."

## 5. Core flow (single path)

1. One guideline sheet covering the target script's required character set.
2. User writes on it (printed or matching layout on their own paper).
3. Capture via QR code + phone camera (auto-corrects perspective/lighting/crop) **or** direct upload of an existing photo.
4. System validates the upload is actually a filled guideline sheet, with a clear, non-alarming error if not.
5. Handwriting → real font file.
6. Preview on a visual canvas with a **Human / Machine toggle**:
   - Human: the rendered font shown naturally (e.g. on a mock portfolio/card).
   - Machine: the underlying vector paths / font data.

The Human/Machine toggle is the single most important control on the editor screen — it gets a fixed position (top of the right panel), never buried in a settings menu.

## 6. Upload requirements & guardrails

Accepted formats: JPG, PNG, HEIC (PDF: decide once real Milestone 1 data exists). Size limit: set from real capture-flow data, not guessed upfront.

**Baseline — required before any UI ships, even internally, non-negotiable:**
- Real content-sniffing on file bytes, not just extension/MIME header.
- Hard caps on file size *and* pixel dimensions.
- Strip EXIF metadata on ingest, always, no exceptions.
- Guideline-sheet structural validation doubles as a security check (junk/inappropriate images mostly won't match the expected shape).

**Required before the Bengali/Hindi public launch — non-negotiable:**
- Automated image-safety classifier (NSFW/violence/CSAM-signal detection) gating entry *before* vectorization or storage. Hard reject, not a soft warning. Log only the rejected image's hash for abuse review.
- Lightweight, non-identity consent checkbox at submission ("this is my own handwriting and I have the right to submit it"). This is a legal/provenance safeguard, not an account — never expand it into auth.
- IP- or session-based rate limiting (there's no account to throttle instead).
- Raw uploaded photos are never displayed publicly by default — only the derived font/glyphs.
- A visible, no-account-required abuse/takedown contact (a plain email link).

**Deferred (only if a public gallery/showcase ships later):** human moderation queue for classifier-borderline cases; separate consent for "process this for me" vs. "make this visible to others." Do not build these now.

## 7. Data retention (must match the on-site privacy policy exactly)

| Data | Retention |
|---|---|
| Raw uploaded photo | Deleted immediately on successful generation; deleted within 24h regardless if generation fails |
| Generated font + provenance | Kept 30 days for re-download, then purged server-side |
| Consent record | Purged together with the underlying submission |
| Rejected/flagged upload hashes | Hash only, never the image; rolling 90-day window unless under active abuse investigation |
| Aggregate/anonymized usage stats | Indefinite — no personal or image data in it |

Never use uploaded handwriting to train any model, ours or anyone else's. No opt-out toggle needed because there is no opt-in path either — do not add a training-consent checkbox unless a human explicitly decides to revisit this. If a self-hosted/open-source deployment path is built, the app must make clear this retention policy describes the hosted instance only.

## 8. Brand palette — locked, implement exactly

| Role | Hex | Usage |
|---|---|---|
| Stage / paper | `#F2ECE1` | Page background, panel surface. Never pure white. |
| Ink (primary) | `#0034D3` | All text, strokes, primary buttons, active/selected states, character-grid selection. Carries the whole brand. |
| Ink (deep) | `#003087` | Emphasis on top of primary blue — pressed/active states, headings on a blue fill. |
| Tint | `#99CCFF` | Light wash only — hover backgrounds, disabled/inactive fills, unselected toggle side. Not for body text under 14px. |

Do:
- One saturated accent (`#0034D3`) everywhere an accent is needed.
- `#F2ECE1` as the only background tone for product surfaces.
- `#99CCFF` only for "quieter than default" states.

Don't:
- Add a second saturated hue anywhere, for any reason ("variety" is not a reason).
- Use pure black or pure white.
- Add a status color (error/success) without checking — if genuinely needed, add the smallest possible addition, don't let it become a fifth brand color.
- Let the hand-drawn squiggle/doodle motif (marketing surfaces only) appear inside the editor/tool UI.

## 9. Layout & grid

12-column grid, desktop-first.

| Breakpoint | Viewport | Columns | Margin | Gutter | Max content width |
|---|---|---|---|---|---|
| Desktop | ≥1280px | 12 | 64px | 24px | 1200px |
| Laptop | 1024–1279px | 12 | 48px | 20px | fluid |
| Tablet | 768–1023px | 8 | 32px | 16px | fluid |
| Mobile | <768px | 4 | 20px | 12px | fluid |

Spacing scale — use only these values, no arbitrary padding: `4·8·12·16·24·32·48·64·96px`. Baseline row height for any glyph-grid/character-picker: `40px`.

**Page patterns:**
- **Marketing/landing:** stage-colour background allowed; content sits in a max 8-column measure (never full-width copy); one hero statement, one supporting line, one CTA — no stacked 6-card feature grids.
- **Capture flow:** single column, centred, max 6 columns wide, one thing happens at a time; progress indicator in ink colour only, no rainbow progress bars.
- **Editor/canvas:** three zones — glyph/character grid (3 cols) → live canvas preview (6 cols) → Human/Machine toggle + output panel (3 cols). Thin 1px hairline borders on the paper surface, never drop-shadowed cards. Nothing duplicated between zones.
- **Gallery/output:** 8-column grid, max 3 items per row even on wide screens — this is a craft product, not a marketplace grid.

Don't: default to white-background SaaS layout; add a second accent color; drop-shadow panels on the editor screen.

## 10. Voice, tone, and copy rules

- Warm, quiet confidence — a craftsperson describing their work, not a SaaS launch.
- Never say "AI-powered" anywhere in product copy. The point is that a person made this.
- Error/edge-case copy is considered and kind, never a system alert.
- Don't invent a founder story or personal narrative that isn't the actual founder's own.
- No emojis in the UI — one real icon set, one weight, one size, everywhere.
- Every screen should help someone finish one specific task; if a component or piece of information is duplicated elsewhere on the same screen, cut it.

## 11. Competitive non-negotiables (why several of the rules above exist)

FontCrafter (free, private, 500+ glyphs, full companion-app ecosystem) has already won the English handwriting-to-font fight — free, private, feature-complete. Do not:
- Build an English companion-app family (a QuoteCrafter/PenSend equivalent).
- Compete on "free" or lead marketing with "not AI handwriting" as the sole differentiator.
- Add any feature whose only purpose is closing a gap with FontCrafter's English feature set.

Bengali/Hindi conjunct support is the one thing no competitor (legacy paid tools, pro creative-tool integrations, or FontCrafter's free ecosystem) currently does. All differentiation effort goes there.

## 12. Non-goals (do not build these without an explicit human decision)

- Generic AI-handwriting-font generator (this is about *your own* handwriting specifically).
- Native mobile app.
- Marketing that positions English as launch-worthy.
- Two capture-quality tiers.
- An English companion-app ecosystem.
- Any account/auth system.
- Subscription billing.
- A public gallery/showcase (until explicitly greenlit — see §6 deferred items).

## 13. When something isn't covered here

If a task requires a decision this file doesn't cover (exact glyph/conjunct set, upload size limit, PDF support, pricing tiers, Telugu scope), treat it as an **open question** — propose an option and ask, rather than silently deciding and building on top of an assumption.
