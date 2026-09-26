# Hatekhori (হাতে খড়ি) — Brand Strategy

> This is the resolved version, after arguing six independent strategy passes (including conflicting ones) against each other and against underlying market + competitor research. Where sources disagreed, the disagreement and reasoning are kept below — this document is meant to be argued with again later, not treated as scripture.

---

## 1. The Single Idea

**Hatekhori is not a font tool that added Bengali/Hindi support later. It is a Bengali/Hindi handwriting-preservation atelier that happens to have proven its engineering in English first — and doesn't say so publicly until the moat is real.**

Everything below follows from this one sentence.

---

## 2. Why This Idea, and Not the Alternatives

Multiple credible-sounding strategies were argued for this project. Three real disagreements had to be resolved:

**Bengali Day 1 vs. English-first validation.**
One line of reasoning: launching English-first makes Hatekhori "an Indian Calligraphr clone with a Bengali name," and Bengali/Hindi should launch immediately to avoid that trap. Another line of reasoning: a Bengali font's required glyph set (base forms + conjuncts + matras + half-forms) can run past 1,000 glyphs — twenty times the complexity of an English A–Z/a–z/0–9 set — making it a bad first thing to build, unvalidated, as a solo/small build.
**Resolution:** don't choose one — sequence them differently. Build the pipeline in English (cheap to iterate, fast to validate), but never show it publicly as the product. The public brand debut is Bengali/Hindi, once the pipeline is proven.

**Two capture modes vs. one.**
The original PRD split "Quick Mode" (low effort, any paper) from "Precision Mode" (structured template, higher fidelity). Resolution: one flow. A craft/atelier brand cannot knowingly ship a path that produces worse output — one bad font shared publicly does lasting reputational damage no amount of Precision Mode polish undoes. Speed and quality are both properties of one well-designed guideline sheet.

**Who the first real user is.**
Candidates ranged from "Western portfolio developer chasing an aesthetic accent" (easy to reach, but already served free — see §3) to "Bengali/Telugu diaspora preserving family heirlooms" (the real emotional core, but too high-stakes to be anyone's first experience of an unproven product).
**Resolution:** the first real user sits in the overlap — an Indian developer or designer who wants **their own script**, rendered as **their own font**, technical enough to tolerate roughness, invested enough in the mission to talk about it.

---

## 3. Competitive Landscape (this decides more than any brand exercise)

Four distinct tiers exist, and confusing them leads to fighting the wrong battle:

**Tier 1 — Legacy paid utilities.** Calligraphr, YourFonts, MyScriptFont/Fontifier lineage. Print-template, scan, upload, TTF/OTF out. Beatable on pricing model (subscription-for-your-own-handwriting is a documented complaint) but not an interesting fight — they're already losing ground to Tier 3.

**Tier 2 — Pro creative-tool integrations.** Fontself (Illustrator/Photoshop extension, real Kickstarter traction — 760 backers, €37,625 in 2015, now used by agencies for color-font work), iFontMaker (iPad, draw-first). Different customer entirely — professional designers already inside Adobe/iPad workflows. Not really competing for Hatekhori's person.

**Tier 3 — The actual threat: free ecosystem killers.** FontCrafter is the one that matters. It's not just a free font generator — it's a full ecosystem: the core tool (500+ glyphs, ligatures, contextual alternates, color-font effects, OTF/TTF/WOFF2/Base64 export, 100% local/private processing, no account) plus a family of companion apps (QuoteCrafter, LetterCrafter, CertificateCrafter, CardCrafter, GreetingCrafter, WeddingCrafter, LabelCrafter, EnvelopeCrafter) and a phone app, PenSend, for typing in your handwriting font and sharing it anywhere. It's already positioned explicitly against Calligraphr's subscription model.

**Verdict on Tier 3: for English, this fight is already over.** Free, private, feature-complete, and first to occupy the "anti-subscription, anti-Calligraphr" story. Nothing Hatekhori could build in English would be the original in that space — only a slower, paid, second copy of it.

**Tier 4 — Craft/foundry brand donors (not competitors).** Pangram Pangram, Atipo Foundry, ABC Dinamo, paper.design, Figma. Different job entirely (they sell finished typefaces or design surfaces, not a handwriting-to-font pipeline) — but real sources for brand mechanics worth borrowing, listed in §7.

This is the second, independent reason (beyond glyph-count complexity) that Indic-first is correct: it isn't just the more interesting identity, after this research it's the *only* uncontested one. Calligraphr, YourFonts, Fontself, and FontCrafter's entire ecosystem all stop at Latin scripts. None of them handle Bengali/Hindi conjuncts. That gap is real and it is Hatekhori's alone.

---

## 4. Positioning

**For** Indian developers and designers who are proud of their own script and tired of every tool treating it as an afterthought,
**Hatekhori is** a personal type atelier that turns real handwriting into an ownable, installable font — Indic scripts first, not as a phase-3 add-on,
**Unlike** Calligraphr, YourFonts, or free ecosystems like FontCrafter, all of which are Latin-script-only and treat Bengali/Hindi conjuncts as unsupported territory, not a gap worth closing.

**What Hatekhori sells:** ownership and script correctness, not speed, novelty, or feature count. The pitch is never "turn your handwriting into a font in seconds, free" — that's FontCrafter's ground, and it's already won.

---

## 5. Brand Pillars

**1. Craft is non-negotiable, even if it means saying no.**
No output ships that wouldn't survive being looked at by someone who actually reads the script. Reject poor-quality photos with a clear, kind message rather than shipping a bad result.

**2. Ownership, not rental.**
One-time payment, forever access, no subscription.

**3. Indic-first is identity, not a roadmap checkbox.**
Bengali/Hindi are not "coming in phase 3." They are the reason Hatekhori exists, and the one thing no competitor — legacy, pro, or free-ecosystem — currently does.

**4. Time is respected by having one good path, not two mediocre ones, and by not chasing a feature war we can't win.**
No forced ceremony, no account walls, and — new, post-competitor-research — no attempt to out-build FontCrafter's English app family. Engineering effort goes entirely toward the Indic pipeline, not toward matching a free competitor feature-for-feature in the one language everyone else already does well.

---

## 6. Voice & Tone

- Warm, quiet confidence — closer to a craftsperson describing their work than a SaaS product launch.
- Never say "AI-powered." The entire point is that a person made this, not an algorithm.
- Error and edge-case copy should feel considered, not like a system alert.
- Avoid borrowing a founder story that isn't actually the founder's own — any personal narrative in marketing should be written by the person it's about, not invented on their behalf. (An earlier draft of this strategy fabricated a personal origin story; flagged here so it isn't reused as if true.)

