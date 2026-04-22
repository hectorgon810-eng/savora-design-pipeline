# TASTE INTELLIGENCE
Feedback file that teaches the pipeline Hector's taste, batch by batch.
Owner: Hector Flores — DreamArt Studio / Savora
Started: 2026-04-21 · Intel file: `docs/INTELLIGENCE_FILE.md`

---

## How this file grows

Every design batch (parallel Nano Banana or HTML variations) produces one entry. Entry logs:

1. **Post ID + format + track**
2. **Winner** — which variation + concrete attributes
3. **Rejected variations** — each with reason tags + freeform note
4. **Rule learned** — the portable pattern that biases future batches

The rule-learned section is the gold. Entries below it are receipts.

---

## Rejection reason tag dictionary

| Tag | Meaning |
|---|---|
| `composition-off` | Centering, balance, focal point wrong |
| `color-off-brand` | Palette violates brand rules |
| `type-wrong` | Font choice, size, placement, tracking, leading wrong |
| `generic` | Canva-made / template-marketplace feel |
| `no-craft` | Lacks intention, rushed |
| `wrong-register` | Register mismatch (e.g., Azteca looking editorial instead of playful-maximalist) |
| `text-over-photo-poor` | Legibility / hierarchy over photo failed |
| `logo-placement-off` | Logo placement or scale wrong |
| `too-busy` | Too many elements competing |
| `too-empty` | Too sparse, unfinished |
| `food-regenerated` | Nano Banana altered the supplied food photograph (critical fail) |
| `voice-off` | Copy doesn't match brand voice |
| `ai-tell` | Stock gradient / cyan-magenta / default drop shadow / 33/33/33 colour / dead-center symmetry |
| `aspect-wrong` | Output not at requested aspect ratio |
| `density-wrong` | Canvas fill doesn't match register's target band |

Always combine with a one-sentence freeform note.

---

## Autonomous-readiness threshold

Pipeline stays in feedback loop until each brand hits **≥20 logged decisions** AND rule-learned sections show clear patterns. Target: 60 decisions total.

| Brand | Logged decisions | % to threshold |
|---|---|---|
| Jackson House | 1 | 5% |
| Blue Mezcal | 3 | 15% |
| El Azteca | 1 | 5% |

---

# SEED RULES (before any human feedback)

Pre-seeded from the intelligence file research. These bias the first generations before any real decision logs exist. Overridden by any conflicting rule learned from an actual Hector decision below.

## Universal (applies to all brands)

- Register first. Format second. Copy third. Name the register out loud before designing.
- Compose for negative space first; use a colour-block field second; soft radial scrim third; knockout type fourth. Never default drop shadow over busy food.
- Focal point at rule-of-thirds intersection (upper-left or lower-right), not dead center.
- Contrast ratio between display and body type ≥ 3:1, ideally 4:1 or 5:1.
- Every flat colour field gets 3–8% noise/grain overlay.
- 60/30/10 colour rule — one dominant, one support, one accent. Never 33/33/33.
- Quote exact text in straight double quotes in NB prompts — every unquoted word is a word the model may misspell.
- Describe type stylistically, not by font name.
- Set aspect ratio via API parameter, not prose.
- For any text over photo: say "integrated as if printed on the linen / menu" — not "overlaid."
- No default Poppins / Montserrat / Open Sans / Roboto.

## Jackson House — seed rules (warm-vernacular → heritage-editorial)

- Canvas density 55–75% — confident but not empty.
- 60% cream ground, 30% forest OR oxblood (pick one dominant), 10% mustard.
- Type: old-style or slab serif display (Farnham / Sentinel / Caslon) + condensed all-caps grotesque (Knockout / Trade Gothic) for labels.
- Texture: cream laid paper + letterpress emboss + Portra 800 grain on photography.
- Photography style: warm tungsten 2800K candlelight, human hands in frame, shallow DOF.
- Never bilingual (English only).
- Award/launch moments — ceremonial symmetry + gold foil OK. Product posts — asymmetric, hairline rules.
- CTA voice: "reservations at link" (small-caps italic). Never a rounded button.

## Blue Mezcal — seed rules (editorial-modernist → moody-nocturnal)

