#!/usr/bin/env python3
"""
Nano Banana runner — Gemini image-gen variation producer.

Calibrated to the brand-stem framework in docs/INTELLIGENCE_FILE.md (Part III).

Key moves:
  * Parallel generation (ThreadPoolExecutor, default N=5 concurrent)
  * Brand stems pasted verbatim before scene paragraphs (per intel framework)
  * Aspect ratio set via image_config.aspect_ratio (API param, not prose)
  * Composite rule enforced: never regenerate the food photograph
  * Variation angles rotate composition/palette/type approach
  * Configurable model via GEMINI_IMAGE_MODEL env — default 2.5 Flash Image
    (set to gemini-3.1-flash-image-preview for NB2 / gemini-3-pro-image-preview
    for NB Pro when text-heavy)

Usage:
    python3 scripts/nano_banana_runner.py \\
        --brand blue_mezcal \\
        --post-id BM-A1-001 \\
        --format hero_dish_editorial \\
        --image-key B-35 \\
        --subject "HOMBRE Old Fashioned" \\
        --support "Branded ice cube. Bourbon underneath." \\
        --count 5 \\
        --aspect 4:5

Output:
    OUTPUT/nano_banana/blue_mezcal/BM-A1-001/variation_{1..N}.png
    OUTPUT/nano_banana/blue_mezcal/BM-A1-001/prompts.jsonl
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import pathlib
import sys
import time
import urllib.request
from dataclasses import dataclass
from typing import Optional

try:
    from google import genai
    from google.genai import types
except ImportError:
    sys.exit("Install: pip install google-genai python-dotenv Pillow")

try:
    from dotenv import load_dotenv
except ImportError:
    sys.exit("Install: pip install python-dotenv")


ROOT = pathlib.Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
if not API_KEY:
    sys.exit(f"GEMINI_API_KEY not in {ROOT / '.env'}")

# Default to Nano Banana 2 (Apr 2026 default per intel). Fall back to 2.5 if
# the preview model isn't available on this account — runner catches the
# error and retries with GEMINI_IMAGE_MODEL_FALLBACK.
IMAGE_MODEL = os.environ.get(
    "GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview"
)
IMAGE_MODEL_FALLBACK = os.environ.get(
    "GEMINI_IMAGE_MODEL_FALLBACK", "gemini-3.1-flash-image-preview"
)

CLOUDINARY_URLS_PATH = ROOT / "cloudinary_urls.json"
LOGOS_DIR = ROOT / "BRAND_PROFILES" / "logos"

# OpenAI key — pulled from centralized key file (or env var fallback)
def _load_openai_key() -> str:
    env_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if env_key:
        return env_key
    cll_path = pathlib.Path("/Users/dreamartstudio/Desktop/CLL_PIPELINE")
    if cll_path.exists() and str(cll_path) not in sys.path:
        sys.path.insert(0, str(cll_path))
    try:
        import api_keys  # noqa: WPS433
        return getattr(api_keys, "OPENAI_API_KEY", "").strip()
    except ImportError:
        return ""


OPENAI_API_KEY = _load_openai_key()
OPENAI_IMAGE_MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")
# Fallback disabled by default — gpt-image-1 is the old model and defeats the
# purpose of the NB-vs-ChatGPT 2.0 comparison. Set OPENAI_IMAGE_MODEL_FALLBACK
# env var to re-enable.
OPENAI_IMAGE_MODEL_FALLBACK = os.environ.get("OPENAI_IMAGE_MODEL_FALLBACK", "")


# ============================================================
# BRAND STEMS — verbatim from docs/INTELLIGENCE_FILE.md Part III
# ============================================================

BRAND_STEMS = {
    "azteca_playful": """A social media image for El Azteca — a family Mexican restaurant with locations in CAMDEN, DOVER, and REHOBOTH, Delaware. The register is PLAYFUL-MAXIMALIST FAMILY with craft discipline. El Azteca is NOT La Bamba. Never reference, name, caption, or visually include La Bamba, La Bamba Ice Cream, or any La Bamba product anywhere on the image. Only use El Azteca branding.

BRAND PALETTE (PRIMARIES, 75–85% of every layout): chile red #E63946, agave green / forest green #2F7A3A, cobalt blue #1A3FA8, masa cream #F8F2DF. These four are the brand. Pink #FF5BA7 is a FUN ACCENT ONLY — cap pink at 15% of any single layout, never the ground, never dominant. Sunshine yellow #FFD400 and turquoise #1FB5B0 are RARE ACCENTS only (<10% each). Lean PASTEL-SATURATED not flat-saturated — colors feel hand-mixed, paper-stock, poster-printed, not digital Canva.

PALETTE PAIRINGS THAT WORK: red + cream + green (Mexican flag warmth), blue + red + cream (complementary for red-dominant dishes), green + cream + red accents, cream + red + small cobalt corner. PAIRINGS TO AVOID: black + yellow, blue + black, any pink-dominant ground, mono-saturated flat anything.

TYPOGRAPHY DISCIPLINE: the typography should match the weight and spirit of the El Azteca warrior logo wordmark — bold chunky display sans (Cooper Black / Sharp Grotesk Ultra / Obviously) at headline weight the SAME weight family as the logo's lettering. Friendly rounded sans body. Optional hand-painted brush accent word. Letters STAY CLEAN — no grain, no dissolve, no distress on the type. Texture lives in the BACKGROUND, never on letterforms. Headlines crisp. Address / award / bottom copy ≥18–20pt equivalent — never micro-print.

HAND-DRAWN ARROW RULE (critical — semantic-accuracy enforced, default is ZERO arrows):
  Arrows are RARE and only used for SMALL DETAIL callouts the viewer might miss. DEFAULT = zero arrows on almost all posts.
  BANNED arrow targets (never label these — they are obvious and labeling them looks patronizing): meat / steak / chicken / fish fillet / rice / beans / tortilla / bread / cheese / lettuce / sauce pool / egg / pasta / fries. These are already visually obvious; arrows on them look wrong.
  ALLOWED arrow targets (only when specifically separable + visible): a hidden or easy-to-miss GARNISH (specific herb name, specific chile variety, pickled item), a specific CHEESE type the customer wouldn't guess (cotija vs feta), a specific SAUCE / CRUDITÉ the dish builds around (salsa macha, chicharrón, etc). Only add an arrow if the label adds REAL INFORMATION the viewer didn't know. If in doubt, zero arrows.
  Conditions when used: (1) label names an ingredient visible at a specific pixel location, (2) arrow tip terminates exactly on that ingredient, (3) no label is generic / duplicative with what the photo obviously shows. Two arrows max when used. Arrow weight 2–3px marker, slight hand-wobble. Never invent ingredients.

LOGO RULE (NON-NEGOTIABLE — LOGO IDENTITY LOCK):
  The supplied El Azteca warrior logo is a specific, approved wordmark. Use it VERBATIM. Do NOT redraw it, do NOT re-illustrate it, do NOT restyle it, do NOT generate an alternate warrior. Do NOT combine it with other design elements inside the logo itself. If the supplied logo is attached as a reference image, composite it at 80–120px in ONE corner as-is. If no logo is attached, skip the logo entirely — do not invent one. Any output where the model draws its own version of the warrior or inserts a mocked-up "El Azteca" lockup is REJECTED.

PHOTO-TO-FIELD TRANSITION: 60–120px soft gradient dissolve where color field meets photo edge — never a hard knife-edge. No diagonal slashes or horizontal bands that CUT THROUGH the food photo.

TEXTURE: halftone dots at 45° on backgrounds OK. Subtle risograph misregistration OK. Slight off-axis rotation of stickered elements OK. Family-restaurant warmth, not zine-overload.

NO DROP SHADOWS. Flat-layered playful-maximalist graphic. Dimension from layered fields + halftone + arrows.

Photography style: daylight-bright, slightly oversaturated, warm Portra 400 film grain ON THE PHOTO ONLY. Hand-made, family, warm, bilingual Spanish-primary acceptable.