---

## 7. Visual Direction & What to Steal (applied to the Indic product only)

- Figma-level precision, paper.design-level restraint — minimal, editorial, generous whitespace.
- Paper/ink texture where it's honest, not decorative AI-gradient default.
- No generic "three equal cards" SaaS layout, no purple gradients, no dashboard-grid-of-fonts feel.
- The Human/Machine toggle is the most ownable visual idea in the product — worth designing as a genuine centerpiece.

**From the craft-foundry tier, applied to Bengali/Hindi, not English:**
- Pangram Pangram's "gallery, not catalog" restraint and named-edition framing (e.g. "Hatekhori — Bengali Edition 01") — never applied to an English offering, where it would just look like a slower FontCrafter.
- Atipo Foundry's pay-what-you-want goodwill and founder-story-forward posture — once there's a real, honestly-written story to tell.
- Figma's plugin-as-distribution lesson — worth pursuing later, but for the Indic output, not as a way to compete with FontCrafter's English app family.

**What NOT to do, now confirmed by competitor research:**
- Don't compete on "free" — FontCrafter already won that.
- Don't build an English companion-app ecosystem (a PenSend/QuoteCrafter equivalent) — that fight is lost before it starts.
- Don't lead marketing with "not AI handwriting" as if that alone is the differentiator — FontCrafter and Calligraphr both already imply/claim human-made handwriting; the differentiator that actually holds is script correctness for Bengali/Hindi, not the human-vs-AI framing alone.

---

## 8. Primary Persona

**The vernacular-proud builder** — an Indian developer or designer, comfortable with rough early software, who wants their own handwriting, in their own script, as something they actually use. Motivated by identity and correctness more than convenience. Tolerant of an imperfect first version *because* they believe in why it exists.

**Deliberately not the primary persona (yet):**
- The Western/English-first portfolio developer chasing a personal-brand accent — already served, for free, better, by FontCrafter's ecosystem. Building for them first buys no moat and picks a fight Hatekhori loses.
- The full emotional heirloom/diaspora preservation use case — real and powerful, but too significant a moment to attach to an unproven first version.

---

## 9. Open Strategic Questions (not yet decided)

- Exact pricing tiers — deferred until pipeline quality (and therefore real value) is known.
- Whether a Figma plugin / npm package / CDN snippet is a v1 commitment or a later system layer — and if so, built for the Indic output specifically, not as an English-competing feature.
- Whether Telugu joins the initial Indic scope or is a clearly later addition.
- What the actual founder story is — to be written honestly, by the person living it, not assumed.