- Canvas density 40–65% — editorial restraint, deliberate breathing room.
- Editorial palette (daytime): 60% bone cream, 30% cobalt, 10% marigold.
- Nocturnal palette (after-hours): 60% charred black, 30% brass/burgundy, 10% warm white.
- Type: refined editorial serif (Canela / GT Sectra / Bodoni) + quiet modern grotesque (Söhne / Neue Haas) for small-caps labels.
- Texture: fine 5% noise overlay, subtle paper grain, tonal 5% gradient — never flat.
- Photography style: moody low-light tungsten 2800–3000K, single rim-light at 45°, 85mm f/2.8, Portra 800 grain.
- Bilingual posture: accent only — one Spanish phrase/word per post as italic pull-quote. Exception: cultural holidays (Spanish primary).
- Cocktails always need rim-light, never overhead on white.
- "Type IS the image" is the editorial move for quote/dicho posts — no decorative photo behind.

## El Azteca — seed rules (playful-maximalist → warm-vernacular)

- Canvas density 75–95% — maximalist fill, layered ornament.
- Playful palette (default): hot pink #FF5BA7 + sunshine yellow #FFD400 as two heroes at 40/40, turquoise at 15, chile red at 5, cream ground.
- Heritage palette (secondary): 60 masa cream, 30 cobalt OR oxblood dominant, 10 marigold.
- Type: bold chunky display sans (Cooper Black / Sharp Grotesk Ultra / Obviously) + friendly rounded sans body + hand-painted brush lettering accent.
- Texture: halftone dots at 45° + risograph misregistration + stickered elements rotated ±1–3° off axis + hand-drawn marker arrows.
- Photography style: overhead flat-lay OR three-quarter daylight 5500K, slightly oversaturated, Portra 400 grain.
- Bilingual posture: heavy — Spanish primary (display), English secondary (small-caps beneath at 40–60% size).
- Ingredient-callout with hand-drawn arrows is the Azteca signature — reference La Bamba Ice Cream.
- Taco Tuesday / Margarita Monday = B1 recurring anchor with large Spanish day-wordmark.

---

# RULES LEARNED

Portable patterns extracted from real Hector decisions below. New rules go on top, dated. Review before every batch.

## Jackson House — rules learned

- **[2026-04-21 · JH-A1-001-r2 · Lobster Roll]** **V4 winner** — vertical color-block strip on the LEFT 30% of canvas with photo filling the right 70% at full scale. Needs two fixes: (a) slight metallic gradient on the headline type (brass foil), (b) deeper tonal gradient on the green field (darker toward the bottom, almost black in the corners).
- **[2026-04-21 · JH feed analysis] 🚨 REGISTER CORRECTION — overrides prior Jackson House direction:**
  > The primary Jackson House direction is **premium-heritage foil-stamped elegance** (black ground + brass-gold foil gradient type + deep tonal forest/oxblood fields), NOT the rustic-cream-paper / letterpress-on-ivory direction previously written. Reference: the National Cocktail Day Jackson House flyer on their feed (gold on black cocktail menu). Hector's exact words: *"need more 'premium' energy for jackson house and blue mezcal, re run, but now look at our feed. notice the colors that are dominant, lets stay around these with slight metallic gradients, not rustic. needs to feel high end, but its really higher end comfort food, so theres a balance."*