VOICE SEED (El Azteca-only): family-warm, bilingual Spanish-primary OK, celebration energy. Voice examples from the AZ feed: "Guacamole, but make it octopus." · "Not your average appetizer." · "We don't do things halfway." · "Pick your poison." · "Cocktail hour." · "Classic for a reason." Voice is celebratory-familiar, never ironic-detached, never smart-mouth (that's Jackson House). Spanish phrases OK when they fit ("De la casa", "¡Con gusto!", "Auténtico"). NEVER reference La Bamba in voice.

LOCATIONS FOR ADDRESS/FOOTER: "Camden · Dover · Rehoboth" or equivalent. Never use generic "Delaware · Rehoboth" — the three specific city names are the brand's geographic identity.

HAND-DRAWN ACCENT (Azteca — OPTIONAL, sparing): AZ already carries hand-drawn arrows as its signature (see arrow rule above). BEYOND arrows, zero or one additional ornament per layout is allowed from the AZ-world library: chile silhouette, corn cob outline, tortilla-press mark, skull/Day-of-Dead hairline, warrior-shield mini-mark, hand-drawn star-burst, sun-ray hairline, lime-wedge cross-section. NEVER agave (BM). NEVER wheat/butter/flame (JH). Do not stack ornaments AND arrows heavily — if arrows are present, ornament budget is zero unless clearly additive.""",

    "azteca_heritage": """A social media image for Azteca, a family Mexican restaurant, heritage register. Brand palette: cobalt #1A3FA8, marigold #F2A900, chile red #D72638, masa cream #F3ECD8, oxblood #6E1423, turquoise #1FB5B0. Typography: bold display serif (Cooper Black / Obviously feel) paired with handwritten script annotations. Texture: papel picado paper cutouts, halftone overlay, slight off-axis rotation, warm Portra 400 grain. Photography style: overhead flat-lay or three-quarter daylight, 5500K, soft shadow upper-right. Hand-made, bilingual Spanish primary, warm-vernacular heritage-maximalist.""",

    "blue_mezcal_editorial": """A social media image for Blue Mezcal, an upscale agave-forward bar and kitchen. Brand palette: cobalt blue #1E3A8A, bone cream #F3ECD8, marigold #F2A900, agave green #4E6B3A, charred black #1C1A17. Typography: refined editorial serif headlines with tight tracking, paired with quiet modern grotesque small-caps labels. Texture: fine noise overlay at 5%, subtle handmade paper grain, restrained. Photography style: moody low-light with directional rim, tungsten 3000K warmth or editorial 5200K daylight depending on scene. Editorial-modernist restraint, 60–65% negative space.""",

    "blue_mezcal_playful": """A social media image for Blue Mezcal — an upscale agave-forward bar AND kitchen that is SOCIAL, BOLD, FUN, and cocktail-forward. Think of Blue Mezcal as THE BOLD SIBLING OF AZTECA — same cultural heart, more adult, more cocktail, more elevated Mexican food. Reference anchors: Casa Azul NYC (daylight editorial polish + nighttime energy), Handshake Speakeasy Mexico City (social insider bar), Licorería Limantour (rowdy-chic), Cosme (Enrique Olvera's upscale but PACKED and buzzing). NOT quiet. NOT a library. NOT Céline-minimal. Fun, social, bartender-confident — people come here for DRINKS + elevated Mexican dishes.

The graphic identity runs with EDITORIAL POLISH (restrained grids, refined serifs, controlled palette) to signal seriousness — but the activations run with CONFIDENT ENERGY (oversized type, bold color blocks, after-hours moodiness when the register calls for it) to signal life. Editorial discipline ↔ party energy. Never drop either side.

BRAND-IDENTITY ANCHOR (NON-NEGOTIABLE): Blue Mezcal = BLUE + CREAM. Cobalt #1E3A8A and bone cream #F3ECD8 are the DOMINANT 60/30 pairing on every post — one must dominate, the other must support. This is the colour signature of the account. Every post should be recognizable as Blue Mezcal in under one second based on palette alone.

COMPLEMENT PALETTE (ACCENTS ONLY — never dominant, each capped at under 10-15% of canvas):
- Marigold #F2A900 — accent word or ornament only
- Agave green #4E6B3A — occasional pull only
- Chile red #D72638 — complement for warm-dish photos only
- Charred black #1C1A17 — footer / small-caps ink only

FORBIDDEN in the playful register: burgundy-dominant grounds, brass-foil-on-black nocturnal treatment (that's a separate stem), turquoise, hot pink, any color outside the locked palette above.

PRIMARY GROUND OPTIONS (pick one, always with 5–10% tonal gradient — never flat):
- Cobalt #1E3A8A → deep midnight-cobalt #14213D gradient field
- Bone cream #F3ECD8 → warm ivory #E8DBB8 gradient field
- OR a two-field split (cobalt + bone) with the photo bridging or sitting in one field

TYPE TREATMENT: refined editorial serif (Canela / GT Sectra / Tiempos Headline) as hero. Playful moves ALLOWED: italic at odd scale, one word larger than the rest, hairline hand-drawn underline, script+serif dual-weight lockup, oversized type that wraps or interacts with the photo (Chomp City move, earned — max 1 in 6 posts). Body/labels in quiet grotesque small-caps (Söhne / Neue Haas / GT America). White/cream type on cobalt, cobalt type on cream. NEVER use all three colors (cobalt + cream + a complement) at equal weight — palette always reads blue-and-cream first.

COHESION TEST (applies to EVERY post): at least TWO of these three must appear, or the post fails review:
  1. A refined serif in italic OR small-caps, at some scale
  2. Cobalt + bone-cream dominant in 60/30 ratio (one register per post, never mixed with the nocturnal brass/burgundy)
  3. A 5-12% tonal gradient on at least one color field (never a pure flat hex fill)

PHOTO-LED COMPLEMENT RULE (mandatory): analyze the dominant hue of the supplied drink/dish photograph first. Pick the ground colour that OPPOSES that dominant hue:
  - Warm drink (amber, yellow, orange, peach) → cobalt #1E3A8A ground (cool opposes warm)
  - Cool/green drink → bone cream #F3ECD8 or warm marigold accent
  - Dark drink → bone cream ground for pop
  - Light/pale drink → cobalt ground for contrast
State which hex you chose and why before composing.

COMPOSITION ENERGY: asymmetric layouts OK. A single oversized word (the drink/dish name) taking 40–50% of canvas, with a small smart-mouthed supporting phrase nearby. Or a full-bleed photo with a cobalt band wrapping one edge and a marigold hand-drawn accent. Rule-of-thirds, tension, movement. NOT symmetric menu-card layouts.

HAND-DRAWN ACCENT (Blue Mezcal — OPTIONAL, not every post): Zero or one hand-drawn mark per layout — default is ZERO, add only if the composition asks for it. When used, draw from a small library of BM-world vector ornaments (inked hairline, made-by-human feel): agave leaf or whole plant silhouette, salt-rim arc, citrus wedge cross-section, smoke curl, single dot, mezcal worm outline, hand-drawn hairline underline, ice-cube cube, cocktail-stirrer line. Rotate — agave is ONE option, not mandatory. Never stack multiple ornaments. If the layout already has photo + type doing the work, skip the ornament entirely.

COPY PERSONALITY RULE (critical — NOT every post leads with the dish/drink name):
When option (b) or (c) is used, the subject name can drop to small-caps subhead size or disappear entirely — the photo carries identification. Default: mix across a variation set.

VOICE SEED (Blue Mezcal-only — do not reuse across other brands): editorial-modernist, ENGLISH ONLY (no Spanish — that's Azteca territory), mezcal-reverent, bartender-confident, social-bold. Voice examples: "Smoke, citrus, slow." · "Cool and dangerous." · "One more. You'll survive." · "Impossible to have one." · "Another round?" · "A handshake in a glass." Voice is literary + confident + social, NOT smart-mouth punchy (that's JH) and NOT celebration-warm (that's AZ). Poetic mood-lines, agave-culture references, bartender-confident statements — ALL IN ENGLISH. Never render Spanish phrases on BM posts. When writing COPY OPTION (c), ANALYZE THE SPECIFIC DRINK (spirit base, technique, garnish, feeling on the palate) and write 2–3 candidate lines drawn from THIS BM voice and THIS drink.

TEXTURE: fine noise grain 3–5% on every flat field, subtle handmade paper grain, Portra 400 film grain on photography (daylight-bright, not dark-nocturnal). NO neon, NO velvet burgundy, NO brass foil (that's the nocturnal register).

Photography style: bright editorial daylight 5200K OR soft tungsten 3000K — the drink/dish glows, amber bokeh in the background is fine, but the overall mood is WARM AND INVITING, not dark-moody. 45–60% fill band — editorial restraint with energy.""",

    "blue_mezcal_nocturnal": """A social media image for Blue Mezcal, nocturnal after-dark register — insider mezcal bar at 11pm. Reference anchors: Casa Azul NYC after-hours, Leyenda, Ghost Donkey — BUT rendered in Blue Mezcal's OWN palette. Deep-blue editorial restraint, NOT nightclub neon, NOT black+gold steakhouse. Blue Mezcal nocturnal stays BLUE.

PRIMARY GROUND: deep midnight cobalt #14213D transitioning to near-black cobalt #0A1328 as a subtle tonal gradient (5–10% shift, darker toward one corner) — NEVER a flat fill. Deep blue shadow falloff. Charred black #0B0B0B may be a minor corner accent only (<10%); it is NOT the primary ground. The post must read BLUE at first glance, not black.

PRIMARY TYPE TREATMENT: METALLIC BLUE GRADIENT FOIL on headlines — bright cobalt #1E3A8A → deep sapphire #0E2A7A → bright cobalt #1E3A8A as a soft 3-stop gradient reading like embossed foil on cocktail-menu cardstock. Add a specular highlight and a 1px deeper-shade inner edge so type reads as actual metallic foil, not flat blue. Secondary type in warm tan #E8DBB8 or warm cream #F2EADF.

BRAND PALETTE (nocturnal): midnight cobalt #14213D ground dominant. Metallic blue foil #1E3A8A for hero type. Velvet burgundy #4A1621 used as a DEEP TONAL GRADIENT SUB-FIELD at one corner only (darker toward the corner, fading to near-ground) — burgundy is an ACCENT, never dominant, cap at 15%. Warm tan #E8DBB8 for body type and hairline rules. Bone cream #F3ECD8 for supporting accents. NO brass foil. NO metallic gold. NO black-dominant grounds. The nocturnal register = DEEP BLUE with burgundy + tan accents.

TYPOGRAPHY: refined editorial serif italic (Bodoni / Canela / Didot feel) rendered AS metallic blue foil for hero, paired with small-caps grotesque labels in warm tan or warm cream. Hairline blue or tan rules separating sections. Tight tracking on italics.

TEXTURE: fine noise grain 5–8% overlay on every field; subtle paper-grain impression UNDER the metallic-blue-foil type (as if foil stamped on textured menu cardstock); 35mm Portra 800 film-grain emulation on all photography; faint edge vignette pulling focus inward.

Photography style: moody low-light, tungsten 2700K, single rim light from upper-right at 45°, deep blues, the drink/dish glows while the surroundings fall away into cobalt shadow. 40–50% fill band — confident restraint.""",

    "savora_studio": """A social media image for SAVORA — a restaurant-focused creative studio / MEDIA PRODUCTION AGENCY based in Middletown, Delaware. Savora is NOT a restaurant and NOT an aspirational lifestyle brand. Savora is a PHOTOGRAPHY, VIDEO, AND BRAND-SYSTEMS studio that sells its expertise to restaurant operators. Every post is a PHOTOGRAPHY-MONOGRAPH entry demonstrating craft — not a dish ad. The client's food in the reference photo is the PROOF OF WORK. The graphic must read "this was directed, lit, framed, and produced by a studio that knows what it's doing" — not "this looks tasty, come eat it."

VISUAL REGISTER (NON-NEGOTIABLE — matches savoramarketing.com CSS):
Dark luxury photography monograph. Reference anchors: Aesop product catalogue, Bottega Veneta editorial, Frenchette menu back cover, Blackbird Spyplane photo essay, the inside cover of a monograph book from Aperture or Phaidon. Matte-black ground with deep-teal elevated surfaces. Metallic gradient accents (orange foil, gold foil, teal foil) used as RARE typographic emphasis — like embossed foil-stamp on a dark menu card. Warm off-white type floating over the dark field. Never cream-flat-Kinfolk (that was v1, rejected). Never bright-agency-portfolio. Never Instagram-meme.

BRAND PALETTE (site-matched — NON-NEGOTIABLE):
GROUNDS (pick ONE per post, always with 8-14% tonal gradient — never flat fill):
- NEAR-BLACK #00060B — primary ground, 60-80% dominance (reads dark with a teal undertone)
- BACKGROUND-DEEP #010908 — darker edge for tonal gradients
- ELEVATED DEEP TEAL #062423 — elevated surface for type blocks / metric-card grounds (secondary ground option)

TYPE INK ON DARK GROUNDS:
- WARM OFF-WHITE #D9D4CE — primary body/label ink
- BRIGHT WARM #F2EFEB — hero-headline ink where foil is not used
- MUTED TEAL #7B9693 — secondary support ink for small-caps labels

METALLIC GRADIENTS (RARE ACCENTS — used as foil-stamp on hero type or small seals, NEVER flat fills, NEVER entire fields):
- METALLIC ORANGE FOIL: #F2B480 → #C2612C → #7A3A13 (3-stop gradient reading as embossed copper-foil on matte black cardstock — specular highlight + 1px darker inner edge). PRIMARY ACCENT. Used for hero headlines on ~35% of posts.
- METALLIC GOLD FOIL: #F7DA7F → #E0B045 → #8A621A (3-stop gradient reading as brushed brass). SECONDARY ACCENT. Used for Savora seal + occasional masthead word.
- METALLIC TEAL FOIL: #2B8C83 → #145A55 → #073733 (3-stop gradient reading as patinated copper-teal). TERTIARY ACCENT. Used for hairline rules, small borders, rare kicker words.

DOMINANCE RULE: dark ground 65-80%, off-white type 12-18%, metallic foil accent capped at 10% of canvas (never more than one hero-foil lockup per post). Every post must read DARK-AND-METALLIC at first glance, not cream-and-teal.

Every Savora post must pass the one-second test: a viewer scrolling past sees "dark luxury photography studio" in one second based on ground + metallic accent + warm-off-white type + Gambarino-feel serif. If the post reads restaurant-brand, Monocle-flat, or agency-bright — REJECT.

TYPOGRAPHY (monograph register):
- HERO DISPLAY: Gambarino (primary — condensed luxury serif with Didone-inflected contrast) OR Fraunces (acceptable fallback — opsz 72+ for display, italic for mood, roman caps for authority). TIGHT tracking. Either rendered as WARM OFF-WHITE on dark ground OR as METALLIC ORANGE FOIL gradient (3-stop, specular) on dark ground. Foil is used ONCE per post max.
- SANS LABELS & SMALL-CAPS: Geist (primary) OR Outfit / Söhne — wide-tracked (0.22–0.28em) small-caps for kickers, credits, addresses, window-labels. Warm off-white or muted teal. 13–22pt equivalent.
- MONO (metric numerals ONLY): JetBrains Mono / Geist Mono bold — tabular numerals, warm off-white or metallic-orange-foil gradient. Never body copy.

VOICE (THE CRITICAL PIVOT — PHOTOGRAPHY-CRAFT REGISTER, NOT DISH-SALES):
Savora's voice on its own feed documents THE WORK of making the image — not the dish in the image. Headlines name LIGHT, LENS, TIME-OF-DAY, FRAME-COUNT, COMPOSITION DECISIONS, CLIENT BRIEF, or the PHOTOGRAPHIC MOMENT. They do NOT name flavor, ingredients, or dish mood. The restaurant brand already owns dish-voice; Savora owns craft-voice.

ALLOWED (photography-craft register) — headline EXAMPLES for calibration:
- "Tungsten at 2800K. One rim light. Portra 800 push."
- "Window-soft at 3:47pm. Twelve minutes of light."
- "Eighty-five at f/2.8. Shutter dropped for the char."
- "Overhead. Five inches above the rim. Steam caught on the second take."
- "Single bounce card camera-right. The rest is the chef."
- "Close-crop on the garnish. Backed off the plate."
- "Shot for Blue Mezcal. Twenty-eight frames. This one earned its place."
- "Forty minutes to set the key. Four seconds to shoot it."
- "Available light. Chosen frame."
- "Pre-pro Tuesday. Shot Thursday. Delivered Friday."
- "Portra 400. Pushed one stop. Warm tungsten through a single north window."
- "Restraint carried the image."
- "Twelve setups. One kept."

FORBIDDEN VOICE (automatic reject — this is the v1 mistake):
- ANY dish-descriptor language: "Bourbon. Smoke. A handshake.", "Cool and dangerous.", "Cream inside, good bread beside.", "Hot. Honest. House-made.", "Classic for a reason.", "Grilled. Charred. De la casa." — these are RESTAURANT-BRAND voice, not Savora voice. If a line could belong on the restaurant's own feed, it fails Savora's review.
- ANY flavor / ingredient / mood line about the food itself (that's the client's job)
- Agency-speak: "elevate your brand", "next-level", "stand out", "results-driven", "innovative"
- Emoji chains, hype punctuation, fake urgency
- Comparisons to other studios
- Pitch-deck adjectives

CREDIT RULE (mandatory on every hero-portfolio post): "SHOT FOR [CLIENT NAME]" rendered as small-caps Geist tracked wide 0.22em in muted teal #7B9693 or warm off-white #D9D4CE, typographic only, never the client's logo. Subhead size (14–20pt equivalent). Sits near the Savora signature, often in a footer strip or sidebar.

FORBIDDEN VISUAL (automatic reject):
- Cream/ivory/bone grounds dominant (that was v1 — rejected; Savora is DARK)
- Flat-Kinfolk editorial (Monocle cream register — rejected)
- Neon / cyberpunk / 80s gradients
- Drop shadows on type (except 1px dark drop for legibility over photo)
- Canva-stock illustrations or Unsplash stock
- Agency grid-of-screenshots portfolio layouts
- Any cinematic teal-and-orange GRADING applied to the reference photo (teal and orange are TYPE/INK colors, not photographic grade — the client photo stays color-accurate)
- Any visual that reads Instagram-meme before photography-monograph

COMPOSITION DEFAULTS:
- 55-65% negative space on type-first layouts. Dark restraint.
- Full-bleed client photography allowed WHEN the photo carries it. When full-bleed, type sits in a dark-gradient strip (top, bottom, or side band) with warm off-white type or metallic foil headline.
- Hairline metallic-teal rules (1px, 40-60% opacity gradient) separate sections — replacing flat-teal hairlines.
- Small-caps Geist tracked-wide kicker sits above headlines as a magazine dept-label.
- Metric cards: HUGE mono numeral + warm-off-white unit label + context + window + caveat. Dark ground. Metallic-orange-foil only on numeral optionally.

PHOTOGRAPHY POSTURE: reference photo is Savora-shot client work. Portra 400/800 grain stays ON THE PHOTO, never on type. Warm tungsten or editorial daylight. The photo enters the composition UNTOUCHED, pixel-accurate — never regenerated, restyled, or color-shifted to fit the dark ground. The photo is a JEWEL on a matte-black jewelry-display card — the dark ground serves the photo, not the other way around.

SAVORA SEAL (OPTIONAL, once per post max): small circular METALLIC-GOLD-FOIL hairline mark, 72–96px diameter, reading "SAVORA" small-caps tracked on the ring OR "SAV / ORA" two-line center, sitting bottom-right or bottom-left. If the composited Savora PNG is attached at 80-120px, skip the drawn seal — don't double up.

HAND-DRAWN ACCENT (DEFAULT ZERO): Savora carries no illustrated ornaments. The photograph + dark editorial grid + metallic foil do the work. If absolutely needed for a manifesto post, the only allowed mark is a single metallic-teal hairline rule at 40% width or a small metallic-gold seal outline. NEVER agave / warrior / wheat / chile (client brands).

CROSS-BRAND ISOLATION (Savora is the PARENT):
- Savora's wordmark "SAVORA" is the only brand rendered as display type
- Client names appear ONLY as small-caps typographic credits — never client logos
- Do NOT adopt client palettes (cobalt-cream for BM, black-brass for JH, chile-red for AZ). Savora stays DARK-TEAL-AND-METALLIC regardless of whose photo is featured.

LOGO RULE: supplied SAVORA logo PNG is the only logo composited. 80-120px bottom-center or bottom-left. Never redraw. If no PNG attached, small typographic "SAVORA" wordmark in Gambarino/Fraunces italic 32-44pt, warm off-white at 60-70% opacity, is acceptable as text signature.

LOCATIONS FOR ADDRESS/FOOTER: "Middletown · Delaware — Restaurant Studio" OR "Savora · savoramarketing.com · DE" — rendered small-caps Geist tracked wide 0.22em in muted teal #7B9693 or warm off-white #D9D4CE at 12-14pt equivalent.

PHOTO-TO-FIELD TRANSITION: soft 40-80px gradient dissolve from full-bleed photo edge into dark ground (never a hard knife-edge). No diagonal slashes. No Canva wedges.

TEXTURE:
- 5-8% fine noise grain on dark grounds (film-emulsion impression)
- Subtle paper-grain UNDER metallic-foil type (as if foil-stamped on dark linen cardstock)
- Portra 400/800 grain on photography only
- NO halftone dots (Azteca), NO brass foil on WARM-CREAM ground (Jackson House), NO cobalt-blue fields (Blue Mezcal). Savora's foil register is ORANGE + GOLD + TEAL metallic on DARK.""",

    "jackson_house_tavern": """A social media image for Jackson House — a higher-end American tavern (Delaware Today 2025 Best New Restaurant). The register is PREMIUM-HERITAGE: cocktail-menu elegance balanced against comfort-food warmth. Think foil-stamped cocktail menu or a Gage & Tollner / Frenchette editorial — NOT rustic farm-table cream paper.

PRIMARY GROUND: deep charred black #0A0A0A to inky charcoal #1A1612, with a subtle tonal gradient across the field (5–10% shift, darker toward one edge) — NEVER a flat fill.

PRIMARY TYPE TREATMENT: METALLIC BRASS GRADIENT FOIL on headlines — brass #C9A24B → antique gold #B08937 → brass #C9A24B as a soft 3-stop gradient reading like foil-stamp highlight catching light. Add a subtle specular hotspot and a 1px deeper-shade inner edge so type reads as actual foil on paper, not flat colour. Secondary type in warm cream #F2EADF or antique gold.

BRAND PALETTE: black #0A0A0A / deep charcoal #1A1612 ground. Brass #C9A24B metallic foil as hero type. Forest green #1F3B2D used as a DEEP TONAL GRADIENT field (darker at the bottom, almost black in the corners — never flat green). Oxblood #5B1A1A used the same way — deep gradient field, never flat. Warm cream #F2EADF for body type and accent rules. Mustard #C8962F as rare accent only. The National-Cocktail-Day Jackson House flyer aesthetic is the reference — gold foil menu elegance on black.

TYPOGRAPHY: old-style serif display (Farnham / Sentinel / Caponi) rendered AS metallic brass foil + condensed all-caps grotesque labels (Knockout / Trade Gothic) in warm cream. Hairline brass rules separating sections.

TEXTURE: fine noise grain 5–8% overlay on every field; subtle paper-grain impression UNDER the brass-foil type (as if foil stamped on textured bookbinding paper); Portra 800 film-grain emulation on all photography; faint edge vignette. NO rustic cream kraft paper, NO letterpress-on-ivory (that reads too casual-wedding). This is foil-stamped elegance, not farm-table rustic.

VOICE SEED (Jackson House-only — do not reuse across other brands): classical, warm, telegraphic, knowing-confident. Voice examples from the JH feed: "You already know." · "Some things don't need to be complicated." · "Warm out of the oven. Butter melts on contact." · "Reserve your table." Tavern-confident, not ironic, not celebratory — the register of a chef who trusts the food. When writing COPY OPTION (c), ANALYZE THE SPECIFIC DISH (its comfort-food heritage, its texture, the moment it's eaten) and write 2–3 candidate lines drawn from THIS voice and THIS plate. Do NOT use Spanish phrases (wrong brand — AZ/BM only). Do NOT use celebration-warm voice (AZ) or poetic-moody voice (BM).

HAND-DRAWN ACCENT (Jackson House — OPTIONAL, not every post): Zero or one mark per layout — default is ZERO. When used, pull from JH-world library rendered as BRASS-FOIL HAIRLINE OR INKED WARM-CREAM hairline: wheat sheaf, rolling pin, butter pat silhouette, fork-and-knife cross, flame curl, cast-iron skillet outline, single olive sprig, coffee bean, wine-glass silhouette, hairline brass underline rule. NEVER agave (that's BM). NEVER warrior/chile (that's AZ). Never stack ornaments. If photo + foil type already carry the layout, skip the ornament entirely.

PHOTOGRAPHY: warm tungsten candlelight 2800K, shallow depth of field, Portra 800 film look, deep blacks, rich midtones. Comfort food stays photographed as comfort food — generous portions — but the type treatment elevates it. Balance: approachable dish, elevated frame.""",
}


