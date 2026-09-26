# Hatekhori — Brand Colour Guideline

*Companion to hatekhori-layout-grid.md, PRD.md and BRAND.md. Locked palette — implement these values exactly, don't approximate.*

## Locked palette (from the Ctrl+ brand board)

| Role | Hex | Usage |
|---|---|---|
| **Stage / paper** | `#F2ECE1` | Page background, panel surface — the "paper" everywhere. Never pure white (`#FFFFFF`). |
| **Ink (primary)** | `#0034D3` | All text, strokes, primary buttons, active/selected states, the character-grid selection. This is the one colour that carries the brand — it does the work a logo usually does. |
| **Ink (deep)** | `#003087` | Reserved for emphasis on top of the primary blue — pressed/active states, headings sitting on a blue fill, the darkest stop when blue sits on blue. |
| **Tint** | `#99CCFF` | Light wash only — hover backgrounds, disabled/inactive fills, the unselected side of a toggle. Don't set body text below 14px on this tint; contrast gets thin. |

## The rule behind the palette

One saturated colour (`#0034D3`) does the brand-carrying work. Everything else — the paper, the tint, the deep accent — is a supporting stop of that *same* blue family, not a competing hue. No third colour, no gradients, no decorative accent added "for variety." If you need a status colour later (error/success), add the smallest possible palette on top of this — don't let it become a fifth brand colour.

## Where the two colour registers apply

- **Editor / tool screens**: `#0034D3` on `#F2ECE1`, hairline borders, flat — no shadows, no decoration. This is the instrument-panel read (see layout-grid.md §5).
- **Marketing / landing surfaces**: same palette, but the Ctrl+ board's loose hand-drawn squiggle motif (the `@`, spirals, doodles) is fair game here as background texture or empty-state illustration. Keep it off the editor screen — decorative linework fights the precision-tool feel the product actually needs.

## Do / don't

**Do**
- Use `#0034D3` as the single accent everywhere an accent is needed — buttons, links, active states, selection.
- Keep `#F2ECE1` as the only background tone for product surfaces.
- Use `#99CCFF` only for "quieter than default" states (hover, inactive, unselected) — never as a primary fill.

**Don't**
- Don't introduce a second saturated hue anywhere in the product.
- Don't use pure black or pure white — everything routes through this four-value palette.
- Don't let the squiggle/doodle motif appear inside the editor/tool UI.