- **[2026-04-21] Dominant feed palette (JH):** warm reds + gold/brass + forest green + deep black/charcoal + warm amber food tones. Every future JH post should draw from this palette.
- **[2026-04-21] Metallic gradient rule (JH + BM):** every headline gets a 3-stop metallic gradient (brass foil for JH, brass-foil for BM nocturnal too). Never flat gold fills — always a foil-stamp reading with a specular hotspot and a deeper-shade inner edge.
- **[2026-04-21] Comfort-food balance rule (JH only):** photograph the comfort food as-is (generous portion, real plate, no pretension) but ELEVATE THE FRAME — foil type, deep tonal gradients, editorial crop. The balance is: approachable dish, elevated typography & colour system.
- **[2026-04-21 · JH-A1-001-r3 · Lobster Roll] V1 winner — CLEAR WIN.** Layout: photo full-bleed, headline in a color-block field lower-left, gold-foil type on deep forest/green field. Works because gold on green carries contrast on its own.
- **[2026-04-21] Drop-shadow rule:** **no drop shadow on type when palette contrast is already sufficient** (e.g., gold foil on deep forest). Gemini adds drop shadows by default — explicitly reject in the prompt for sufficient-contrast combos. Drop shadows stay only when type sits over photo without a color field.
- **[2026-04-21] Logo integration rule:** the REAL brand logo must be used, not a Gemini-generated wordmark. Runner needs `--logo` flag accepting a PNG/SVG, attached as a second reference to the API call with instruction "place this logo exactly at bottom-center (or specified position), do NOT redraw, restyle, or re-letter it — use it as-is." Logos live at `BRAND_PROFILES/logos/{brand}.png`.
- **[2026-04-21 · JH-A1-001-r4 · Lobster Roll] V1 winner.** Logo attached + award-badge + no-shadow ruleset works. V1 approach (color-block field lower-left, photo right 70%, brass-foil type, deep forest/oxblood gradient) = JH default going forward.

## Blue Mezcal — rules learned

- **[2026-04-21 · BM-A1-002]** Nocturnal cocktail spotlights — **editorial magazine-spread layout: headline + sub in upper-third, photo anchored to lower-half, canvas fill at the low end of BM's 40–65% band (≈40–50% fill = 50–60% negative space)** beats asymmetric color-block, type-as-image, flipped-canvas, and diagonal-split alternatives. *Bias future BM cocktail batches toward Variation 2 angle as baseline; rotate others only when a specific post-type demands it.*
- **[2026-04-21 · BM-A1-002]** **Color-block fields for headline must pull from the same nocturnal palette as the rest of the design** (brass / warm white / burgundy on charred black). Gemini drifted to cream/editorial palette in V1 even though stem = nocturnal. Lock palette-match in next batch by stating explicitly: "The color-block field MUST use [palette hex list] — do not introduce colors outside this list."
- **[2026-04-21 · BM-A1-002] 🚨 UNIVERSAL HERO RULE — applies to all brands, all formats with a food/drink photo:**
  > **Never shrink, inset, or miniaturize the supplied Cloudinary photo.** The photo is the canvas foundation — it fills the primary region at full scale. Typography, colour fields, and ornament lay OVER the photo (integrated, not decorated by it). Variations that reduce the photo to a small swatch, tile, or inset are rejected on sight.
  > *Hector's exact words: "i dont want smaller images of what we have, use the real images as the template, and design over them."*
- **[2026-04-21 · BM-A1-002] Photo-led palette complement rule:**
  > When selecting color-block / accent fields, the brand palette choice must COMPLEMENT the photo's dominant colour, not clash with it. HOMBRE photo dominant = warm amber/orange (bourbon + ice cube backlight). Correct brand-palette complement = cobalt / deep navy (on the editorial spectrum) or brass + charred black (nocturnal). Gemini did not reliably deliver brand cobalt in V5. Next BM cocktail batch: state dominant photo hue explicitly + demand the complementary brand hex in the prompt.