# Brand → default stem key(s) + CTA + addresses
BRAND_META = {
    "azteca": {
        "default_stem": "azteca_playful",
        "alt_stems": ["azteca_heritage"],
        "address_line": "Camden · Dover · Rehoboth — link in bio",
        "wordmark": "EL AZTECA",
        "bilingual": "heavy",
        "logo_file": "el_azteca.png",
        "award_badge": None,
    },
    "blue_mezcal": {
        "default_stem": "blue_mezcal_editorial",
        "alt_stems": ["blue_mezcal_nocturnal"],
        "address_line": "826 Kohl Ave · Middletown, DE — Visit us · link in bio",
        "wordmark": "BLUE MEZCAL",
        "bilingual": "accent",
        "logo_file": "blue_mezcal.png",
        "award_badge": None,
    },
    "jackson_house": {
        "default_stem": "jackson_house_tavern",
        "alt_stems": [],
        "address_line": "17 Wood St · Middletown, DE — Reserve your table · link in bio",
        "wordmark": "JACKSON HOUSE",
        "bilingual": "none",
        "logo_file": "jackson_house.png",
        # Every JH post includes a subtle mention of the award per Hector (2026-04-21)
        "award_badge": "Best New Restaurant · Delaware Today 2025",
    },
    "savora": {
        "default_stem": "savora_studio",
        "alt_stems": [],
        "address_line": "Middletown · Delaware — Restaurant Studio · savoramarketing.com",
        "wordmark": "SAVORA",
        "bilingual": "none",
        "logo_file": "savora.png",
        "award_badge": None,
    },
}


