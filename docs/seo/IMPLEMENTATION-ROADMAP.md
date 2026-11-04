# Hatekhori (হাতে খড়ি) — 4-Phase SEO Implementation Roadmap

> **Target Horizon:** 12 Months  
> **Strategic Objective:** Become the #1 ranked global destination for Indic handwriting typography and the premier non-subscription alternative to Calligraphr.

---

## 1. Phased Execution Roadmap

```
  Phase 1: Foundation (Weeks 1–4)
  ├── Clean Technical SEO, Canonicals, OpenGraph, Core Web Vitals (< 1.1s LCP)
  ├── Structured Data (SoftwareApplication, Organization, WebSite)
  └── High-Converting Core Pages (Homepage, /studio, /sheets downloads)

  Phase 2: Expansion (Weeks 5–12)
  ├── Competitor Silo (/compare/calligraphr-alternative, /compare/hatekhori-vs-calligraphr)
  ├── Script Hubs (/scripts/bengali, /scripts/hindi)
  └── First Wave of Core How-To Guides (Figma, Canva, OS installation)

  Phase 3: Scale (Weeks 13–24)
  ├── Interactive Specimen Gallery & Community Showcase
  ├── Localized Hreflang expansion for native Bengali & Hindi searchers
  └── Strategic Outreach (HasGeek, DesignUp, TypeDrawers, Figma Community)

  Phase 4: Authority (Months 7–12)
  ├── Computational Typography Whitepapers & Indic Ligature Research
  ├── Digital Preservation Partnerships (Cultural heritage archives)
  └── Continuous Drift Monitoring & GEO / AI Engine Answer Optimization
```

---

## 2. Detailed Phase Breakdown

### Phase 1: Foundation & Technical Health (Weeks 1–4)
- [ ] **Audit Current HTML/CSS:** Verify semantic tags (`<header>`, `<main>`, `<article>`, `<footer>`, semantic `<h1>`–`<h6>`).
- [ ] **Metadata Baseline:** Inject unique, optimized `<title>` and `<meta name="description">` tags into all live templates.
- [ ] **OpenGraph & Twitter Cards:** Add high-contrast social cards featuring the signature `#0034D3` ink on `#F2ECE1` paper with real handwriting specimens.
- [ ] **Core Web Vitals Optimization:**
  - Preconnect Google Webfonts (`Instrument Serif`, `Tiro Bangla`, `Tiro Devanagari Hindi`).
  - Ensure zero layout shift on glyph matrix rendering.
  - Optimize client-side vectorization scripts so main thread remains interactive (INP < 50ms).
- [ ] **JSON-LD Schema Foundation:** Implement `Organization`, `WebSite`, and `SoftwareApplication` markup on homepage.
- [ ] **Robots & AI Signals:** Deploy clean `robots.txt` and `/llms.txt` enabling crawl access for Googlebot, Bingbot, PerplexityBot, and GPTBot.

### Phase 2: Interception & Expansion (Weeks 5–12)
- [ ] **Deploy Competitor Comparison Hub:**
  - Launch `/compare/calligraphr-alternative` with 15-point feature matrix.
  - Launch `/compare/hatekhori-vs-calligraphr` targeting direct brand switchers.
  - Launch `/compare/best-handwriting-font-generators`.
- [ ] **Deploy Indic Script Hubs:**
  - Launch `/scripts/bengali` with comprehensive Unicode table (U+0980–U+09FF) and conjunct guides.
  - Launch `/scripts/hindi` highlighting Devanagari shirorekha continuous topline rules.
- [ ] **Guideline Sheet Optimization:**
  - Add dedicated landing pages for `/sheets/bengali`, `/sheets/hindi`, and `/sheets/english` with direct download triggers and image schema.
- [ ] **Search Console Configuration:**
  - Submit XML sitemaps to Google Search Console and Bing Webmaster Tools.
  - Monitor crawl status, indexing coverage, and mobile friendliness.

### Phase 3: Community & Scale (Weeks 13–24)
- [ ] **Interactive Font Specimen Gallery:** Enable users to share read-only specimen cards (e.g., `hatekhori.com/specimen/[font-id]`) generating organic viral backlinks.
- [ ] **Figma Plugin Integration:** Build a companion Figma plugin that pulls generated Hatekhori fonts directly into Figma canvases, with an accompanying landing page ranking for `figma handwriting font plugin`.
- [ ] **Vernacular Multilingual Expansion:**
  - Implement full bilingual pages for Bengali (`bn-IN`, `bn-BD`) and Hindi (`hi-IN`).
  - Deploy accurate `hreflang` headers and language switcher.
- [ ] **Digital PR & Community Seed:**
  - Showcase project on Indian design platforms (DesignUp community, HasGeek, Reddit `r/kolkata`, `r/bangladesh`, `r/india`).

### Phase 4: Long-Term Authority & GEO Dominance (Months 7–12)
- [ ] **Typographic Whitepapers:** Publish computational typography research on automated Bézier contour simplification and Indic ligature synthesis.
- [ ] **Cultural Archival Partnerships:** Partner with regional cultural foundations to digitize historical manuscripts and prominent authors' handwriting into open-source fonts.
- [ ] **Automated SEO Drift Monitoring:** Set up quarterly baseline audits using the `seo-drift` framework to detect accidental regressions in meta tags, schema, or Core Web Vitals.
- [ ] **Generative Engine Optimization (GEO) Auditing:** Test prompts on ChatGPT, Perplexity, Claude, and Google AI Overviews; refine entity citations and structured FAQ markup to ensure Hatekhori is consistently cited as the authority for Indic handwriting fonts.

---

## 3. Risk Mitigation & Dependencies

| Risk Factor | Probability | Impact | Mitigation Strategy |
|---|:---:|:---:|---|
| **Googlebot struggles to render client-side Canvas/WASM** | Low | High | Prerender all marketing, comparison, and guide pages as clean static HTML; keep dynamic canvas strictly inside `/studio`. |
| **Competitors lower prices or introduce free tiers** | Medium | Medium | Hatekhori's moat is Indic script engineering (conjuncts and matras), not just price. No competitor currently has Indic capability. |
| **Thin content flags on template/download pages** | Low | Medium | Every download page includes complete step-by-step instructions, printing recommendations, pen guidelines, and troubleshooting tips (> 1,000 words). |
| **Negative user reviews from low-quality user photos** | Medium | High | Robust client-side validation detects poor lighting, skew, or incomplete sheets immediately *before* processing, preventing user frustration. |