- **[2026-04-21 · BM-A1-003 · Cucumber Margarita] 🚨 REGISTER CORRECTION — burgundy-dominant nocturnal reads off-brand for Blue Mezcal.** Hector's exact words: *"not sure how i feel about the burgundy colors? how does this fit blue mezcal? ... for blue mezcal i would expect something more blue and white so we can start building the branding on their actual page."* → Burgundy is canonical in brand profile as 30% accent, BUT the NAME "Blue Mezcal" forces blue+white to stay dominant as brand-identity anchor. Demoted burgundy to <15% rare accent. Added new `blue_mezcal_playful` stem — blue + white + marigold, editorial spine with more energy (Casa Azul daylight × Intelligentsia × Dandelion Chocolate). Nocturnal/burgundy stem reserved for late-night cocktail content specifically.
- **[2026-04-21 · BM-A1-003] Copy personality rule — applies to ALL brands going forward:** Hero headline is NOT always the subject name. Three options per variation pool — (a) subject name, (b) feeling/mood line ("Cool and dangerous."), (c) smart-mouthed punchline ("Impossible to have just one.", "You already know."). Mix across a set. Reason: formulaic "name + short desc" across every post kills personality. Baked into `build_scene_paragraph` as HEADLINE OPTIONS + into BM playful stem as COPY PERSONALITY RULE.
- **[2026-04-21 · BM-A1-003] Footer format rule — applies to ALL brands:** Address/CTA always renders as a single low-key hairline-ruled footer line at the bottom margin (V1 format). Model was PRINTING THE WORD "CTA" on the image (placeholder leak). Prompt now explicitly reminds model: "NEVER print the word 'CTA' or 'ADDRESS' literally on the image — those are labels for you, not content."
- **[2026-04-21 · BM-A1-003] Agave-leaf ornament = approved BM signature mark.** V4 rendered a small hand-drawn agave plant — Hector approved. Added to `blue_mezcal_playful` stem as the recurring one-per-layout signature ornament (when a hand-drawn mark is used at all). Not every post, but an approved reusable option.
- **[2026-04-21 · BM-A1-003-r4] Major unlock — 4 new angles land at once:** V4 (vertical sidebar), V6 (recipe-ingredient sidebar), V7 (dramatic-crop, idea good), V8 (mirrored V1) all read solid on first run. Pattern: angles that carry ADDITIONAL INFORMATION (ingredient list, issue/folio, method) OR a DRAMATIC CROP feel more like real design than pure color-block-over-photo. Keep pushing this direction for future brands.
- **[2026-04-21 · BM-A1-003-r4] V5 type-first poster FAILED — hero-photo-rule collision.** Type-first at 70% leaves too little room for the photo. Fix: rewrote V5 as TYPE-DRIVEN EDITORIAL with photo floor at ≥50% of canvas. Rule: no variation angle may shrink the photo below 50% of canvas in any direction.
- **[2026-04-21 · BM-A1-003-r4] V1 word-spill + V3 composition-off:** Text-fit-container rule landed unevenly. Gemini respects it when the container is generous (V4, V6) but still clips when the container is aggressive (V1 corner block). Patch idea for future iteration: add explicit minimum-container-size (40% × 30% of canvas minimum for a corner headline block).
- **[2026-04-21 · BM-A1-003-r4] Dramatic crop direction approved in principle.** V7 concept (extreme close-up + big negative-space type) landed conceptually but the crop choice was off. Next time: let the model pick from 3 pre-defined crop targets (garnish close-up, condensation + rim, glass-edge silhouette) rather than leaving crop open.
- **[2026-04-22 · BM-A1-004 — big step forward] Verdict: V1 great, V2 nice, V3 ok/good colors, V4 strong drink-focused comp, V5 STILL failing (dead space), V6 ok, V7 good BUT placeholder leak, V8 cut-out hero loved. "Definitely on brand for Blue Mezcal."** Batch is the first BM run Hector called on-brand top-to-bottom.
- **[2026-04-22 · BM-A1-004] Agave ornament — SOFTENED to optional + expanded library.** Hector: "don't feel like you have to add the agave plant on every single one. if anything, i would like those vector designs around the flyers but in context of each restaurant. more than agave can be drawn as a nice addition." Rule now: zero or one hand-drawn vector per layout (default ZERO). Pull from per-restaurant world-library — for BM: agave, citrus wedge, salt-rim arc, smoke curl, ice cube, stirrer, mezcal worm. For AZ: warrior, chile, corn, tortilla-press, arrow, skull/Day-of-Dead mark. For JH: wheat sheaf, rolling pin, flame, butter pat, coffee-bean, fork/knife cross. EACH brand stem needs its own ornament library block.
- **[2026-04-22 · BM-A1-004] Placeholder leak round 2 — "SUPPORT LINE" printed literally on V7.** Same class of error as "CTA"/"ADDRESS". Fix: renamed internal labels to reduce leak surface (SUPPORT LINE → BODY COPY; FOOTER LINE → BOTTOM-MARGIN LINE) AND added explicit NO-LITERAL-LABEL RULE listing ALL meta-label words that must never appear on canvas. Pattern: any ALL-CAPS section header I use in prompts is a leak risk.
- **[2026-04-22 · BM-A1-004] Cut-out hero (V8 Frenchette) = approved BM move.** "love the drink being cut out." The isolated drink-on-cream-ground with script+serif lockup landed. Promote this to a reusable composition pattern across brands when a clean silhouette is possible.
- **[2026-04-22 · BM-A1-004] V5 Sweetgreen-award — still losing photo space.** Second batch failing same way. Retire or rebuild: next version must PHYSICALLY RESERVE ≥55% canvas for photo before type is composed (not ≥50% as floor — ≥55% as hard min), with the award lockup constrained to a top-third or bottom-third strip only.