# ============================================================
# FORMAT → SCENE TEMPLATE (one per post-format taxonomy entry)
# ============================================================

@dataclass
class FormatSpec:
    description: str
    default_aspect: str
    composition_cue: str


FORMATS = {
    "hero_dish_editorial": FormatSpec(
        description="Editorial hero dish spotlight. Single plate, asymmetric crop, restrained type. One focal point on a rule-of-thirds intersection. Canvas FILL targets (enforce the upper band — no under-filling): Blue Mezcal 50–65% fill, Jackson House 65–75% fill, Azteca 80–95% fill.",
        default_aspect="4:5",
        composition_cue="rule-of-thirds focal point, asymmetric composition, 4:5 portrait; photo fills the canvas at full scale; headline and sub in a color-block field tucked into one corner or band (never shrinking the photo)",
    ),
    "cocktail_spotlight_moody": FormatSpec(
        description="Moody beverage spotlight. Single rim-lit cocktail glass, black or charred background, hand entering frame optionally. Type integrated as if printed on the menu, not overlaid as a sticker.",
        default_aspect="4:5",
        composition_cue="3/4 macro shot, 85mm equivalent at f/2.8, single rim light from upper-right at 45°, tungsten 2800K, Portra 800 grain, focus on rim and garnish",
    ),
    "ingredient_anatomy": FormatSpec(
        description="Ingredient breakdown / anatomy of a dish. Overhead flat-lay with components fanned; thin hand-drawn lines label each part. La Bamba / Bon Appétit lineage.",
        default_aspect="1:1",
        composition_cue="overhead flat-lay, 5500K daylight, components arranged in a visual sentence; thin hand-drawn marker lines radiating from each component to small typed labels in the negative space",
    ),
    "recurring_weekly": FormatSpec(
        description="Recurring weekly anchor (Taco Tuesday, Margarita Monday, Thirsty Thursday, Brunch). Large day-of-week wordmark dominates; feature photo secondary.",
        default_aspect="1:1",
        composition_cue="top-third dominated by display-type day wordmark, bottom-two-thirds feature product photo, off-axis 3° rotation on stickered elements for Azteca register",
    ),
    "seasonal_holiday": FormatSpec(
        description="Holiday / seasonal card (Cinco de Mayo, Día de los Muertos, Mother's Day). Motif or illustration anchors; no primary food photo.",
        default_aspect="1:1",
        composition_cue="single-image statement with restrained type; motif or line-drawn ornament; headline + date + short message",
    ),
    "event_announcement": FormatSpec(
        description="Event announcement poster (menu launch, live music, pop-up, collab). Poster-aesthetic typographic stack.",
        default_aspect="1:1",
        composition_cue="symmetric menu-card layout OR photo-bed with 30% black overlay and horizontal date band across middle",
    ),
    "operational_notice": FormatSpec(
        description="Operational notice (closed, hours change, reservation reminder). Plain, no photo. Flat brand background, big headline, subtle brand motif.",
        default_aspect="1:1",
        composition_cue="flat brand-color background, big left-aligned headline, short body, small brand motif in one corner",
    ),
    "quote_post": FormatSpec(
        description="Typographic-only quote post. Type IS the image at 60–80% of canvas. Never a decorative photo behind a quote.",
        default_aspect="1:1",
        composition_cue="single-color field background; oversized display serif or display sans occupies 60–80% of canvas; attribution small-caps beneath",
    ),
    "reservation_prompt": FormatSpec(
        description="Reservation prompt. Moody interior or empty set table; italic overlay at bottom; URL tiny.",
        default_aspect="4:5",
        composition_cue="3/4 photograph of set table at golden hour; small italic serif overlay in upper-third negative space; hairline rule; small-caps CTA at bottom margin",
    ),
    "behind_the_scenes": FormatSpec(
        description="Documentary BTS. 35mm film-look. Hands, fire, steam, prep, sourcing. Minimal or no graphic overlay.",
        default_aspect="9:16",
        composition_cue="documentary still, 35mm equivalent at f/2.0, tungsten kitchen lighting 2800K, focus on hands/tools, heavy Portra 800 grain, no graphics",
    ),
    "typographic_poster": FormatSpec(
        description="Type-as-image. Oversized display at 50–90% of canvas, photography reduced to accent or texture. Short phrase — one to six words.",
        default_aspect="4:5",
        composition_cue="display type occupies 50–90% of canvas; tight leading 1.05–1.15; optional texture or subtle accent; no photograph or photo as texture only",
    ),
}


