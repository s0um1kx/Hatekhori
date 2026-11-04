# Hatekhori (হাতে খড়ি) — Site Architecture & URL Hierarchy

> **Architecture Philosophy:** Focused, flat, highly indexable hub-and-spoke structure designed for speed, effortless crawling, and maximum internal PageRank flow.

---

## 1. Visual URL Architecture Tree

```
https://hatekhori.com/
│
├── / (Homepage — Interactive Specimen, Value Proposition, Studio Trigger)
│
├── /studio (Web Studio / Glyph Processing Interface)
│
├── /sheets/ (Guideline Sheet Hub — High Download & Image Search Surface)
│   ├── /bengali (A4 Sheet, Character Guide, Stroke Sequence)
│   ├── /hindi (Devanagari A4 Sheet, Matra Alignment Guide)
│   └── /english (Latin A–Z/0–9 Test Sheet)
│
├── /scripts/ (Script-Specific Linguistic Hubs — Pure SEO Moat)
│   ├── /bengali (Bengali Handwriting Typography, Conjuncts, Glyph Set)
│   ├── /hindi (Devanagari Script Engine, Shirorekha Continuous Rules)
│   └── /english (Latin Pipeline & OpenType Export Capabilities)
│
├── /compare/ (High-Converting Competitor & Alternative Hub)
│   ├── /calligraphr-alternative (Primary Alternative Landing Page)
│   ├── /hatekhori-vs-calligraphr (1:1 Head-to-Head Technical Breakdown)
│   ├── /hatekhori-vs-fontcrafter (Why We Focus on Indic vs. English Ecosystems)
│   └── /best-handwriting-font-generators (Comprehensive 2026 Category Roundup)
│
├── /guides/ (Technical & How-To Content Hub — Informational Authority)
│   ├── /how-to-turn-handwriting-into-font (Pillar Guide)
│   ├── /install-custom-font-figma-canva (Designer Workflow)
│   ├── /install-custom-font-mac-windows (Operating System Installation)
│   ├── /bengali-typography-conjuncts (Linguistic Deep Dive)
│   └── /devanagari-font-kerning-rules (Typographic Precision)
│
├── /archive/ (Digital Handwriting Preservation Stories & Cultural Archive)
│   └── /preserving-family-handwriting (Emotional Persona Target)
│
├── /legal/
│   ├── /privacy (Strict Zero-Data Retention & EXIF-Stripping Policy)
│   ├── /terms (Open Access & Personal Font Ownership Guarantee)
│   └── /security (Content Guardrails & Abuse Contact)
│
├── /llms.txt (Standardized markdown documentation for AI agents & GEO)
└── /sitemap.xml (Semantic XML Sitemap)
```

---

## 2. Page Specifications & Content Pillars

### Pillar 1: The Core Atelier (`/` & `/studio`)
- **Primary Keyword:** `handwriting font generator`, `turn handwriting into font`
- **Role:** High-conversion conversion engine. Features interactive live preview canvas, sample script toggles (Bengali / English / Hindi), and instant access to download sheets or launch studio.

### Pillar 2: Competitor & Alternative Silo (`/compare/*`)
- **Primary Keywords:** `calligraphr alternative`, `calligraphr vs`, `free handwriting font generator no subscription`
- **Role:** Bottom-of-funnel conversion. Directly targets users looking to switch or seeking non-subscription alternatives.
- **Internal Linking:** Every comparison page links directly to the `/sheets/` downloads and the `/studio` launch button.

### Pillar 3: Indic Script Hubs (`/scripts/*`)
- **Primary Keywords:** `bengali handwriting font maker`, `hindi handwriting font generator`, `devanagari custom font maker`
- **Role:** Uncontested organic traffic. Educates searchers on how complex Indic conjuncts and vowel signs (*matras*) are accurately recognized and vectorized without losing the author's personal handwriting cadence.

### Pillar 4: Practical Workflow Guides (`/guides/*`)
- **Primary Keywords:** `how to install custom font in figma`, `how to use handwriting font in word`, `convert handwriting to otf`
- **Role:** Broad top-of-funnel acquisition, driving backlinks from design forums (Figma Community, Reddit, UX blogs).

---

## 3. Internal Linking Architecture

```
                    ┌─────────────────────────┐
                    │     Homepage (/)        │
                    └────────────┬────────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           ▼                     ▼                     ▼
   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
   │ /compare/ hub │     │ /scripts/ hub │     │ /sheets/ hub  │
   └───────┬───────┘     └───────┬───────┘     └───────┬───────┘
           │                     │                     │
           │ (Contextual Links)  │ (Linguistic Cross)  │ (Download CTAs)
           ▼                     ▼                     ▼
   ┌───────────────────────────────────────────────────────────┐
   │              /studio (Conversion Destination)             │
   └───────────────────────────────────────────────────────────┘
```

### Internal Linking Rules:
1. **The Rule of Contextual Relevance:** Every blog guide must contextually link to the relevant `/sheets/*` download within the first 150 words.
2. **Breadcrumb Hierarchy:**  
   `Home > Comparisons > Calligraphr Alternative`  
   `Home > Scripts > Bengali Handwriting Font`  
   All breadcrumbs use valid `BreadcrumbList` JSON-LD schema.
3. **Anchor Text Integrity:** Avoid generic "click here" or "learn more." Always use descriptive, keyword-rich anchor text (e.g., *"download the Bengali handwriting guideline sheet"*, *"view the Calligraphr vs Hatekhori comparison matrix"*).

---

## 4. XML Sitemap & Quality Gates

### Quality Gates for Indexation:
- **Zero Thin Pages:** Every indexable URL must have > 800 words of unique, non-boilerplate content (with the exception of `/studio` which is an interactive web app).
- **Canonical Consistency:** All URLs must be self-canonicalized, HTTPS, lowercase, and without trailing slashes.
- **Sitemap Partitioning:**
  ```xml
  <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap><loc>https://hatekhori.com/sitemap-core.xml</loc></sitemap>
    <sitemap><loc>https://hatekhori.com/sitemap-compare.xml</loc></sitemap>
    <sitemap><loc>https://hatekhori.com/sitemap-scripts.xml</loc></sitemap>
    <sitemap><loc>https://hatekhori.com/sitemap-guides.xml</loc></sitemap>
  </sitemapindex>
  ```
