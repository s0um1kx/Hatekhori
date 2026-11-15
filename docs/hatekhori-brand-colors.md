# Hatekhori (হাতে খড়ি) — Brand Colour & Visual Guidelines

*Companion to `hatekhori-layout-grid.md`, `PRD.md`, and `BRAND.md`. Locked palette and design tokens — implement these exact values across all frontend stylesheets and components.*

---

## 1. The Design Philosophy: Chalk, Slate, and Paper

Hatekhori ("holding the chalk") is rooted in the traditional ritual marking a child's first step into literacy — drawing their very first letter with white chalk on a slate stone.

The brand's visual identity reflects this tactile, cultural origin:
- **No artificial AI gradients** or trendy purple SaaS palettes.
- **High-contrast, unadorned editorial typography**: the clarity of ink on paper, the timelessness of chalk on a chalkboard.
- **Instrument-level precision**: 1px hairline borders, monochrome surfaces, and subtle, intentional accents.

---

## 2. Locked Design Tokens & Color Palette

The interface supports both **Light Mode (Paper & Charcoal Ink)** and **Dark Mode (Chalkboard & Deep Slate)** via standard CSS custom properties.

### Light Mode (Default — Clean Paper Atelier)

| Token | Hex | Usage & Role |
| :--- | :--- | :--- |
| `--bg` | `#FFFFFF` | Primary canvas and page background. Clean, bright paper surface. |
| `--fg` | `#111111` | Primary text, titles, deep charcoal ink, primary button fills. |
| `--muted` | `#666666` | Secondary body text, sub-labels, metadata readouts, inactive chevrons. |
| `--border` | `#E5E5E5` | Structural 1px hairline boundaries, card edges, divider rules. |
| `--subtle` | `#F7F7F7` | Inset backgrounds, secondary containers, inactive tabs, table zebra stripes. |
| `--accent` | `#111111` | Primary interactive elements, selected pill tags, active focus rings. |
| `--accent-hover` | `#333333` | Hover fill on primary buttons and interactive elements. |
| `--red` | `#D2271B` | Intentional alert accent: destructive actions, remove photo, error states. |

### Dark Mode (Chalkboard & Deep Slate)

Automatically activated via `@media (prefers-color-scheme: dark)`:

| Token | Hex | Usage & Role |
| :--- | :--- | :--- |
| `--bg` | `#0D0D0D` | Primary canvas background — deep slate stone / chalkboard. |
| `--fg` | `#F0F0F0` | Primary text, titles, high-contrast chalk-white letterforms. |
| `--muted` | `#888888` | Muted chalk dust labels, secondary copy, inactive elements. |
| `--border` | `#242424` | Hairline panel borders, card dividers. |
| `--subtle` | `#141414` | Recessed slate containers, inactive pill buttons, dropzone idle plate. |
| `--accent` | `#F0F0F0` | High-contrast chalk-white buttons and active tab indicators. |
| `--accent-hover` | `#D0D0D0` | Hover fill on chalk-white buttons. |
| `--red` | `#E03529` | High-visibility alert accent in dark mode. |

---

## 3. Atmospheric Surfaces & Cinematic Accents

For cinematic moments — the **Hero Chalk Video Card** and the **Atmospheric Call-to-Action (CTA) Banner** — Hatekhori uses a controlled deep-slate atmosphere:

```css
/* Atmospheric CTA Banner Background */
background: 
  radial-gradient(ellipse 70% 60% at 50% 50%, rgba(38, 38, 38, 0.85) 0%, rgba(13, 13, 13, 0.98) 100%),
  #0D0D0D;
```

- **Video Backdrop:** `hatekhori-chalk.mp4` with poster `hatekhori-chalk-poster.jpg`, depicting chalk writing on slate.
- **Glassmorphic Touch:** `.btn-glass` provides subtle glass surface depth on primary buttons without sacrificing readability.

---

## 4. Typographic Palette

Typography is central to Hatekhori's identity as a type foundry and atelier:

| Family | Stack | Role |
| :--- | :--- | :--- |
| **Serif (Headings)** | `"Instrument Serif", Georgia, serif` | Editorial headlines, landing hero title, section headers. Gives the brand literary authority and craft warmth. |
| **Sans (Interface)** | `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif` | Clean, neutral UI controls, body copy, instructions, navigation, forms. |
| **Monospace (Data)** | `"DM Mono", monospace` | Technical indicators, cell counts, Unicode codepoints (e.g., `U+0985`), engine progress states, file sizes. |
| **Handwriting (Latin)** | `"Hatekhori Latin", "Hatekhori", "Kalam", cursive` | Specimen preview for English handwriting fonts. |
| **Handwriting (Bengali)** | `"Hatekhori Bangla", "Tiro Bangla", serif` | Specimen preview for Bengali handwriting fonts. |
| **Handwriting (Hindi)** | `"Hatekhori Hindi", "Tiro Devanagari Hindi", serif` | Specimen preview for Hindi handwriting fonts. |

---

## 5. Motion & Transitions

- **Primary Easing:** `--ease-out: cubic-bezier(0.23, 1, 0.32, 1);`
- **Fast Duration:** `--duration-fast: 160ms;`
- **Button Feedback:** Micro-shift on hover (`transform: translateX(3px)` for forward arrows, `translateX(-3px)` for back buttons).
- **Reduced Motion:** Always respect `prefers-reduced-motion: reduce` by disabling transitions and video backgrounds.

---

## 6. Do / Don't

### Do
- Maintain high contrast between foreground and background in both light and dark themes.
- Use `Instrument Serif` exclusively for large display statements and section headings.
- Keep hairline borders 1px solid (`var(--border)`) without heavy drop shadows.
- Keep error/alert states strictly within the single `--red` token.

### Don't
- Never introduce saturated blues, purples, or multicolored gradients into the product UI.
- Never use cartoonish emojis in interface buttons, labels, or toasts — use clean SVGs (Lucide style).
- Never allow low-contrast gray text on dark surfaces (body text must meet WCAG AAA / AA standards).