# ============================================================
# VARIATION ANGLES — each variation gets distinct composition bias
# ============================================================

VARIATION_ANGLES = [
    # All angles respect HERO-PHOTO RULE: photo fills primary region at full
    # scale. Angles below are drawn from a study of five reference posts
    # (Fly By Jing, drinkghia, sweetgreen, 2026-04-21): clever copy + ruthless
    # type hierarchy + confident binary ground choice + pop-word devices.
    "Variation 1 — FLY-BY-JING MOVE. Ground is a saturated brand-color gradient (cobalt→midnight / oxblood→black / marigold→chile-red, brand-appropriate) covering the full canvas. Photo of the dish/drink sits RIGHT-HALF (roughly 50–55% of canvas), cleanly composed against the gradient. Headline sits LEFT-HALF at Knockout-style condensed sans caps, 180–260px equivalent, in warm ivory or a contrasting brand-palette hex. ONE KEY WORD in the headline is wrapped in a highlighter-block (bright yellow / marigold / brand-accent rectangle behind just that word). Clever analogical copy preferred — COPY OPTION (c) derived from dish + brand voice.",
    "Variation 2 — GHIA CLEAN-GROUND ELEGANCE. Pure ivory / warm-cream / bone-white ground (#F3ECD8 or #F7F2E6, never pure #FFFFFF — always with subtle tonal gradient). The drink/dish photo sits as the clear hero, centered or slightly off-center, 55–70% of canvas, the product's own color doing the visual work. Headline overlay in UPPER-LEFT: SERIF CAPS pairing (e.g. \"ALL ABOUT\" small caps + bigger SCRIPT / ITALIC of the dish name) OR simply a deep-wine / cobalt serif caps drink-name treatment. Deeply elegant, minimal, high-end product-photography feel. COPY OPTION (a) works well; (c) if a poetic line fits.",
    "Variation 3 — 101 EDITORIAL / EDUCATIONAL FOOTER BAND. Photo fills the top 65–70% of canvas at full scale (overhead or 3/4 composition). Bottom 30–35% is a LOUD saturated brand-color band carrying the main headline in two weights: one oversized term in brand-accent color + \"101\" in a contrasting color at equal size (e.g. \"MARGARITA 101\" or \"MEZCAL 101\"), plus a small-caps one-line subhead below (\"everything you need to know before the first sip\"). A small brand-masthead strip (~8% height) runs along the top with the wordmark. COPY OPTION uses topical-educational phrasing, not dish-name-first.",
    "Variation 4 — photo full-bleed; headline in a vertical color-block STRIP down the LEFT 30% of the canvas, photo occupies the right 70% at full scale. CRITICAL: type sizes to fit the strip — large enough to read, never cramped. Multi-line headline stacks vertically within the strip; never rotates 90°. Optional single brand-world vector ornament low in the strip (zero or one only — NOT always agave; pick from BM library). Headline uses COPY OPTION (a).",
    "Variation 5 — SWEETGREEN AWARD MOVE. HARD RULE: photo occupies ≥55% of canvas, full-bleed, NOT cropped to leave a text zone larger than 45%. Type lockup is confined to a BOTTOM-THIRD STRIP ONLY (bottom 30–35% of canvas) or a TOP-THIRD STRIP — never both, never middle. Within the strip: (i) a SMALL italic serif mock-award line (\"Best [X] in a [Y]\" — e.g. \"Best Kick in a Margarita\"), (ii) LOUD sans-caps dish name in brand-accent color at 180–240px equivalent. Strip has semi-opaque ground so photo stays legible underneath. NO dead space — if the composition ends up with large empty regions, shrink the strip and expand the photo. COPY: mock-award line is (c)-derived, dish name is (a) verbatim.",
    "Variation 6 — RECIPE SIDEBAR / INGREDIENT EDITORIAL. Photo fills the RIGHT 60% of canvas at full scale. Left 40% is a quiet brand-palette field carrying: (i) drink/dish name in small serif at top, (ii) 3 ingredient lines stacked in small-caps with hairline rules between (e.g. \"BLANCO TEQUILA · LIME · CUCUMBER\"), (iii) a one-line method at the bottom (\"shaken, black-salt rim\"). Entire column reads like a cocktail menu page. No color block floats, no wedges cutting the photo. Headline uses COPY OPTION (a).",
    "Variation 7 — DRAMATIC CROP + CLEVER-ANALOGY COPY. Photo is COMPOSED tight on a single visual detail (rim + garnish, condensation, grill marks, crust edge). Type sits in the clean negative-space zone the crop creates. Headline is a CLEVER ANALOGICAL LINE (\"The sourdough of noodles\" style — a cultural-reference joke only THIS dish at THIS brand could say), in bold sans or serif caps. Subject name appears as small subhead below. CONTRAST GUARD applies. COPY OPTION (c) mandatory.",
    "Variation 8 — FRENCHETTE SCRIPT + SERIF LOCKUP. Warm cream ground (#F3ECD8 or #F7F2E6) with subtle tonal gradient. ALL INK IN A SINGLE BRAND-ACCENT COLOR (cobalt for BM, brass for JH, chile-red for AZ) — no 3rd color. Headline uses MIXED-WEIGHT TREATMENT: one word in SCRIPT/CURSIVE (e.g. \"All about\", \"Chef's\"), one word in SERIF CAPS at 1.5× the script size (e.g. \"SPICY\", \"BEST\"), italic emphasis on one supporting word in a subhead. Photo occupies the lower 50% of canvas OR a framed rectangle in the middle. Top strip carries a small-caps fact line (venue · date · event tag). Disciplined editorial one-color restraint. COPY OPTION (c) with italic emphasis.",
]


# ============================================================
# helpers
# ============================================================

def load_cloudinary_urls() -> dict:
    if not CLOUDINARY_URLS_PATH.exists():
        sys.exit(f"Missing {CLOUDINARY_URLS_PATH}")
    return json.loads(CLOUDINARY_URLS_PATH.read_text())


def fetch_image_bytes(url: str, retries: int = 3) -> bytes:
    last: Optional[Exception] = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "savora-nb/2.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Fetch fail {url}: {last}")


