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
    "GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image-preview"
)
IMAGE_MODEL_FALLBACK = os.environ.get(
    "GEMINI_IMAGE_MODEL_FALLBACK", "gemini-2.5-flash-image"
)

CLOUDINARY_URLS_PATH = ROOT / "cloudinary_urls.json"
LOGOS_DIR = ROOT / "BRAND_PROFILES" / "logos"


# ============================================================
# BRAND STEMS — verbatim from docs/INTELLIGENCE_FILE.md Part III
# ============================================================

BRAND_STEMS = {
    "azteca_playful": """A social media image for Azteca, a family Mexican restaurant. The register is PLAYFUL-MAXIMALIST FAMILY (La Bamba Ice Cream is the anchor), but with craft discipline — not cheap and not random.

BRAND PALETTE: hot pink #FF5BA7, sunshine yellow #FFD400, turquoise #1FB5B0, chile red #E63946, cream #F8F2DF, cobalt #1A3FA8 (heritage accent). Palette pairings that WORK: pink+red+cream (warm), blue+red (complementary for red-dominant food), pink+cream (soft playful). Palette pairings to AVOID: black+yellow (harsh school-bus), blue+black (flat), mono-saturated flat (cheap). Lean PASTEL-SATURATED rather than flat-saturated — colours feel hand-mixed, paper-stock, poster-printed, not digital Canva.

TYPOGRAPHY DISCIPLINE: bold chunky display sans-serif (Cooper Black / Sharp Grotesk Ultra / Obviously) + friendly rounded sans body + optional hand-painted brush accent. The LETTERS ARE CLEAN AND READABLE — no grain, no dissolve, no knockout, no distress overlay on the type itself. Texture lives in the BACKGROUND FIELD, never in the letterforms. Headlines are crisp. Body reads without effort. Address / award / tiny bottom copy is at least 18–20pt equivalent — NEVER micro-decorative-print.

HAND-DRAWN ARROW RULE (critical — La Bamba signature executed correctly):
  Every hand-drawn marker arrow MUST originate from a short ingredient label (2–4 words: "camarón", "salsa azteca", "aguacate") and TERMINATE at the visible location of that specific ingredient in the food photograph. Before drawing an arrow, name the ingredient + trace the line to the exact pixel location of that ingredient in the supplied photo. Arrows pointing at random sauce pools, empty space, the glass rim, or generic decoration are WRONG. Three to five semantic arrows max — fewer is more. Arrow weight is 2–3px marker, slight hand-wobble, not vector-perfect.

PHOTO-TO-FIELD TRANSITION: where a brand colour field meets the edge of the food photograph, use a 60–120px soft gradient dissolve (the field colour fading to transparent into the photo edge), NOT a hard knife-edge. No diagonal slashes or horizontal colour bands that CUT THROUGH the food photograph. Colour fields sit ADJACENT to the photo or EXTEND FROM one edge outward, never bisect the plate.

TEXTURE: halftone dots at 45° on backgrounds OK. Subtle risograph misregistration OK. Slight off-axis rotation of stickered elements OK. But texture stays OUT of the type. Use less texture overall — family restaurant warmth, not zine-overload.

NO DROP SHADOWS on Azteca layouts — this register is flat-layered playful-maximalist graphic, not dimensional. The layering of coloured fields + halftone + arrows IS the dimension.

LOGO: real Azteca warrior logo (supplied as second reference) placed at 80–120px in a corner, full colour, as-is.

Photography style: daylight-bright, slightly oversaturated, warm Portra 400 film grain ON THE PHOTO ONLY (not added on top of design). Hand-made, family, warm, bilingual Spanish-primary.

VOICE SEED (Azteca-only — do not reuse across other brands): family-warm, bilingual Spanish-primary, celebration energy. Voice examples from the AZ feed: "Guacamole, but make it octopus." · "Not your average appetizer." · "We don't do things halfway." · "Pick your poison." · "Cocktail hour." · "Classic for a reason." Voice is celebratory-familiar, never ironic-detached. When writing COPY OPTION (c), ANALYZE THE SPECIFIC DISH (its ingredients, its regional origin, its role in a Mexican family meal) and write a 2–3 candidate lines drawn from THIS voice and THIS plate. Do NOT use smart-mouth punchlines ("You already know") — that's Jackson House voice, wrong brand. Spanish phrase OK if it fits ("De la casa", "¡Con gusto!", "Auténtico").""",

    "azteca_heritage": """A social media image for Azteca, a family Mexican restaurant, heritage register. Brand palette: cobalt #1A3FA8, marigold #F2A900, chile red #D72638, masa cream #F3ECD8, oxblood #6E1423, turquoise #1FB5B0. Typography: bold display serif (Cooper Black / Obviously feel) paired with handwritten script annotations. Texture: papel picado paper cutouts, halftone overlay, slight off-axis rotation, warm Portra 400 grain. Photography style: overhead flat-lay or three-quarter daylight, 5500K, soft shadow upper-right. Hand-made, bilingual Spanish primary, warm-vernacular heritage-maximalist.""",

    "blue_mezcal_editorial": """A social media image for Blue Mezcal, an upscale agave-forward bar and kitchen. Brand palette: cobalt blue #1E3A8A, bone cream #F3ECD8, marigold #F2A900, agave green #4E6B3A, charred black #1C1A17. Typography: refined editorial serif headlines with tight tracking, paired with quiet modern grotesque small-caps labels. Texture: fine noise overlay at 5%, subtle handmade paper grain, restrained. Photography style: moody low-light with directional rim, tungsten 3000K warmth or editorial 5200K daylight depending on scene. Editorial-modernist restraint, 60–65% negative space.""",

    "blue_mezcal_playful": """A social media image for Blue Mezcal — upscale agave bar, PLAYFUL-EDITORIAL register. Still high-end, but with energy: think Casa Azul NYC × Intelligentsia × Dandelion Chocolate. Editorial spine, more fun than luxury-moody.

BRAND-IDENTITY ANCHOR (critical): Blue Mezcal IS blue + white. Cobalt #1E3A8A and bone cream #F3ECD8 are the dominant pairing. This is the colour signature of the account — every post should be instantly recognizable as Blue Mezcal at a glance. NO burgundy-dominant grounds. NO brass-on-black nocturnal treatment.

PRIMARY GROUND OPTIONS (pick one, always with 5–10% tonal gradient, never flat):
- Cobalt #1E3A8A → deep midnight-cobalt #14213D gradient field
- Bone cream #F3ECD8 → warm ivory #E8DBB8 gradient field
- OR half-and-half split (cobalt + bone) with the photo bridging the seam

TYPE TREATMENT: refined editorial serif (Canela / GT Sectra / Tiempos) as hero, but with playful moves allowed — italic at odd scale, one word larger than the rest, hairline hand-drawn underline, a small ornament (agave leaf, a hand-drawn salt-rim mark, a single dot). Body/labels in quiet grotesque small-caps (Söhne / Neue Haas / GT America). Marigold #F2A900 allowed as a single accent word or ornament only (< 10% of layout). White/cream type on cobalt, cobalt type on cream.

PHOTO-LED COMPLEMENT RULE (mandatory): analyze the dominant hue of the supplied drink/dish photograph first. Pick the ground colour that OPPOSES that dominant hue:
  - Warm drink (amber, yellow, orange, peach) → cobalt #1E3A8A ground (cool opposes warm)
  - Cool/green drink → bone cream #F3ECD8 or warm marigold accent
  - Dark drink → bone cream ground for pop
  - Light/pale drink → cobalt ground for contrast
State which hex you chose and why before composing.

COMPOSITION ENERGY: asymmetric layouts OK. A single oversized word (the drink/dish name) taking 40–50% of canvas, with a small smart-mouthed supporting phrase nearby. Or a full-bleed photo with a cobalt band wrapping one edge and a marigold hand-drawn accent. Rule-of-thirds, tension, movement. NOT symmetric menu-card layouts.

HAND-DRAWN ACCENT (Blue Mezcal signature): one — only one — hand-drawn mark per layout. The APPROVED signature mark is a small hand-drawn agave silhouette (one leaf or whole plant, inked hairline) — use it as the recurring BM ornament when in doubt. Other allowed: hand-drawn salt-rim arc, hairline underline, a single dot. Not six stickers. One precise mark that feels made by a human.

COPY PERSONALITY RULE (critical — NOT every post leads with the dish/drink name):
When option (b) or (c) is used, the subject name can drop to small-caps subhead size or disappear entirely — the photo carries identification. Default: mix across a variation set.

VOICE SEED (Blue Mezcal-only — do not reuse across other brands): editorial-modernist, bilingual accent-only, mezcal-reverent, moody-refined. Voice examples from the BM feed and brand profile: "Smoke, citrus, slow." · "Cool and dangerous." · "Some things don't need to be complicated." · "Para todo mal, mezcal; para todo bien, también." Voice is literary + restrained, NOT smart-mouth punchy (that's JH) and NOT celebration-warm (that's AZ). Poetic mood-lines, agave-culture references, bartender-confident statements. When writing COPY OPTION (c), ANALYZE THE SPECIFIC DRINK (its spirit base, technique, garnish, feeling on the palate) and write 2–3 candidate lines drawn from THIS BM voice and THIS drink. Spanish dicho OK when earned. Do NOT borrow example lines from other brands.

TEXTURE: fine noise grain 3–5% on every flat field, subtle handmade paper grain, Portra 400 film grain on photography (daylight-bright, not dark-nocturnal). NO neon, NO velvet burgundy, NO brass foil (that's the nocturnal register).

Photography style: bright editorial daylight 5200K OR soft tungsten 3000K — the drink/dish glows, amber bokeh in the background is fine, but the overall mood is WARM AND INVITING, not dark-moody. 45–60% fill band — editorial restraint with energy.""",

    "blue_mezcal_nocturnal": """A social media image for Blue Mezcal, nocturnal after-dark register — insider mezcal bar at 11pm. The aesthetic target is a foil-stamped cocktail menu at a high-end agave den: Casa Azul NYC after-hours, Leyenda, Ghost Donkey. Editorial moody-nocturnal restraint, NOT nightclub neon.

PRIMARY GROUND: deep charred black #0B0B0B transitioning to velvet burgundy #4A1621 or smoke gray #2A2825 as a subtle tonal gradient (5–10% shift, darker toward one corner) — NEVER a flat fill. Deep blacks with rich shadow falloff.

PRIMARY TYPE TREATMENT: METALLIC BRASS GRADIENT FOIL on headlines — brass #C9A24B → antique gold #B08937 → brass #C9A24B as a soft 3-stop gradient reading like foil-stamp highlight catching candlelight. Add a specular hotspot and a 1px deeper-shade inner edge so type reads as actual foil on paper, not flat gold. Secondary type in warm white #EDE4D3 or antique brass.

BRAND PALETTE: charred black #0B0B0B / smoke gray #2A2825 ground. Brass #C9A24B metallic foil as hero type. Velvet burgundy #4A1621 used as a DEEP TONAL GRADIENT field (darker at the bottom corners, approaching near-black — never flat burgundy). Warm white #EDE4D3 for body type and hairline rules. Agave green #4E6B3A as rare sub-accent only (<5%). NO cobalt blue in nocturnal register — cobalt is editorial-register only.

TYPOGRAPHY: refined editorial serif italic (Bodoni / Canela / Didot feel) rendered AS metallic brass foil for hero, paired with small-caps grotesque labels in warm white. Hairline brass rules separating sections. Tight tracking on italics.

TEXTURE: fine noise grain 5–8% overlay on every field; subtle paper-grain impression UNDER the brass-foil type (as if foil stamped on textured menu cardstock); 35mm Portra 800 film-grain emulation on all photography; faint edge vignette pulling focus inward. Velvet surfaces, rich shadow falloff. NO rustic cream paper, NO neon, NO flat gold.

Photography style: moody low-light, tungsten 2700K, single rim light from upper-right at 45°, deep blacks, the drink/dish glows while the surroundings fall away. 40–50% fill band — confident restraint.""",

    "jackson_house_tavern": """A social media image for Jackson House — a higher-end American tavern (Delaware Today 2025 Best New Restaurant). The register is PREMIUM-HERITAGE: cocktail-menu elegance balanced against comfort-food warmth. Think foil-stamped cocktail menu or a Gage & Tollner / Frenchette editorial — NOT rustic farm-table cream paper.

PRIMARY GROUND: deep charred black #0A0A0A to inky charcoal #1A1612, with a subtle tonal gradient across the field (5–10% shift, darker toward one edge) — NEVER a flat fill.

PRIMARY TYPE TREATMENT: METALLIC BRASS GRADIENT FOIL on headlines — brass #C9A24B → antique gold #B08937 → brass #C9A24B as a soft 3-stop gradient reading like foil-stamp highlight catching light. Add a subtle specular hotspot and a 1px deeper-shade inner edge so type reads as actual foil on paper, not flat colour. Secondary type in warm cream #F2EADF or antique gold.

BRAND PALETTE: black #0A0A0A / deep charcoal #1A1612 ground. Brass #C9A24B metallic foil as hero type. Forest green #1F3B2D used as a DEEP TONAL GRADIENT field (darker at the bottom, almost black in the corners — never flat green). Oxblood #5B1A1A used the same way — deep gradient field, never flat. Warm cream #F2EADF for body type and accent rules. Mustard #C8962F as rare accent only. The National-Cocktail-Day Jackson House flyer aesthetic is the reference — gold foil menu elegance on black.

TYPOGRAPHY: old-style serif display (Farnham / Sentinel / Caponi) rendered AS metallic brass foil + condensed all-caps grotesque labels (Knockout / Trade Gothic) in warm cream. Hairline brass rules separating sections.

TEXTURE: fine noise grain 5–8% overlay on every field; subtle paper-grain impression UNDER the brass-foil type (as if foil stamped on textured bookbinding paper); Portra 800 film-grain emulation on all photography; faint edge vignette. NO rustic cream kraft paper, NO letterpress-on-ivory (that reads too casual-wedding). This is foil-stamped elegance, not farm-table rustic.

VOICE SEED (Jackson House-only — do not reuse across other brands): classical, warm, telegraphic, knowing-confident. Voice examples from the JH feed: "You already know." · "Some things don't need to be complicated." · "Warm out of the oven. Butter melts on contact." · "Reserve your table." Tavern-confident, not ironic, not celebratory — the register of a chef who trusts the food. When writing COPY OPTION (c), ANALYZE THE SPECIFIC DISH (its comfort-food heritage, its texture, the moment it's eaten) and write 2–3 candidate lines drawn from THIS voice and THIS plate. Do NOT use Spanish phrases (wrong brand — AZ/BM only). Do NOT use celebration-warm voice (AZ) or poetic-moody voice (BM).

PHOTOGRAPHY: warm tungsten candlelight 2800K, shallow depth of field, Portra 800 film look, deep blacks, rich midtones. Comfort food stays photographed as comfort food — generous portions — but the type treatment elevates it. Balance: approachable dish, elevated frame.""",
}


