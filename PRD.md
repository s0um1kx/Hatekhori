# Hatekhori (হাতে খড়ি) — Product Requirements Document v2

> Supersedes the original PRD. Rewritten after brand/market validation research and a direct competitor study (see BRAND.md for the full reasoning behind these decisions).

## 1. Overview

**Hatekhori** ("holding the chalk") is named after the traditional Bengali ritual marking a child's first step into formal education. Hatekhori turns a person's actual handwriting into a real, installable, ownable font — starting with Bengali and Hindi, the scripts no existing tool treats as first-class.

**What changed from v1:** Hatekhori is not "a handwriting-to-font website that will eventually support Indic scripts." It is an Indic-first typeface atelier that happens to validate its engineering pipeline in English first, privately, before anything ships publicly. See §4 for why, and §4a for what competitor research confirmed about that decision.

**Format:** Website (not a native app).

**Primary audience:** Indian developers and designers — proud of their own script, technical enough to tolerate an early build, invested enough in the idea to spread it. (Full persona and competitor reasoning in BRAND.md.)

---

## 2. Vision

**One line:** Hatekhori preserves human handwriting — starting with the scripts the world's font tools forgot — as ownable, installable type, in an era where AI can fake handwriting for everyone but can't fake yours.

**Three horizons:**
- **Now:** A working pipeline that turns real handwriting into a real font, without looking like a ransom note.
- **Next:** A personal type system — your font, live on your own site/portfolio/Figma files, not just a downloaded file.
- **Later:** An archive — family handwriting, a first teacher's alphabet, a grandparent's script — preserved as usable type before it's lost.

---

## 3. Problem & Why Now

Two forces, both real and evidenced, not just a hunch:
- **Anti-AI-slop backlash:** 2026 design commentary consistently names "Anti-AI Crafting" — the deliberate rejection of AI's hyper-polished look — as the defining trend of the year.
- **Indic scripts are a real technical gap, not just an underserved market.** A text-ready Bengali font requires a glyph closure (base forms + conjuncts + matras + half-forms) that can run past 1,000 glyphs — an order of magnitude beyond a Latin A–Z/a–z/0–9 set. Every mainstream handwriting-to-font tool is Latin-script-only. This is Hatekhori's actual, defensible wedge.

---

## 4. Build Order (the decision that changed everything)

**Technical sequencing and brand sequencing are deliberately different.**

- **Internally, first:** Build and validate the core pipeline — capture → cleanup → vectorize → metrics (baseline, x-height, kerning) → usable font file — using **English** as the test script, because it's small (~60–90 glyphs) and cheap to iterate on. This phase is never shown publicly as "the product."
- **Publicly, first:** Once the pipeline clears its own quality bar (§9), the first script Hatekhori launches with — the one anyone outside the builder ever sees — is **Bengali and/or Hindi**.

### 4a. What the competitor study confirmed

A direct study of the existing handwriting-to-font market (Calligraphr, YourFonts, Fontself, iFontMaker, and critically **FontCrafter**) found that FontCrafter is not just a free English tool — it's a full ecosystem: the font generator (500+ glyphs, ligatures, contextual alternates, color-font effects, OTF/TTF/WOFF2/Base64 export, 100% local/private, no account) plus a family of companion apps (QuoteCrafter, CardCrafter, WeddingCrafter, etc.) and a phone app for using the font everywhere, already positioned explicitly against Calligraphr's subscription model.

**This is a second, independent reason English is validation-only, never the product:** even a well-built English offering from Hatekhori would be a slower, paid second copy of something free, private, and feature-complete that already exists. There is no version of "compete on English handwriting-to-font" that isn't a losing fight. Bengali/Hindi conjunct support is the one thing none of these tools — legacy or free-ecosystem — currently do. That is the only uncontested ground, and Hatekhori's entire engineering effort belongs there.

---

## 5. Core Flow (single path, no split modes)