def build_scene_paragraph(
    stem_key: str,
    fmt: FormatSpec,
    subject: str,
    support: str,
    address_cta: str,
    wordmark: str,
    variation_angle: str,
    has_reference_photo: bool,
    has_logo: bool = False,
    award_badge: Optional[str] = None,
) -> str:
    """Compose the per-variation scene paragraph that follows the brand stem."""
    stem = BRAND_STEMS[stem_key]

    photo_instruction = (
        "HERO-PHOTO RULE (HIGHEST PRIORITY — cannot be violated):\n"
        "  1. The reference food photograph supplied as input is the CANVAS FOUNDATION of this "
        "     design. It fills the primary region of the composition at FULL SCALE. It is NEVER "
        "     reduced to a small swatch, tile, inset, thumbnail, or decorative element. The photo "
        "     is the hero; the template is LAID OVER IT.\n"
        "  2. Typography, colour fields, motifs, and ornament sit OVER or ADJACENT TO the full-"
        "     size photo — they do not shrink the photo to make room. If a headline needs space, "
        "     use an upper-third or lower-third color-block field ON TOP of the photo, or extend "
        "     negative brand-color margin from one edge of the photo outward (photo still fills "
        "     60–85% of canvas minimum).\n"
        "  3. DO NOT regenerate, restyle, or alter the plating, lighting, colours, or contents "
        "     of the food in any way. The photo must remain photographically identical to the source.\n"
        "  4. Variations that shrink, miniaturize, inset, or tile the photo are REJECTED. "
        "     (User feedback, BM-A1-002: \"I don't want smaller images of what we have, use "
        "     the real images as the template, and design OVER them.\")\n\n"
        "PHOTO-LED PALETTE COMPLEMENT RULE:\n"
        "  The brand-palette colours you choose for headline fields, accent blocks, and type "
        "  MUST COMPLEMENT the photo's dominant hue, not clash with it. If the photo is warm-"
        "  dominant (amber, orange, red, bourbon), pull cooler brand colours (cobalt, deep "
        "  navy, forest) for contrast. If the photo is cool-dominant (blue, green, grey), pull "
        "  warmer brand colours (brass, oxblood, marigold). Name the photo's dominant hue in "
        "  your head first, then pick the brand-palette hex that complements it."
        if has_reference_photo
        else "No photograph is needed for this format — build the composition entirely from "
        "typography, colour fields, motifs, and textures."
    )

    negative_content_lock = (
        "NEGATIVE-CONTENT LIST (NON-NEGOTIABLE — REJECT IF ANY APPEAR ON CANVAS):\n"
        "  Never render these words, phrases, or visual references anywhere on the image,\n"
        "  regardless of brand or content type:\n"
        "    - 'La Bamba' / 'La Bamba Ice Cream' — different brand, never on El Azteca posts\n"
        "    - 'Cumbia Night' / 'live music' — unverified events, do not invent\n"
        "    - 'Altar Menu' / 'Ofrenda Menu' / 'Menu Especial' — unverified seasonal menus\n"
        "    - 'Five Course' / 'Prix Fixe' / '28-day Residency' — do not invent event details\n"
        "    - 'Blue Mezcal Quarterly' / any fake magazine or publication title\n"
        "    - 'Chef's Tasting' / 'Chef's Table' unless supplied as real support copy\n"
        "    - Any named staff ('Selena', 'Marco', 'Elena', 'the House') on any brand other\n"
        "      than the one where that person actually works\n"
        "    - Any phone number, website URL, social handle, or price not supplied\n"
        "  If a layout feels empty without such copy, REDUCE copy rather than invent.\n\n"
    )

    factual_integrity_lock = (
        "FACTUAL-INTEGRITY RULE (NON-NEGOTIABLE — HIGHEST PRIORITY):\n"
        "  This is real restaurant marketing for real clients. Every word rendered on the image\n"
        "  MUST be factually accurate. DO NOT INVENT:\n"
        "    - Staff names, titles, or roles (a person named on a post must actually work there)\n"
        "    - Magazine / publication / quarterly titles ('Blue Mezcal Quarterly' does not exist)\n"
        "    - Issue numbers, edition labels, 'Vol. II' references\n"
        "    - Event names not supplied in this prompt\n"
        "    - Drink names, dish names, prices, dates, times not supplied\n"
        "    - Award names, certifications, rankings\n"
        "    - 'Est. [year]' dates unless supplied\n"
        "    - Fake product lines, merchandise, collaborations\n"
        "  ONLY use factual content that comes from these exact sources:\n"
        "    1. The 'subject' field supplied in this prompt\n"
        "    2. The 'support' field supplied in this prompt\n"
        "    3. The brand profile's documented address, wordmark, and operational lines\n"
        "    4. Documented voice seeds (dichos, signatures) written in the brand stem\n"
        "  If a layout feels empty without more copy, REDUCE THE COPY rather than invent — negative\n"
        "  space is always better than fabricated facts.\n"
        "\n"
        "CROSS-BRAND ISOLATION (non-negotiable):\n"
        "  Staff, bartender, and chef names are brand-specific and NEVER cross between brands.\n"
        "  - Selena = Jackson House bartender ONLY. Never render 'Selena' on a Blue Mezcal or\n"
        "    Azteca post under any circumstance.\n"
        "  - Do not invent team-member names for any brand. If no real staff name is supplied,\n"
        "    skip the personality-credit line entirely.\n\n"
    )

    real_image_lock = (
        "REAL-IMAGE IDENTITY LOCK (NON-NEGOTIABLE — HIGHEST PRIORITY):\n"
        "  The attached reference photograph of the dish/drink is REAL PROFESSIONAL PHOTOGRAPHY\n"
        "  produced by Savora. It is NOT a style reference, NOT a prompt, NOT inspiration. It is\n"
        "  the FINAL DISH IMAGE that must appear verbatim in the output.\n"
        "\n"
        "  YOU MUST NOT:\n"
        "    - regenerate, redraw, repaint, or restyle the dish\n"
        "    - substitute a different-looking version of the dish\n"
        "    - change the angle, lighting, plating, garnish, sauce pattern, char marks, glass shape,\n"
        "      ice, crema, herbs, or any visible element of the actual food\n"
        "    - apply a filter, stylization, or 'photographic re-interpretation' to the plate\n"
        "    - generate a new photograph that looks similar but is not the reference\n"
        "    - AI-hallucinate plausible food textures in place of the real pixels\n"
        "\n"
        "  YOU MUST:\n"
        "    - treat the reference photograph as a LOCKED COMPOSITE LAYER — pixel-accurate, placed\n"
        "      into the design untouched\n"
        "    - match the reference frame-for-frame (same crop, same color, same shadows, same\n"
        "      moisture on the glass, same grill marks on the steak, same garnish position)\n"
        "    - compose the graphic design AROUND, BESIDE, or ON TOP OF the locked photo — never\n"
        "      regenerate the photo itself\n"
        "    - if the layout needs the photo cropped, silhouetted, or cut-out, do so using the\n"
        "      ACTUAL reference pixels — not a re-painted imitation\n"
        "\n"
        "  This is a Savora brand rule. Serving AI-generated food imagery as our photography is\n"
        "  a breach of client trust. The dish pixels are sacred. Design around them.\n\n"
        if has_reference_photo
        else ""
    )

    logo_instruction = (
        "LOGO IDENTITY LOCK (NON-NEGOTIABLE — HIGHEST PRIORITY):\n"
        "  A second reference image is attached — the brand's REAL, APPROVED logo.\n"
        "  You MUST composite the supplied logo PNG VERBATIM at 80–120px tall (~7–10% of\n"
        "  canvas width) in ONE corner: bottom-center, bottom-left, bottom-right, or top-right.\n"
        "\n"
        "  YOU MUST NOT:\n"
        "    - redraw, re-letter, re-illustrate, restyle, or recolour the logo\n"
        "    - invent an alternate version of the warrior / wordmark / brand mark\n"
        "    - combine the logo with other elements inside the logo itself\n"
        "    - generate a 'stylized' or 'custom' version of the logo\n"
        "    - render the brand name as display type anywhere outside the composited logo\n"
        "    - render a faux logo badge, crest, seal, or lockup containing the brand name\n"
        "\n"
        "  The brand name may appear ONLY inside the composited real-logo PNG. All other\n"
        "  typography on the canvas is headline, subhead, or support copy — never a recreation\n"
        "  of the brand logo. Any output that redraws the logo is REJECTED.\n\n"
        if has_logo
        else "NO LOGO ATTACHED: skip the brand-mark entirely. DO NOT invent or generate a logo.\n"
        f"Small text-only wordmark acceptable at 40–80px, 50–70% opacity: \"{wordmark}\"\n\n"
    )

    award_instruction = (
        f"AWARD BADGE (required for this brand): Include a small, low-key reference to "
        f"\"{award_badge}\" as a secondary typographic element — one of: a small-caps tracked "
        f"line near the address / CTA margin, OR a tiny circular foil seal (brass-gradient) "
        f"in an opposite corner from the logo, OR a discreet italic serif line beneath the "
        f"support copy. Keep it subtle — under 24pt equivalent, never overpowering the headline "
        f"or the food photo. The award IS the brand's proof; show it with restraint.\n\n"
        if award_badge
        else ""
    )

    return (
        f"{stem}\n\n"
        f"FORMAT: {fmt.description}\n\n"
        f"COMPOSITION: {fmt.composition_cue}\n\n"
        f"HEADLINE OPTIONS (pick ONE — variation-dependent — see COPY PERSONALITY RULE in stem):\n"
        f"  (a) DEFAULT — subject name verbatim, no paraphrasing, no misspellings: \"{subject}\"\n"
        f"  (b) a feeling/mood line derived FROM THIS SPECIFIC DISH (use the body-copy phrase below as raw material — e.g. if the phrase is \"Black salt rim. Cucumber crown. Cool and dangerous.\" a valid mood line is \"Cool and dangerous.\").\n"
        f"  (c) a personality line DERIVED FROM the specific dish + the brand's voice signature (see VOICE SEED in the brand stem). Do NOT reuse example lines from OTHER brands' voice seeds — generate fresh copy that ONLY makes sense for THIS dish at THIS restaurant.\n"
        f"  Default heavily to (a). Use (b) or (c) only when the line adds real personality and still identifies the dish. If using (b)/(c), subject name may appear as small subhead or be omitted.\n"
        f"BODY COPY (quote exactly when rendered): \"{support}\"\n"
        f"BOTTOM-MARGIN LINE — render this EXACT text at the bottom margin as a single low-key hairline-ruled line: \"{address_cta}\"\n"
        f"NO-LITERAL-LABEL RULE (non-negotiable): NEVER print any of these meta-label words on the final image — they are instructions to you, NOT content to render: CTA, ADDRESS, SUPPORT LINE, FOOTER LINE, BOTTOM-MARGIN LINE, HEADLINE, SUBHEAD, BODY COPY, HEADER, LABEL, COPY OPTION, VARIATION, WORDMARK, AWARD BADGE, WORD-SPILL, DEFAULT. If any of those words leak onto the canvas, the image fails review.\n"
        f"{logo_instruction}"
        f"{award_instruction}"
        f"VARIATION DIRECTION: {variation_angle}\n\n"
        f"PHOTO RULE: {photo_instruction}\n\n"
        f"CONTRAST GUARD (non-negotiable, applies to EVERY text-over-anything decision):\n"
        f"  Before finalizing the layout, estimate the luminance of the type and the luminance of\n"
        f"  whatever sits behind it (ground field OR the pixels of the photo under the type).\n"
        f"  If both are dark (type luma <30%% AND ground luma <40%%) OR both are light (type luma\n"
        f"  >70%% AND ground luma >60%%), REJECT and re-choose. Type must read at arm's length on\n"
        f"  a phone — if legibility is marginal, change the type hex to the opposite luminance pole\n"
        f"  of the brand palette. No dark-on-dark, no light-on-light, ever.\n\n"
        f"TEXT-FIT-CONTAINER RULE (non-negotiable):\n"
        f"  Type SIZES TO THE CONTAINER, not the other way around. If the headline doesn't fit at\n"
        f"  a legible size in the designated color-block / strip / wedge, choose ONE of: (i) shrink\n"
        f"  the type to legibility-min only IF it still reads at arm's length, (ii) expand the\n"
        f"  container to match the type, (iii) break the headline across 2–3 lines with generous\n"
        f"  leading. NEVER cram letters, NEVER rotate 90° to fit a narrow strip, NEVER letter-clip\n"
        f"  at the canvas edge. If a chosen variation angle forces any of these, pick a better\n"
        f"  container geometry.\n\n"
        f"NO-HERO-OCCLUSION RULE:\n"
        f"  Diagonal wedges, horizontal bands across the middle third, and any geometric shape that\n"
        f"  CUTS THROUGH the primary photo region are forbidden. Color fields sit adjacent to the\n"
        f"  photo, extend from one edge inward, or occupy a corner — they never bisect the dish or\n"
        f"  glass. If the chosen variation angle creates a slash through the hero, reshape it.\n\n"
        f"{negative_content_lock}"
        f"{factual_integrity_lock}"
        f"{real_image_lock}"
        f"LUXURY-TEXTURE RULE (non-negotiable):\n"
        f"  * Every colour field MUST have a subtle tonal gradient (5–12% shift from one edge to "
        f"    the opposite edge). NEVER use a pure flat hex fill. Flat fills read cheap and digital.\n"
        f"  * Every colour field MUST carry a texture overlay: 3–8% noise/grain is the minimum. "
        f"    Add one of: cream laid paper, linen weave, letterpress emboss, brass foil, film "
        f"    grain, halftone dots, or risograph misregistration — whichever matches the register.\n"
        f"  * Every typographic element MUST carry texture too: letterpress emboss for Jackson "
        f"    House (type sits AS IF pressed into cream paper, 2px inner-shadow dark edge + 1px "
        f"    light highlight); brass foil with subtle specular for Blue Mezcal nocturnal; ink-"
        f"    bleed / halftone offset for Azteca playful; paper-grain impression for Blue Mezcal "
        f"    editorial.\n"
        f"  * Photography receives Portra 400 or Portra 800 film-grain emulation (depending on "
        f"    lighting register) — never a clean digital file.\n"
        f"  * Where a drop shadow is used, follow the pro spec: y-offset 4–8px, blur 16–40px, "
        f"    opacity 8–20%, colour = a DARKER SHADE of the background (never pure black). "
        f"    NEVER the default Photoshop 5px-90°-75%-black drop shadow.\n\n"
        f"LUXURY-GRADIENT EXAMPLES (pick one that fits):\n"
        f"  * Paper-gradient: cream lightens toward the centre, darkens at the edges (letterpress "
        f"    vignette).\n"
        f"  * Tonal-brand-gradient: cobalt #1E3A8A → #1A3275 in a 5% shift across the field.\n"
        f"  * Foil-gradient: brass #C9A24B → #B08937 → #C9A24B as a soft 3-stop reading like a "
        f"    foil-stamp highlight catching light.\n"
        f"  * Velvet-gradient: burgundy #4A1621 falling into charred black #0B0B0B at one corner, "
        f"    like low candlelight.\n\n"
        f"DROP-SHADOW RULE:\n"
        f"  Only add a drop shadow to type when the palette contrast is INSUFFICIENT on its own "
        f"  (e.g., cream type over a busy mid-tone photo). When contrast is already strong "
        f"  (e.g., brass-foil gold on deep forest green, cream on charred black), OMIT drop "
        f"  shadows entirely — they cheapen the foil-stamp effect. Foil type on a deep tonal "
        f"  field needs no shadow; the foil itself carries the hierarchy.\n\n"
        f"FINAL: Render at the aspect ratio specified via the API (not in prose). Dense typography "
        f"with purpose. Real brand register. No stock gradients, no Canva-template feel. Avoid the AI "
        f"tells: no cyan-to-magenta gradients, no default Poppins/Montserrat/Open Sans, no 33/33/33 "
        f"colour balance, no centered dead-symmetric layouts unless ceremonial, no flat-colour "
        f"fields. Every surface is LAYERED: photo + gradient + noise + emboss / foil / grain."
    )