## Jackson House — rules learned

- **[2026-04-22 · JH-A1-002 · Chimichurri Steak] V2 CLEAR WINNER — Ghia clean-ground elegance.** Quote: "clear winner. great cut of the plate into 2 colors, perfect use of the image with good typography." Pattern to promote: clean ivory/cream two-field split + brass-foil serif caps on one side + hero photo on the other. Elevate this layout to JH PRIMARY move (not just one of 8 variations).
- **[2026-04-22 · JH-A1-002] NO DROP SHADOWS on brass-foil type.** Hector on V5: "not a fan of that drop shadow on the gold, light on dark already has a good separation." Brass-foil gradient + specular highlight already carries dimension — adding a drop shadow turns elevated into cheap. Patch: explicit no-drop-shadow rule on JH foil headlines.
- **[2026-04-22 · JH-A1-002] Ornament over-use still leaking (V4 pan).** Even after making ornaments "optional, default zero," model still adds them when layout doesn't need one. Reinforce: if photo + type fill ≥70% of compositional weight, ornament budget = 0. Ornament is a RESCUE tool for sparse compositions, not decoration.
- **[2026-04-22 · JH-A1-002] V6 recipe-sidebar STILL has text overflow on JH.** 3rd time V6 fails text-fit on JH (wider dish names + foil weight = more space needed). Patch: JH-specific V6 container minimum = 42% × 40% of canvas (vs. 40% × 30% for BM/AZ). Brass-foil caps are wider than sans.
- **[2026-04-22 · JH-A1-002] V7 logo rendered as FAKE TEXT, not the attached PNG.** Model treating logo reference as style guide instead of asset. Patch: explicit "use the attached logo reference PNG verbatim — do not recreate, do not retype, do not restyle" instruction.
- **[2026-04-22 · JH-A1-002] V8 copy line — (c) option firing weak.** Hector: "would've used a different main phrase." Voice-seed is seeded correctly, but model picking surface-level instead of earned lines. Patch idea: when (c) fires, require model to state the specific dish-attribute→voice-line derivation in prompt log (not on image).
- **[2026-04-22 · JH-COMPARE-02 · NB Flash vs gpt-image-2] gpt-image-2 SUBSTANTIALLY BETTER on same prompts.** Hector verdict: "substantially better in my opinion. although where we have gone with gemini is not bad." OpenAI wins on typographic polish, color handling, composition sophistication. Gemini stays viable — cheaper, faster, respectable output. Keep both backends wired; default to gpt-image-2 for hero content, Gemini for bulk.
- **[2026-04-22 · JH-COMPARE-02] V8 (Frenchette script + serif lockup) = CLEAR WINNER when executed by gpt-image-2.** "Composition / showcasing this specific dish for its length and graphic design visual appearance." Promote V8 Frenchette to signature-layer move for Savora generally — reusable across all three brands with palette swap.
- **[2026-04-22 · REAL-IMAGE IDENTITY LOCK — UNIVERSAL BRAND RULE, HIGHEST PRIORITY] Savora does NOT serve AI-regenerated food photography.** Both backends have a tendency to "reinterpret" the reference photo as inspiration rather than lock it verbatim. Hector: "as Savora we take pride in our images, don't want to start serving fake images. make sure there's real image identity lock." Patch landed in build_scene_paragraph(): explicit REAL-IMAGE IDENTITY LOCK block — reference photo is locked composite layer, pixel-accurate, untouched; design composes around it. Applies to ALL brands, ALL variations, ALL backends. Hector is building a separate AI-duplicate-plate system as a parallel track — that work stays OUT of this pipeline.

