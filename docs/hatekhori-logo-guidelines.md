# Hatekhori (হাতে খড়ি) — Logo & Brand Asset Guidelines

> Compact production guide for the Hatekhori visual identifier: geometry, lockups, color tokens, and asset deployment.

---

## 1. The Brand Mark: "The Atelier H"

- **Concept**: An architectural Latin letter 'H' cut from a slate block, bridged by a 45° chisel chalk stylus pointing downward to paper.
- **Role**: Identifier for an Indic-first typeface atelier and handwriting preservation engine.
- **Core Versions (in `frontend/`)**:
  - `logo.svg` / `logo-white.svg`: Primary brand lockup for website headers, documentation, and print specimens.
  - `logo-symbol.svg` / `logo-symbol-white.svg`: Standalone 256×256 master vector symbol.
  - `favicon.svg`: Modern adaptive vector favicon with native `@media (prefers-color-scheme: dark)` color switching.
  - `favicon.ico` / `favicon-32x32.png`: Standard browser tab favicons.
  - `apple-touch-icon.png`: Chalk-white mark on `#0D0D0D` squircle tile (22% corner radius).

---

## 2. Clear Space & Proportions

- **Clear Space Unit (X)**: Equal to the width of one vertical slate pillar (52 units on a 256 grid, or roughly 20% of symbol height).
- Maintain at least **1X** unobstructed margin on all four sides of any lockup or symbol.
- No text, UI controls, or busy imagery should intrude into the clear space zone.

```
       +-----------------------------------------+
       |                  [ 1X ]                 |
       |        +-----------------------+        |
[ 1X ] | [ 1X ] |   [ HATEKHORI LOGO ]  | [ 1X ] | [ 1X ]
       |        +-----------------------+        |
       |                  [ 1X ]                 |
       +-----------------------------------------+
```

---

## 3. Minimum Sizing

| Format | Environment | Minimum Size | Recommended File |
| :--- | :--- | :--- | :--- |
| **Horizontal Lockup** | Web / Mobile | 120 px width | `frontend/logo.svg` |
| **Horizontal Lockup** | Print | 30 mm width | Vector PDF / SVG |
| **Symbol Only** | Web UI / Avatar | 24 × 24 px | `frontend/logo-symbol.svg` |
| **Browser Favicon** | Browser Tabs | 16 × 16 px | `frontend/favicon.svg` or `favicon.ico` |
| **Touch / PWA Icon** | Mobile Homescreen | 180 × 180 px | `frontend/apple-touch-icon.png` |

---

## 4. Color Palette & Contrast Pairing

| Color Token | Hex | RGB | Role in Identity |
| :--- | :--- | :--- | :--- |
| **Slate Black** (`--fg` / `--bg-dark`) | `#0D0D0D` | `rgb(13, 13, 13)` | Primary mark fill on light paper; dark mode background slate. |
| **Chalk White** (`--bg` / `--fg-dark`) | `#F0F0F0` | `rgb(240, 240, 240)` | Reversed mark fill on dark slate / chalkboard. |
| **Pure Paper** (`--bg-light`) | `#FFFFFF` | `rgb(255, 255, 255)` | Light mode canvas surface. |
| **Vermilion Alert** (`--red`) | `#D2271B` | `rgb(210, 39, 27)` | Intentional ritual alert accent (seals, errors, destructives). |

### Approved Background Pairs:
1. **Light Mode**: `#0D0D0D` mark on `#FFFFFF` paper surface (19.2:1 contrast ratio, WCAG AAA).
2. **Dark Mode**: `#F0F0F0` mark on `#0D0D0D` deep slate chalkboard (17.5:1 contrast ratio, WCAG AAA).
3. **App Tile**: `#F0F0F0` mark enclosed within `#0D0D0D` rounded squircle tile.

---

## 5. Web & Application Deployment

### HTML `<head>` Integration:
```html
<!-- Adaptive SVG Favicon (automatic dark/light theme detection) -->
<link rel="icon" type="image/svg+xml" href="favicon.svg" />

<!-- Fallback PNG Favicons -->
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png" />
<link rel="icon" type="image/png" sizes="16x16" href="favicon-16x16.png" />
<link rel="shortcut icon" href="favicon.ico" />

<!-- Apple Touch & PWA Manifest -->
<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png" />
<link rel="manifest" href="site.webmanifest" />
<meta name="theme-color" content="#0D0D0D" />
```

### In-App Navigation (`index.html`):
```html
<a href="#" class="brand" aria-label="Hatekhori Home">
  <svg class="brand-logo" width="22" height="22" viewBox="0 0 256 256" fill="currentColor" aria-hidden="true">
    <path d="M44 36H96V108H160V36H192L212 56V220H160V148L128 180L96 148V220H44Z"/>
  </svg>
  <span>Hatekhori</span>
</a>
```

---

## 6. Rules & Misuse

- **Do not stretch, squeeze, or alter aspect ratios.**
- **Do not introduce artificial gradients, glow effects, or drop shadows.**
- **Do not recolor the mark outside the approved slate, chalk, and vermilion palette.**
- **Do not rotate the mark or change the 45° chisel apex geometry.**
- **Do not type out the wordmark using live fonts for official lockups** — always use the outlined SVG master paths in `frontend/logo.svg`.