# Brand → default stem key(s) + CTA + addresses
BRAND_META = {
    "azteca": {
        "default_stem": "azteca_playful",
        "alt_stems": ["azteca_heritage"],
        "address_line": "Delaware · Rehoboth — Find your nearest location · link in bio",
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
    "Variation 4 — photo full-bleed; headline in a vertical color-block STRIP down the LEFT 30% of the canvas, photo occupies the right 70% at full scale. CRITICAL: type sizes to fit the strip — large enough to read, never cramped. Multi-line headline stacks vertically within the strip; never rotates 90°. Approved BM signature: small hand-drawn agave-leaf ornament low in the strip (BM only). Headline uses COPY OPTION (a).",
    "Variation 5 — SWEETGREEN AWARD MOVE. Photo full-bleed, dark-cinematic or high-saturation. Two-line headline treatment: (i) a SMALL italic serif line reading \"Best [X] in a [Y]\" style mock-award (e.g. \"Best Kick in a Margarita\" / \"Best Crust in a Comfort Dish\" / \"Best Texture in a Taco\"), (ii) below it the LOUD sans caps dish name in neon-yellow or bright contrasting brand-accent, 200–280px equivalent. Type lives lower-third or lower-left. Photo must be legible underneath; contrast-guard mandatory. COPY: mock-award line is (c)-derived, dish name is (a) verbatim.",
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

    logo_instruction = (
        "LOGO RULE (use supplied logo image as-is):\n"
        "  A second reference image is attached — the brand's ACTUAL logo. Place this logo "
        "  exactly as supplied at roughly 80–120px tall (about 7–10% of canvas width) in ONE "
        "  of these positions: bottom-center, bottom-left, bottom-right, or top-right. "
        "  DO NOT redraw, re-letter, stylize, recolour, or regenerate the logo — composite "
        "  the supplied PNG verbatim. Do not add an additional wordmark text elsewhere; the "
        "  logo IS the wordmark for this design.\n\n"
        if has_logo
        else "WORDMARK: small wordmark-text in one corner (40–80px equivalent, 50–70% "
        f"opacity): \"{wordmark}\"\n\n"
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
        f"  (b) a feeling/mood line derived FROM THIS SPECIFIC DISH (use the SUPPORT LINE as raw material — e.g. if support says \"Black salt rim. Cucumber crown. Cool and dangerous.\" a valid mood line is \"Cool and dangerous.\").\n"
        f"  (c) a personality line DERIVED FROM the specific dish + the brand's voice signature (see VOICE SEED in the brand stem). Do NOT reuse example lines from OTHER brands' voice seeds — generate fresh copy that ONLY makes sense for THIS dish at THIS restaurant.\n"
        f"  Default heavily to (a). Use (b) or (c) only when the line adds real personality and still identifies the dish. If using (b)/(c), subject name may appear as small subhead or be omitted.\n"
        f"SUPPORT LINE (quote exactly when used as body copy): \"{support}\"\n"
        f"FOOTER LINE — render this EXACT text at the bottom margin as a single low-key hairline-ruled line (NEVER print the word \"CTA\" or \"ADDRESS\" literally on the image — those are labels for you, not content): \"{address_cta}\"\n"
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

    client = genai.Client(api_key=API_KEY)

    # Build prompts for each variation
    jobs = []
    for i in range(args.count):
        angle = VARIATION_ANGLES[i % len(VARIATION_ANGLES)]
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
        jobs.append((i + 1, angle, prompt_text))

    # Log all prompts
    with prompts_log.open("w") as fh:
        for idx, angle, text in jobs:
            fh.write(json.dumps({
                "variation": idx,
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

    print(f"[model] primary={IMAGE_MODEL}  fallback={IMAGE_MODEL_FALLBACK}")
    print(f"[run] {args.brand} / {args.post_id} / {args.format} / {aspect_ratio} / stem={stem_key} / count={args.count} / parallel={args.parallel}")

    start = time.time()

    def worker(job):
        idx, angle, text = job
        print(f"[gen {idx:>2}] start — {angle[:60]}...")
        png, used_model = generate_with_retry(
            client, text, aspect_ratio, ref_bytes, logo_bytes=logo_bytes,
        )
        if not png:
            print(f"[gen {idx:>2}] ✗ failed all models")
            return idx, None
        out_path = out_dir / f"variation_{idx}.png"
        out_path.write_bytes(png)
        print(f"[gen {idx:>2}] ✓ {out_path.name} ({len(png)/1024:.0f} KB) via {used_model}")
        return idx, out_path

    with cf.ThreadPoolExecutor(max_workers=args.parallel) as executor:
        list(executor.map(worker, jobs))

    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f}s. Review: open {out_dir}")


if __name__ == "__main__":
    main()
