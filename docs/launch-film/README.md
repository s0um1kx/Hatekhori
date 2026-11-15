# Hatekhori Launch Film (হাতে খড়ি)

> Built with the `/product-launch-motion` and `/motion-designer` deterministic `seek(t)` pipeline.

A high-fidelity, 20-second product film showcasing **Hatekhori** — an Indic-first digital typeface atelier and handwriting preservation engine that turns written sheets into installable OpenType (`.otf`) fonts for Bengali, Hindi, and English.

---

## Deliverables & Directory Layout

```
docs/launch-film/
├── brief.md                     # Approved creative brief and director decisions
├── README.md                    # Beat map, technical architecture & CLI commands
├── src/                         # Pure seek(t) deterministic film source
│   ├── index.html               # Scrubber & preview stage player
│   ├── film.css                 # Slate & Chalk design tokens
│   ├── core.js                  # Damped harmonic springs & math primitives
│   ├── fx.js                    # Deterministic SVG path tracer, blur & glitch
│   ├── device.js                # Shell geometry morpher & blur content swapper
│   ├── scenes.js                # Master timeline, DOM markup & synced cues
│   ├── assets.js                # Inlined fonts, logos, guideline sheets (0.17 MB)
│   └── main.js                  # Scrubber controls & frame evaluation
├── audio/                       # 120 BPM sound composition & synced SFX
│   ├── edit.wav                 # 44.1 kHz stereo master mix
│   └── edit.m4a                 # AAC 256k master soundtrack
├── dist/                        # Standalone distribution
│   └── hatekhori-launch.html    # Single 100% self-contained inlined file (4.9 MB)
└── out/                         # Rendered outputs
    ├── hatekhori-launch.mp4     # Master 60 fps 1440×1440 MP4 with audio
    ├── hatekhori-launch-loop.mp4# Muted loop version for autoplay
    ├── hatekhori-launch-poster.png # Climax drop hero frame
    ├── hatekhori-launch-post.txt# Two-sentence social launch announcement
    └── t*.png                   # Keyframe scene verification stills
```

---

## Beat Map & Sequence Timing (120 BPM · 20.0s)

| Beat | Timestamp | Scene | Shell Transformation | Visual Action |
| :--- | :--- | :--- | :--- | :--- |
| **B1–B4** | `0.0s – 2.0s` | **The Hook** | Slate Plaque (`740×520`, `r: 24px`) | Hatekhori white logo, tagline, and script tags (`বাংলা`, `हिन्दी`, `English`). Cursor enters and clicks *Launch Font Studio*. |
| **B5–B8** | `2.0s – 4.0s` | **The Sheet** | A4 Paper (`640×900`, `r: 16px`, white) | Four black corner marks, 60 Bengali cells. Cursor clicks *Download Guideline Sheet*. |
| **B9–B14** | `4.0s – 7.0s` | **The Ingest** | Studio Workbench (`1200×800`, `r: 20px`) | Photo drops in; corner crosshairs lock with optical rectification; privacy badge flashes (`Zero AI Training · EXIF Scrubbed`); consent checks; *Generate Font* triggers. |
| **B15–B20** | `7.0s – 10.0s` | **The Vector Lab** | Macro Focus Plate (`700×700`, `r: 22px`) | Bengali vowel **অ** (`U+0985`) raster stroke dissolves into crisp red Bézier curves, showing on-curve anchors, tangent handles, and font metrics. |
| **B21–B28** | `10.0s – 14.0s` | **The Drop (Climax)** | Specimen Deck (`1260×840`, `r: 22px`) | **DROP HIT.** Live cursor types in user's handwriting: *"আমার বাংলা ভাষা"*, switches to Hindi tab *"मेरी लिखावट"*, then English *"Hatekhori Atelier"*. |
| **B29–B34** | `14.0s – 17.0s` | **The Waterfall** | Fluid Stage (`1200×840`, `r: 20px`) | Optical proportions scale smoothly: `48px` → `32px` → `24px` → `18px` body prose. |
| **B35–B40** | `17.0s – 20.0s` | **The Delivery & Loop**| Delivery Card (`740×520`, `r: 24px`) | OpenType `.otf` badge, cursor clicks *Download Font (.otf)*, final brand lockup: *"Your handwriting. Preserved forever."* Closes loop seamlessly back to 0s. |

---

## Technical Principles

1. **One Shape, Never Cut**: The entire film takes place inside a single morphing hero frame (`#shell`) that smoothly changes dimensions, position, corner radius, borders, and background color.
2. **Blur Content Swaps**: When the container morphs, outgoing plates blur and fade early (`filter: blur(...)`); incoming content springs into position once the shell establishes its new geometry.
3. **Closed-Form Damped Springs**: Every layout change and pointer motion uses analytical damped harmonic oscillator step equations (`spring(t, t0, response, damping)`).
4. **Zero Live Clocks or Randomness**: All visual and acoustic properties are pure mathematical functions of time `seek(t)`. No CSS `@keyframes`, no `setTimeout`, no `setInterval`, and no `Math.random()`.

---

## How to Preview & Rebuild

### 1. Interactive Browser Preview
Open `docs/launch-film/src/index.html` (or `docs/launch-film/dist/hatekhori-launch.html`) in Google Chrome or Microsoft Edge. Use the bottom scrubber bar to step frame-by-frame through any millisecond or press `Play` to watch with the synchronized audio track.

### 2. Verify Frame Determinism & Loop
```powershell
node ../../.gemini/config/plugins/motion-designer/skills/motion-designer/scripts/check.mjs docs/launch-film/src/index.html --dist docs/launch-film/dist/hatekhori-launch.html
```

### 3. Rebuild Single Self-Contained HTML
```powershell
python ../../.gemini/config/plugins/motion-designer/skills/motion-designer/scripts/build_single.py docs/launch-film/src/index.html docs/launch-film/dist/hatekhori-launch.html
```

### 4. Render Video (60 FPS MP4)
```powershell
$env:PATH = "C:\KMPlayer;$env:PATH"
node ../../.gemini/config/plugins/motion-designer/skills/motion-designer/scripts/render.mjs video docs/launch-film/src/index.html docs/launch-film/out/hatekhori-launch.mp4 --audio docs/launch-film/audio/edit.m4a
```
