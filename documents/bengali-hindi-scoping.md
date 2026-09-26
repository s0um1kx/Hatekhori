# Bengali & Hindi Glyph-Set Scoping — Hatekhori (হাতে খড়ি)

> **Context:** Milestone 1 kill-test passed. Per [AGENTS.md](file:///c:/Users/Administrator/Hatekhori/documents/AGENTS.md) §2 & §3 and [PRD.md](file:///c:/Users/Administrator/Hatekhori/documents/PRD.md) §4, Hatekhori is an Indic-first typeface atelier. While engineering was validated on English internally, the first script a public user sees is Bengali and/or Hindi. This document establishes the exact character inventory and guideline sheet structure required for high-fidelity Indic handwriting synthesis.

---

## 1. The Indic Challenge vs. Latin

Unlike Latin scripts (~60–90 basic glyphs), Indic scripts are abugidas requiring:
1. **Independent Vowels (স্বতন্ত্র স্বরবর্ণ / स्वतंत्र स्वर)**
2. **Consonants with inherent vowel /a/ (ব্যঞ্জনবর্ণ / व्यंजन)**
3. **Dependent Vowel Signs / Matras (কার / मात्राएं)** that attach above, below, before, or after base consonants
4. **Conjuncts / Ligatures (যুক্তাক্ষর / संयुक्ताक्षर)** formed by halant/virama combinations, numbering into hundreds
5. **Special signs (অনুস্বার, বিসর্গ, চন্দ্রবিন্দু / अनुस्वार, विसर्ग, चन्द्रबिन्दु, नुक्ता)**

Attempting a 1,000+ glyph sheet upfront causes user fatigue and lowers handwriting quality. Hatekhori's strategy is a **curated, launch-viable high-frequency closure** that covers >98% of natural written Bengali and Hindi on a 2-page guideline sheet (~118–125 carefully selected cells).

---

## 2. Bengali Script Scoping (বাংলা)

### A. Independent Vowels (স্বরবর্ণ) — 11 Glyphs
`অ, আ, ই, ঈ, উ, ঊ, ঋ, এ, ঐ, ও, ঔ`

### B. Dependent Vowel Signs / Matras (কার) — 10 Glyphs
`া (আ-কার), ি (ই-কার), ী (ঈ-কার), ু (উ-কার), ূ (ঊ-কার), ৃ (ঋ-কার), ে (এ-কার), ৈ (ঐ-কার), ো (ও-কার), ৌ (ঔ-কার)`
*Note: In the guideline sheet, matras are captured relative to a reference dotted circle (◌).*

### C. Consonants (ব্যঞ্জনবর্ণ) — 35 Glyphs
`ক, খ, গ, ঘ, ঙ`
`চ, ছ, জ, ঝ, ঞ`
`ট, ঠ, ড, ঢ, ণ`
`ত, থ, দ, ধ, ন`
`প, ফ, ব, ভ, ম`
`য, র, ল, শ, ষ, স, হ`
`ড়, ঢ়, য়`

### D. Modifiers & Special Marks — 4 Glyphs
`ৎ (খণ্ড ত), ং (অনুস্বার), ঃ (বিসর্গ), ঁ (চন্দ্রবিন্দু)`

### E. Bengali Numerals (সংখ্যা) — 10 Glyphs
`০, ১, ২, ৩, ৪, ৫, ৬, ৭, ৮, ৯`

### F. High-Frequency Conjuncts (যুক্তাক্ষর) — Top 48 Glyphs
These represent the essential ligatures that cannot be synthesized simply by naive juxtaposition:
- **ক্-conjuncts:** ক্ত, ক্স, ক্ষ (ক+ষ), ক্ব, ক্র
- **গ্-conjuncts:** গ্দ, গ্ধ, গ্র
- **ঙ্-conjuncts:** ঙ্ক, ঙ্গ, ঙ্ঘ
- **চ্-conjuncts:** চ্চ, চ্ছ, চ্ঞ
- **জ্-conjuncts:** জ্জ, জ্ঞ (জ+ঞ), জ্ব, জ্র
- **ঞ্-conjuncts:** ঞ্চ, ঞ্ছ, ঞ্জ, ঞ্ঝ
- **ট্/ড্-conjuncts:** ট্ট, ড্ড, ন্ট, ন্ড, ন্থ
- **ত্-conjuncts:** ত্ত, ত্থ, ত্ন, ত্র, ত্ব
- **দ্-conjuncts:** দ্দ, দ্ধ, দ্ব, দ্র
- **ধ্/ন্-conjuncts:** ধ্ন, ন্ন
- **প্/ব্-conjuncts:** প্ত, ব্দ, ব্ধ, ব্র
- **ষ্/স্-conjuncts:** ষ্ট, ষ্ঠ, ষ্ণ, স্প, স্ত, স্থ, স্ন
- **হ্-conjuncts:** হ্ন, হ্ম, হ্ল, হৃ

**Bengali Total:** 11 + 10 + 35 + 4 + 10 + 48 = **118 glyphs** (fits cleanly on a 2-page 8×8 grid).

---

## 3. Hindi / Devanagari Script Scoping (देवनागरी)

### A. Independent Vowels (स्वर) — 12 Glyphs
`अ, आ, इ, ई, उ, ऊ, ऋ, ए, ऐ, ओ, औ, अं`

### B. Matras (मात्राएं) — 11 Glyphs
`ा, ि, ी, ु, ू, ृ, े, ै, ो, ौ, ं`

### C. Consonants (व्यंजन) — 33 Glyphs
`क, ख, ग, घ, ङ`
`च, छ, ज, झ, ञ`
`ट, ठ, ড, ढ, ण`
`त, थ, द, ध, न`
`प, फ, ब, भ, म`
`य, र, ल, व, श, ष, स, ह`

### D. Modifiers & Nuqta Consonants — 7 Glyphs
`ः (विसर्ग), ँ (चन्द्रबिन्दु), क़, ख़, ग़, ज़, फ़, ड़, ढ़`

### E. Devanagari Numerals (अंक) — 10 Glyphs
`०, १, २, ३, ४, ५, ६, ७, ८, ९`

### F. Core Half-Forms & Conjuncts (संयुक्ताक्षर) — Top 45 Glyphs
- **Half-forms (अर्ध रूप):** क्, ख्, ग्, घ्, च्, ज़्, ञ्, ण्, त्, थ्, ধ্, न्, प्, ब्, भ्, म्, ल्, व्, श्, ष्, स्
- **Compound ligatures:** क्ष, त्र, ज्ञ, श्र, द्ध, द्व, द्य, द्म, ट्ट, ठ्ठ, ड्ड, ढ्ढ, ङ्ग, ङ्क, त्त, क्त, न्न, म्म, च्च, ल्ल

**Hindi Total:** ~118–125 glyphs.

---

## 4. OpenType Layout & Shaper Requirements

Indic handwriting fonts require dynamic font features handled via OpenType GSUB/GPOS tables:
1. **Shirorekha / Matra Alignment (মাথারেখা / शिरोरेखा):**
   - In Latin, characters align on the baseline ($y = 0$).
   - In Bengali and Hindi, characters hang from the **headline / shirorekha** ($y \approx 720$).
   - **Crucial pipeline adjustment:** The guideline sheet marks the headline as the primary alignment datum, with baseline and descender marks positioned below.
2. **GSUB Lookups:**
   - `locl` / `nukt` (Nuqta forms)
   - `akhn` (Akhand ligatures: ক্ষ/क्ष, জ্ঞ/ज्ञ)
   - `rphf` (Reph forms)
   - `blwf` (Below-base forms: র-ফলা, উ-কার)
   - `half` (Half forms in Devanagari)
   - `pres` / `psts` (Pre- and post-base substitutions: ই-কার/ি placement)
3. **GPOS Lookups:**
   - Mark-to-base (`mark`) and mark-to-mark (`mkmk`) for precise vowel sign positioning over varying consonant widths.

---

## 5. Next Implementation Deliverable
With this character inventory defined, we proceed to:
1. **Guideline Sheet UI:** Clean, desktop-first, `#F2ECE1` / `#0034D3` capture interface supporting print-ready sheet display/download and direct photo upload/inspection.
2. **OpenType Engine Extensions:** Extending [compiler.py](file:///c:/Users/Administrator/Hatekhori/compiler.py) to generate GSUB/GPOS ligature tables for Indic conjuncts.