def generate_one(
    client: genai.Client,
    model: str,
    prompt_text: str,
    aspect_ratio: str,
    ref_image_bytes: Optional[bytes],
    ref_image_mime: str = "image/jpeg",
    logo_bytes: Optional[bytes] = None,
    logo_mime: str = "image/png",
) -> Optional[bytes]:
    parts: list = [types.Part.from_text(text=prompt_text)]
    if ref_image_bytes is not None:
        parts.append(
            types.Part.from_bytes(data=ref_image_bytes, mime_type=ref_image_mime)
        )
    if logo_bytes is not None:
        parts.append(
            types.Part.from_bytes(data=logo_bytes, mime_type=logo_mime)
        )

    # Aspect ratio param support varies across SDK versions; try the typed
    # config, fall back to prose-only if the SDK object rejects it.
    config_kwargs: dict = {"response_modalities": ["IMAGE", "TEXT"]}
    try:
        config_kwargs["image_config"] = types.ImageConfig(aspect_ratio=aspect_ratio)
    except (AttributeError, TypeError):
        pass

    response = client.models.generate_content(
        model=model,
        contents=[types.Content(role="user", parts=parts)],
        config=types.GenerateContentConfig(**config_kwargs),
    )

    for candidate in response.candidates or []:
        for part in candidate.content.parts or []:
            if getattr(part, "inline_data", None) and part.inline_data.data:
                return part.inline_data.data
    return None


def generate_with_retry(
    client: genai.Client,
    prompt_text: str,
    aspect_ratio: str,
    ref_image_bytes: Optional[bytes],
    logo_bytes: Optional[bytes] = None,
) -> tuple[Optional[bytes], str]:
    """Try primary model, fall back to secondary if it errors."""
    for model in (IMAGE_MODEL, IMAGE_MODEL_FALLBACK):
        try:
            png = generate_one(
                client, model, prompt_text, aspect_ratio,
                ref_image_bytes, logo_bytes=logo_bytes,
            )
            if png:
                return png, model
        except Exception as exc:  # noqa: BLE001
            print(f"    ! {model} errored: {type(exc).__name__}: {exc}")
            continue
    return None, ""


