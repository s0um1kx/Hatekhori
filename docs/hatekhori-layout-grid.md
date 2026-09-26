# Hatekhori — Layout & Grid Guidelines

*Companion to PRD.md, BRAND.md and the account-level design.md. This file is the actual grid math and page-layout rules — the thing an AI coding agent (or you) checks before placing a single div.*

## 1. What the reference clip is actually doing

The clip you sent (**Scriptscript by Schultzschultz**) isn't decoration — it's a formula:

- **One saturated "stage" colour, one "ink" colour, nothing else.** Burnt orange background, indigo-blue strokes/labels. No gradient, no third accent competing for attention.
- **Panels are instruments, not cards.** Thin 1px hairline borders, square corners, mono/technical labels in small caps (`Script`, `word space`, `letter width`). It reads like an oscilloscope, not a website.
- **Three-zone workspace**: glyph editor (left) → live preview (centre) → parameters + mini-output (right). Each zone has exactly one job. Nothing is duplicated between zones.
- **A single moving detail** (the rotating logo mark) is the *only* motion in the whole frame — so it actually gets noticed.

The lesson isn't "use orange." It's: **pick one stage colour + one ink colour, commit completely, and let the grid do the rest of the work.**

## 2. Competitor scan

| Product | Layout | Colour | Read |
|---|---|---|---|
| **FontCrafter** | Single-page utility, plain scan→upload→download steps, default form styling | Near-colourless — white background, system blue links | Feels like a tool a developer shipped in a weekend (it was — "one HTML file, 6,300 lines"). Zero brand identity, which is *the point* for them: free-utility positioning. |
| **Calligraphr** | Classic SaaS dashboard: sidebar + grid-template downloader + account gate | Corporate blue/white, stock SaaS palette | Functional but generic — could be any B2B tool. Account-first (login before you even see the template). |
| **FontCraft** | iPad-first draw canvas, tool palette down one side | Soft neutral greys, light accent | Reads as a drawing app, not a type tool — friendly but not confident. |

**The gap**: none of your direct competitors have a stage colour. They're all "default web app" white/grey/blue. That's the whitespace — a confident, saturated, consistent colour identity is instantly differentiating in this category, the same way Schultzschultz's orange makes their tool memorable in a screen recording alone.

## 3. Brand colour

Locked and maintained separately in **hatekhori-brand-colors.md** — the palette (`#0034D3` ink, `#F2ECE1` paper, `#99CCFF` tint, `#003087` deep accent), the reasoning behind it, and where the Ctrl+ board's squiggle motif is and isn't allowed. Read that file alongside this one; the grid rules below assume that palette.

## 4. Grid system

**12-column grid, desktop-first (this is a designer/developer tool — desktop is primary, mobile is secondary per the existing PRD).**

| Breakpoint | Viewport | Columns | Margin | Gutter | Max content width |
|---|---|---|---|---|---|
| Desktop (default) | ≥1280px | 12 | 64px | 24px | 1200px |
| Laptop | 1024–1279px | 12 | 48px | 20px | fluid |
| Tablet | 768–1023px | 8 | 32px | 16px | fluid |
| Mobile | <768px | 4 | 20px | 12px | fluid |

Spacing scale (use only these values — no arbitrary padding):
`4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96px`

Baseline row height for anything grid-like (character picker, glyph list): **40px**, so a 26-letter A–Z grid always lines up cleanly regardless of column count.

## 5. Page-level layout patterns

**Landing / marketing pages** (stage-colour background allowed here):
- 12-col grid, but content itself sits in a **max 8-column** measure — never let marketing copy run the full width, it reads as unstructured/AI-generated.
- One hero statement, one supporting line, one CTA. No stacked feature-card grids of 6+ identical boxes (this is exactly the "AI slop" pattern design.md already flags).

**Capture flow** (guideline sheet → photo/upload → validation):
- Single column, centred, max 6 columns wide. This is a sequential task — don't give it a multi-panel layout, one thing happens at a time.
- Progress indicator uses the ink colour only, no rainbow progress bars.

**Editor / canvas screen** (this is your Schultzschultz moment — where the tool should feel like an instrument):
- Three-zone layout, same logic as the reference: **glyph/character grid** (3 cols) → **live canvas preview** (6 cols) → **Human/Machine toggle + output panel** (3 cols).
- Panels get thin 1px borders on the paper surface colour, not drop-shadowed cards — shadows read as generic UI-kit, hairlines read as instrument.
- The Human/Machine toggle is the single most important control on this screen — give it its own fixed position (top of the right panel), don't bury it in a settings menu.

**Gallery / output states** (font preview, download):
- 8-column grid, no more than 3 items per row even on wide screens — this is a craft product, not a marketplace grid.

## 6. Do / don't (extends design-guidelines.md)

**Do**
- One stage colour, one ink colour, one neutral paper tone — that's the whole palette.
- Hairline borders + mono/uppercase micro-labels for anything tool-like (editor, parameters).
- Let every panel do exactly one job, same as the reference clip's three zones.

**Don't**
- Don't default to white-background SaaS layout — that's literally what FontCrafter and Calligraphr already look like; matching them erases your differentiation.
- Don't add a second accent colour "for variety" — the reference clip's whole impact comes from restraint.
- Don't drop-shadow panels on the editor screen — flat + hairline reads as precision tool, shadows read as generic dashboard template.