**v1 had two capture modes (Quick / Precision). This is cut.** There is one flow:

1. User is shown one well-designed guideline sheet — covering the target script's required character set (for English: A–Z/a–z/0–9, internal validation only; for Bengali/Hindi: base consonants, vowel signs, and the conjunct set the engineering phase determines is achievable at launch quality).
2. User writes on it — either printed, or on any paper following the same layout.
3. Capture happens via **QR code + phone camera** (auto-corrects perspective/lighting/crop) or **direct upload** of an existing photo.
4. System validates the upload is actually a filled guideline sheet, with a clear, non-alarming error message if not.
5. Handwriting is processed into a real font file.
6. User previews the result on a **visual canvas** with a **Human / Machine toggle**:
   - **Human:** the rendered font, shown naturally (e.g., on a mock portfolio/card).
   - **Machine:** the underlying technical representation — vector paths / font data.

---

## 6. Upload Requirements

- **Accepted formats:** JPG, PNG, HEIC. PDF: decide during Milestone 1 based on how much it complicates validation.
- **Size limit:** to be set once real file sizes from the capture flow are known.
- **Validation:** must reject non-guideline-sheet uploads with a clear, on-brand error.

### 6a. Content & Upload Guardrails

**This is infrastructure, not brand differentiation** — it lives quietly underneath the product, not in the craft narrative (see BRAND.md). It exists precisely because the product is accountless (§10): with no identity layer to ban, throttle, or trace a bad actor, every safeguard has to live in the upload pipeline itself.

Risk categories this needs to cover: illegal imagery uploaded as a fake "handwriting sample," someone submitting another person's handwriting/signature (a forgery concern, not just a misuse one), offensive content written on the sheet itself, resource abuse (decompression bombs, oversized dimensions, scripted flooding), and privacy leakage (phone photos carrying EXIF GPS data by default).

**Baseline — required before any UI ships, even internally:**
- Real content-sniffing on file bytes, not just extension/MIME header
- Hard caps on file size *and* pixel dimensions
- Strip EXIF metadata on ingest, always, no exceptions
- The existing guideline-sheet structural validation (§5/§6) does double duty here: a genuine guideline-sheet photo has a specific shape most junk or inappropriate images won't match, so this check is a security property as well as a UX one

**Required before the Bengali/Hindi public launch — non-negotiable:**
- An automated image-safety classifier (NSFW/violence/CSAM-signal detection) gating entry *before* anything reaches vectorization or storage — hard reject, not a soft warning, with the rejected image's hash logged for abuse review rather than silently discarded
- A lightweight, non-identity consent checkbox at submission ("this is my own handwriting and I have the right to submit it") — a legal/provenance safeguard, not an account, so it doesn't reopen the auth question
- IP- or session-based rate limiting, since there's no account to throttle instead
- Raw uploaded photos are never displayed publicly by default — only the derived font/glyphs are shown, shrinking the blast radius of anything that slips past the classifier
- A visible, no-account-required abuse/takedown contact (a plain email link), since there's no user to ban — only a way for someone to flag "that's my handwriting/signature and I didn't consent"

**Deferred — only relevant if a public gallery/showcase feature is ever built:**
- Human moderation queue for classifier-borderline cases
- Separate consent for "process this for me" vs. "make this visible to others"

### 6b. Data Retention & Privacy

**An extension of §6a's infrastructure, not a separate legal afterthought.** Because there's no account system, retention rules and deletion have to be designed around the pipeline and session, not a user record.

| Data | Handling | Retention |
|---|---|---|
| Raw uploaded photo | Processed (validate → vectorize → metrics) | Deleted immediately on successful font generation; deleted within 24h regardless if generation fails |
| Generated font + provenance data (§7) | Held so the user can (re)download it | Fixed window (e.g. 30 days) via the session/download link, then purged server-side — not indefinite |
| Consent record (§6a checkbox) | Tied to the same session as the photo/font | Purged together with the underlying submission |
| Rejected/flagged upload hashes (§6a classifier) | Hash only, never the image, for abuse-pattern detection | Rolling window (e.g. 90 days) unless part of an active abuse investigation |
| Aggregate/anonymized usage stats | No personal or image data | Indefinite — product telemetry, exempt from the rest of this table |