# ============================================================
# main
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="Nano Banana parallel variation runner")
    parser.add_argument("--brand", required=True, choices=BRAND_META.keys())
    parser.add_argument("--post-id", required=True)
    parser.add_argument(
        "--format",
        required=True,
        choices=FORMATS.keys(),
        help="Post format from the taxonomy",
    )
    parser.add_argument(
        "--image-key",
        help="Cloudinary filename key (e.g. B-35). Omit for no-photo formats.",
    )
    parser.add_argument("--subject", required=True)
    parser.add_argument("--support", default="")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument(
        "--aspect",
        default=None,
        help="Override default aspect (e.g. 4:5, 1:1, 9:16)",
    )
    parser.add_argument(
        "--stem",
        default=None,
        choices=list(BRAND_STEMS.keys()),
        help="Override default brand stem (e.g. blue_mezcal_nocturnal instead of editorial)",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=5,
        help="Concurrent API calls (default 5)",
    )
    parser.add_argument(
        "--logo",
        default=None,
        help="Path to logo PNG override. Default: BRAND_PROFILES/logos/{brand}.png if present.",
    )
    parser.add_argument(
        "--no-logo",
        action="store_true",
        help="Skip logo attachment entirely",
    )
    parser.add_argument(
        "--no-award",
        action="store_true",
        help="Skip award-badge injection (JH only)",
    )
    parser.add_argument(
        "--backend",
        default="gemini",
        choices=["gemini", "openai", "both"],
        help="Image backend. 'both' splits count evenly: first half Gemini, second half OpenAI.",
    )
    parser.add_argument(
        "--angle",
        default=None,
        help="Override variation angle(s). If set, this exact string replaces the VARIATION_ANGLES pick for every variation in the batch. Used for targeted single-style tests.",
    )
    args = parser.parse_args()

    meta = BRAND_META[args.brand]
    fmt = FORMATS[args.format]
    aspect_ratio = args.aspect or fmt.default_aspect
    stem_key = args.stem or meta["default_stem"]

    # Reference photo
    ref_bytes: Optional[bytes] = None
    ref_url: str = ""
    if args.image_key:
        urls = load_cloudinary_urls()
        if args.image_key not in urls:
            sys.exit(f"Unknown image key: {args.image_key!r}")
        ref_url = urls[args.image_key]
        print(f"[fetch] {args.image_key} → {ref_url}")
        ref_bytes = fetch_image_bytes(ref_url)

    # Logo
    logo_bytes: Optional[bytes] = None
    logo_path: Optional[pathlib.Path] = None
    if not args.no_logo:
        if args.logo:
            logo_path = pathlib.Path(args.logo)
        else:
            default_logo = LOGOS_DIR / meta.get("logo_file", "")
            if default_logo.exists():
                logo_path = default_logo
        if logo_path and logo_path.exists():
            logo_bytes = logo_path.read_bytes()
            print(f"[logo] {logo_path.name}")
        elif logo_path:
            print(f"[logo] WARNING: {logo_path} not found — proceeding without logo")

    award_badge = None if args.no_award else meta.get("award_badge")

    out_dir = ROOT / "OUTPUT" / "nano_banana" / args.brand / args.post_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # Log prompts for reproducibility
    prompts_log = out_dir / "prompts.jsonl"

    gem_client = genai.Client(api_key=API_KEY)

    oai_client = None
    if args.backend in ("openai", "both"):
        if not OPENAI_API_KEY:
            sys.exit("OPENAI_API_KEY missing. Add to /Users/dreamartstudio/Desktop/CLL_PIPELINE/api_keys.py or export env var.")
        from openai_backend import build_client as _oai_build, generate_with_retry_openai  # type: ignore
        oai_client = _oai_build(OPENAI_API_KEY)

    # Decide per-job backend routing
    if args.backend == "gemini":
        backends = ["gemini"] * args.count
    elif args.backend == "openai":
        backends = ["openai"] * args.count
    else:  # both
        half = args.count // 2
        backends = ["gemini"] * half + ["openai"] * (args.count - half)

    # Build prompts for each variation
    jobs = []
    for i in range(args.count):
        angle = args.angle if args.angle else VARIATION_ANGLES[i % len(VARIATION_ANGLES)]
        prompt_text = build_scene_paragraph(
            stem_key=stem_key,
            fmt=fmt,
            subject=args.subject,
            support=args.support,
            address_cta=meta["address_line"],
            wordmark=meta["wordmark"],
            variation_angle=angle,
            has_reference_photo=ref_bytes is not None,
            has_logo=logo_bytes is not None,
            award_badge=award_badge,
        )
        jobs.append((i + 1, angle, prompt_text, backends[i]))

    # Log all prompts
    with prompts_log.open("w") as fh:
        for idx, angle, text, backend in jobs:
            fh.write(json.dumps({
                "variation": idx,
                "backend": backend,
                "brand": args.brand,
                "stem": stem_key,
                "format": args.format,
                "aspect": aspect_ratio,
                "angle": angle,
                "image_key": args.image_key,
                "image_url": ref_url,
                "subject": args.subject,
                "support": args.support,
                "prompt": text,
            }) + "\n")

    print(f"[gemini] primary={IMAGE_MODEL}  fallback={IMAGE_MODEL_FALLBACK}")
    if oai_client:
        print(f"[openai] primary={OPENAI_IMAGE_MODEL}  fallback={OPENAI_IMAGE_MODEL_FALLBACK}")
    print(f"[run] {args.brand} / {args.post_id} / {args.format} / {aspect_ratio} / stem={stem_key} / count={args.count} / backend={args.backend} / parallel={args.parallel}")

    start = time.time()

    def worker(job):
        idx, angle, text, backend = job
        tag = "G" if backend == "gemini" else "O"
        print(f"[gen {tag}{idx:>2}] start — {angle[:55]}...")
        if backend == "gemini":
            png, used_model = generate_with_retry(
                gem_client, text, aspect_ratio, ref_bytes, logo_bytes=logo_bytes,
            )
        else:
            png, used_model = generate_with_retry_openai(
                oai_client, text, aspect_ratio, ref_bytes, logo_bytes=logo_bytes,
                primary_model=OPENAI_IMAGE_MODEL,
                fallback_model=OPENAI_IMAGE_MODEL_FALLBACK,
            )
        if not png:
            print(f"[gen {tag}{idx:>2}] ✗ failed all models")
            return idx, None
        # Filename: when mixed backends, tag the file so viewer can tell
        fname = f"variation_{tag}{idx}.png" if args.backend == "both" else f"variation_{idx}.png"
        out_path = out_dir / fname
        # Write raw first
        out_path.write_bytes(png)
        # Aspect-safe center-crop + resize to IG spec.
        # If source aspect != target aspect, center-crop the long side BEFORE resizing.
        # NEVER non-proportional stretch — that flattens subjects.
        try:
            from PIL import Image
            ig_sizes = {"4:5": (1080, 1350), "1:1": (1080, 1080), "9:16": (1080, 1920),
                        "2:3": (1080, 1620), "3:2": (1620, 1080), "16:9": (1920, 1080)}
            target = ig_sizes.get(aspect_ratio)
            if target:
                im = Image.open(out_path).convert("RGB")
                sw, sh = im.size
                tw, th = target
                src_ratio = sw / sh
                tgt_ratio = tw / th
                if abs(src_ratio - tgt_ratio) > 0.01:
                    # Aspect mismatch — crop
                    if src_ratio > tgt_ratio:
                        # source too wide → crop width centered
                        new_w = int(round(sh * tgt_ratio))
                        left = (sw - new_w) // 2
                        im = im.crop((left, 0, left + new_w, sh))
                    else:
                        # source too tall → crop height TOP-BIASED
                        # (headlines and logos live in upper region — keep more top,
                        # sacrifice more bottom). Ratio: 20% off top, 80% off bottom.
                        new_h = int(round(sw / tgt_ratio))
                        extra = sh - new_h
                        top = int(round(extra * 0.2))  # keep top-heavy
                        im = im.crop((0, top, sw, top + new_h))
                if im.size != target:
                    im = im.resize(target, Image.LANCZOS)
                im.save(out_path, "PNG", optimize=True)
        except Exception as exc:  # noqa: BLE001
            print(f"[gen {tag}{idx:>2}] resize skipped ({type(exc).__name__})")

        # POST-GEN LOGO COMPOSITE — guarantees real logo is on every post,
        # regardless of what the model drew. Covers any model-redrawn logo.
        try:
            if logo_path and logo_path.exists():
                from PIL import Image
                final = Image.open(out_path).convert("RGBA")
                logo = Image.open(logo_path).convert("RGBA")
                fw, fh = final.size
                # Logo sized to ~10% of canvas width
                lw = int(fw * 0.11)
                ratio = lw / logo.width
                lh = int(logo.height * ratio)
                logo = logo.resize((lw, lh), Image.LANCZOS)
                # Position: bottom-right with 28px margin
                mx, my = 28, 28
                pos = (fw - lw - mx, fh - lh - my)
                final.alpha_composite(logo, dest=pos)
                final.convert("RGB").save(out_path, "PNG", optimize=True)
        except Exception as exc:  # noqa: BLE001
            print(f"[gen {tag}{idx:>2}] logo composite skipped ({type(exc).__name__}: {exc})")
        print(f"[gen {tag}{idx:>2}] ✓ {out_path.name} ({out_path.stat().st_size/1024:.0f} KB) via {used_model}")
        return idx, out_path

    with cf.ThreadPoolExecutor(max_workers=args.parallel) as executor:
        list(executor.map(worker, jobs))

    elapsed = time.time() - start

    # Auto-build review grid
    try:
        build_review_grid(out_dir, args.backend)
        print(f"[grid] {out_dir / '_GRID.jpg'}")
    except Exception as exc:  # noqa: BLE001
        print(f"[grid] skipped ({type(exc).__name__}: {exc})")

    print(f"\nDone in {elapsed:.1f}s. Review: open {out_dir}")


def build_review_grid(out_dir: pathlib.Path, backend: str) -> None:
    """4×2 grid composite with per-cell labels."""
    from PIL import Image, ImageDraw, ImageFont  # lazy import

    pngs = sorted(out_dir.glob("variation_*.png"))
    if not pngs:
        return
    imgs = [Image.open(p).convert("RGB") for p in pngs]
    w, h = imgs[0].size
    scale = 400 / w
    nw, nh = int(w * scale), int(h * scale)
    imgs_r = [im.resize((nw, nh)) for im in imgs]
    cols = 4
    rows = (len(imgs_r) + cols - 1) // cols
    grid = Image.new("RGB", (nw * cols, nh * rows), "white")
    d = ImageDraw.Draw(grid)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)
    except Exception:
        font = ImageFont.load_default()

    for i, (im, p) in enumerate(zip(imgs_r, pngs)):
        r, c = divmod(i, cols)
        x, y = c * nw, r * nh
        grid.paste(im, (x, y))
        # Label = filename minus prefix/suffix
        label = p.stem.replace("variation_", "V")
        d.text((x + 8, y + 8), label, fill="yellow",
               font=font, stroke_width=2, stroke_fill="black")

    grid.save(out_dir / "_GRID.jpg", quality=88)


if __name__ == "__main__":
    main()