## El Azteca — rules learned

- **[2026-04-21 · AZ-A1-001 · Cóctel de Camarón] V1 winner WITH corrections applied.** V1 composition (color-block lower-left, photo right, logo bottom, hand-drawn arrows) is the AZ default — conditional on the texture + arrow + palette fixes below.
- **[2026-04-21] AZ arrow-semantic rule:** every hand-drawn marker arrow must POINT AT the specific named ingredient in the photo (shrimp, sauce, avocado). Arrows at random sauce pools, rim, empty space, or decorative swoops are rejected. 3–5 arrows max. 2–3px hand-wobble marker weight.
- **[2026-04-21] AZ type-texture rule:** letters stay CLEAN — no grain, no dissolve, no knockout, no distress overlay on letterforms. Texture lives in the background field only. Headlines crisp, body readable. Bottom copy ≥18–20pt equivalent — never micro-decorative-print.
- **[2026-04-21] AZ palette-pairing rule:**
  - WORKS for warm-red food (shrimp, birria, mole): pink+red+cream, blue+red complementary, pink+cream
  - AVOID: black+yellow (harsh school-bus), blue+black (flat), mono-saturated flat (cheap)
  - Lean PASTEL-saturated, not flat-saturated — feel hand-mixed / poster-printed, not digital Canva
- **[2026-04-21] AZ photo-to-field transition:** 60–120px soft gradient dissolve between color field and photo edge — not a hard knife-edge. No horizontal bands or diagonal slashes cutting through the food.
- **[2026-04-21] AZ drop-shadow rule:** no drop shadows on AZ layouts — register is flat-layered playful-maximalist graphic. Dimension comes from layered fields + halftone + arrows.
- **[2026-04-21] AZ texture-amount rule:** less is more. Family-restaurant warmth, not zine-overload. Halftone + riso OK on fields. V1's texture level was too heavy.
- **[2026-04-21] AZ logo rule:** warrior logo @ 80–120px full-color in a corner works — reinforces family-restaurant register.

---

# DECISION LOG

Newest entries on top. One entry per batch.

---

## Template for each entry

```markdown
## [POST_ID] — [Brand] — [YYYY-MM-DD]

- **Template / format:** [hero_dish_editorial | cocktail_spotlight_moody | ingredient_anatomy | ...]
- **Track:** [Nano Banana | Claude Design HTML]
- **Aspect / Stem:** [4:5 / blue_mezcal_editorial]
- **Source image (if any):** [Cloudinary key]
- **Subject + support:** [exact headline] / [support line]

**Winner:** Variation [N]
**Winner attributes:**
- Composition: [what worked — rule-of-thirds position, negative space %, etc.]
- Palette: [hex dominance + why]
- Typography: [stylistic description + hierarchy]
- Texture / treatment:
- Copy / voice:

**Rejected variations:**
- Variation [N] — tags: [`generic`, `type-wrong`] — note: [one sentence]
- ...

**Rule learned:**
> [One-sentence portable pattern. Scoped to brand or universal. Bias future generation toward this.]
```

---

# REFERENCE EXEMPLARS (not batches — seed visuals)

Inline references for what "elevated" looks like per brand. These live at `REFERENCES/_inbox/` pending sort into `labamba/` · `casa_azul/`.

## Azteca reference — La Bamba Ice Cream ecosystem
- **Churro Cup ingredient-callout** — white outline wordmark watermark behind · saturated yellow + hot pink + turquoise background with triangular geometric shapes · hand-drawn marker arrows + handwritten ingredient labels · photo integrates into left-side callout grid · La Bamba wordmark corner-sticker.
- **"¡La combinación perfecta!"** — pink script headline, oversized, upper-third · yellow ground · two products side-by-side (sandwich + drink) · ground-plane shadow · La Bamba wordmark centered under photos. Bilingual-Spanish-primary.
- **"PALETAS DE TU SABOR FAVORITO"** — outline-serif display at 60% of canvas · deep olive-yellow ground · paletas photo overlaps the type · cinematic color grade. Type-as-image move.

**What these teach the system:**
- Two heroes at 40/40 (pink + yellow) with cream as canvas.
- Hand-drawn arrows are a non-negotiable Azteca signature.
- Watermark-outline wordmark behind the subject = premium maximalist move, not busy.
- Bilingual Spanish-primary even for simple product shots.

