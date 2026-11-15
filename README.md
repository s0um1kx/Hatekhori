# Hatekhori (হাতে খড়ি)

> Turn your real handwriting into an installable, ownable font. Bengali, Hindi, and English.

Hatekhori ("holding the chalk") is named after the traditional Bengali ritual marking a child's first step into literacy — drawing their first letter on a slate stone. It is an Indic-first digital typeface atelier and handwriting preservation engine that turns written sheets into installable OpenType (`.otf`) fonts.

---

## Documentation & Architecture

- [Product Requirements Document (PRD)](docs/PRD.md) — Product vision, multi-script specs, studio workbench architecture, and pipeline requirements.
- [Agent & Engineering Guidelines](docs/AGENTS.md) — Standing instructions for agents and contributors working in this repository.
- [Brand Strategy](docs/BRAND.md) — Positioning, cultural moat, competitive landscape, pillars, and voice.
- [Brand Colour & Visual Guidelines](docs/hatekhori-brand-colors.md) — Locked design tokens, light/dark mode palette, and typography.
- [Logo & Brand Asset Guidelines](docs/hatekhori-logo-guidelines.md) — Production vectors, clear space, minimum sizing, and favicon specifications.
- [Layout & Grid Guidelines](docs/hatekhori-layout-grid.md) — Responsive grid system, landing showcase, studio workbench layout, and modals.
- [Privacy Policy](docs/privacy-policy.md) — Zero AI model training commitment, data lifecycle, and early deletion procedures.
- [Security Policy & Threat Model](docs/SECURITY.md) — Rate limiting, decompression bomb defense, EXIF scrubbing, and vulnerability disclosure.

---

## Core Features

- **Multi-Script Support:** First-class guideline sheets and font compilation for Bengali (60 cells), Hindi (60 cells), and English (90 cells).
- **Atelier Two-Stage Flow:** Focused two-step studio: (1) Guideline sheet download and preparation → (2) Upload, vectorization, and font compilation.
- **Interactive Specimen & Laboratory:** Live font tester, optical scale waterfall, continuous prose readability block, and clickable character matrix with Unicode codepoint inspector (`U+0985`).
- **Accountless & Private:** No user accounts, no login walls, no tracking cookies, and **zero machine learning model training** on user handwriting.
- **Instant Typography Utility:** Shareable live font preview links, one-click `.otf` download, and ready-to-paste `@font-face` CSS snippets.

---

## License

Open source under the [MIT License](LICENSE).