**The core promise:** uploaded handwriting is never used to train any model, Hatekhori's or anyone else's — no opt-out needed because there is no opt-in path either. If handwriting samples are ever used to improve the pipeline itself, that requires a separate, explicit opt-in at submission — never bundled into the §6a processing consent.

**Deletion without an account:** the §6a abuse/takedown contact doubles as the deletion request path — someone emails describing roughly when/what they submitted, support locates and purges by session metadata, no identity system required. State this explicitly in the on-site policy rather than leaving it implicit.

**Self-hosted disclaimer:** since Hatekhori is open source, this retention model describes the hosted instance only — a self-hosted deployment is under its own operator's terms, and the policy should say so.

---

## 7. Output / System (not just a file — but scoped to the Indic product only)

Give a system, not a file: font file(s), a ready-to-paste web snippet, a Figma-installable version if in scope, some marker of provenance (name, date). **Important scope note post-competitor-study:** this system layer is built for the Bengali/Hindi output, not as an attempt to match FontCrafter's English app family (QuoteCrafter, PenSend, etc.) feature-for-feature — that fight is already lost and not worth entering. None of this needs to be in Milestone 1.

---

## 8. Business Model

**Open source, no payment gateway for now.** No monetization layer is being built at this stage — the project ships as open source with no checkout, no license key, no paid tier. If a business model is introduced later, the standing constraint carried over from earlier thinking is: **one-time payment, not subscription** — a subscription for access to *your own handwriting* is a trust-breaking model in this category, a documented complaint against the incumbent. That remains the fallback direction if/when monetization is revisited, but it is explicitly not being built now.

---

## 9. Milestone 1 — Definition of Done

Milestone 1 is **not** "the English website." It is:

**The pipeline kill-test:** Take a small batch of real, varied handwriting photos (different pens, lighting, handwriting neatness) through capture → vectorize → metrics → font export, in English. Evaluate: does the output look like a font a designer would actually use, or a ransom note?

- **Pass →** proceed to building the real guideline-sheet UI and capture flow (still privately, still English), then begin Bengali/Hindi glyph-set scoping in parallel.
- **Fail →** stop. Fix the vectorization/metrics pipeline before writing any more UI code.

---

## 10. Non-Goals

- Not a generic AI-handwriting-font generator — it's specifically about a person's **own** handwriting as personal, ownable output.
- Not a native mobile app — web-first.
- Not, at launch, a tool marketed around English handwriting — English is internal validation only, per §4.
- Not two capture tiers of differing quality — per §5.
- **Not an attempt to out-feature FontCrafter's free English ecosystem** — no companion-app family, no competing on "free," no leading with "not AI handwriting" as the sole differentiator. That ground is already occupied and already lost; Hatekhori's differentiation is script correctness for Bengali/Hindi, not feature parity in English.
- **Not an accounted-for product.** No auth, no login, no signup wall, no user accounts. With no payment gateway and no re-download/provenance-to-a-paying-user problem to solve, there is no structural reason to gate any part of the core flow (§5) behind identity. Provenance (name, date — §7) is a plain form field at export time, not an account system. Revisit only if a future "Next"-horizon feature (a persistent, live-on-your-site type system) genuinely requires it — and even then, prefer a self-sovereign, exportable state (a project file the user keeps) over a login wall.

---

## 11. Open Questions

- Exact character/conjunct set for Bengali/Hindi launch — determined by what the pipeline can actually render well.
- Upload size limit and PDF support — deferred to real data from Milestone 1.
- Exact pricing tiers — deferred until output quality is proven.
- Whether Telugu is a second-wave Indic script or stays out of scope.