## Blue Mezcal reference — Casa Azul NYC ecosystem
- **"Charred Grilled Octopus"** — heavy sans block headline in cream (offset orange block) upper-left · Casa Azul wordmark top-right · food photo bottom 60% on cobalt ground. Editorial restraint.
- **"I LIVE FOR thirsty thursdays"** — all-caps white display stacked with a script word · orange ground · wedge crop of taco tray at top · cocktail centered bottom · Casa Azul wordmark bottom-right inside black diagonal wedge.
- **"TACO TUESDAY" (Oaxacan register)** — chunky display black on terracotta ground · illustrated wolf head · torn-paper motif · TUESDAY, AUGUST 3 · 6–9 PM info line. Heritage-modernist feel.

**What these teach the system:**
- Editorial cobalt for Blue Mezcal hero dish = signature move. Don't flatten to all-navy.
- Block-headline tucked into a corner (not full-width) is the Casa Azul A1 pattern.
- Color-block field behind type is preferred over drop shadow.
- Wordmark top-right corner, not bottom-center, for editorial restraint posts.
- Script-type as accent word only — "thirsty **thursdays**", not full caption.

---

*(decision entries begin below)*

---

## BM-A1-002 — Blue Mezcal — 2026-04-21

- **Template / format:** `cocktail_spotlight_moody`
- **Track:** Nano Banana (NB2 `gemini-3.1-flash-image-preview`, 1 variation fell back to 2.5)
- **Aspect / Stem:** 4:5 · `blue_mezcal_nocturnal`
- **Source image:** `B-35` (HOMBRE Old Fashioned branded ice cube)
- **Subject + support:** "HOMBRE Old Fashioned" / "Branded ice cube. Bourbon underneath."
- **Batch timing:** 5 variations generated in 28.2s parallel (5 concurrent threads)

**Winner:** Variation 2
**Winner angle logged:** Wider framing · low end of BM's 40–65% fill band (≈40–50% fill / 50–60% negative space) · headline + sub in upper-third · photo anchored to lower-half · editorial magazine spread feel.
**Winner attributes:**
- Composition: editorial spread rhythm — upper-third is quiet type zone, lower-half carries the photo
- Palette: nocturnal (charred black + brass + warm white — confirmed working)
- Typography: refined editorial serif italic + small-caps label beneath
- Texture / treatment: 5% noise overlay (implicit from stem)

**Rejected variations:**
- Variation 1 — tags: `color-off-brand` — composition fine; color-block field's palette didn't match the rest of the design (mixed palette, violated 60/30/10 + single dominant rule)
- Variation 3 — tags: `wrong-register`, `type-wrong`, `composition-off` — type-as-image too aggressive for cocktail spotlight; better for quote posts
- Variation 4 — tags: `photo-shrunk` — **CRITICAL NEW RULE from Hector: "don't want smaller images of what we have; use the real images as the template, and design OVER them."** Gen reduced photo to a miniature decoration. Photo must stay FULL-SIZE as the foundation; type + ornament lay OVER.
- Variation 5 — tags: `color-off-brand`, `too-busy` — Hector: "blue would've been perfect to contrast the orange in this case, but just doesn't work." HOMBRE photo has warm amber/orange dominance (bourbon + ice); brand cobalt/deep navy was the correct complement; gen didn't deliver true brand blue. Also stickered collage reads Azteca, not BM.

**Rule learned:**
> BM nocturnal cocktails default to **editorial magazine-spread layout: upper-third quiet type zone, lower-half photo**. Reject type-as-image (better for dichos), cream flips (that's JH territory), and collage/diagonal-split (that's Azteca territory). **Color-block fields for headlines must lock to the nocturnal palette — do not let cream / editorial-bone leak in.**

**Meta-feedback on logging protocol:**
> I inferred V1's tag as `composition-off`. Hector corrected — composition was fine, colors were off. **Keep inferring tags** (per Hector's autonomous-execution preference) **but flag them as inferred + offer one-line override**. Don't treat inferred tags as confirmed unless user validates them.

---
