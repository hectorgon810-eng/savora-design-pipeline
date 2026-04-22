#!/bin/bash
# BM Week Test — 10 posts, 10 different content types, 1 Gemini + 1 OpenAI each.
# Tests the Blue Mezcal brand world doc against real generation.
# Run from pipeline root.

set -euo pipefail
cd "$(dirname "$0")/.."

PY="python3 scripts/nano_banana_runner.py"
COMMON="--brand blue_mezcal --count 2 --parallel 2 --backend both"

# ============================================================
# POST 01 — Cocktail Spotlight · Playful-daylight register
# Ghia two-field split, photo-led palette complement (cucumber=cool → marigold/chile accent)
# ============================================================
$PY $COMMON \
  --post-id BM-W-01 \
  --format hero_dish_editorial \
  --stem blue_mezcal_playful \
  --image-key B-3 \
  --subject "Cucumber Margarita" \
  --support "Black salt rim. Cucumber crown. Cool and dangerous." \
  --aspect 4:5 \
  --angle "GHIA CLEAN-GROUND ELEGANCE · playful daylight register. Cream ground (#F3ECD8) divided vertically into two fields. Photo on the RIGHT 55% at full scale, pure bone-cream field on the LEFT 45%. Left field carries a refined GT Sectra or Canela italic caps lockup of the drink name (subject) at 120-160px, cobalt #1E3A8A ink, tight tracking. Small-caps Söhne body-copy line in cobalt below the headline. Optional single hand-drawn cucumber-wedge cross-section silhouette, 40px, cobalt hairline. NO ornament overload. Headline uses COPY OPTION (a) — drink name verbatim. 5% tonal gradient on the left cream field (lighter top-right, slightly darker bottom-left). 3-5% paper-grain noise overlay on the cream field." \
  || echo "POST 01 FAILED"

# ============================================================
# POST 02 — Cocktail Spotlight · Nocturnal register
# Frenchette cut-out hero on charred black + brass foil script+serif lockup
# ============================================================
$PY $COMMON \
  --post-id BM-W-02 \
  --format cocktail_spotlight_moody \
  --stem blue_mezcal_nocturnal \
  --image-key B-7 \
  --subject "Spicy Margarita" \
  --support "Smoke, citrus, slow." \
  --aspect 4:5 \
  --angle "FRENCHETTE CUT-OUT HERO + SCRIPT-SERIF LOCKUP · nocturnal register. Charred-black ground (#0B0B0B) with a deep 10% tonal gradient (slightly warmer toward center). Cocktail glass silhouetted as a clean cut-out centered in the lower 55% of the canvas, rim-lit with brass-amber specular. Top 30% carries a MIXED-WEIGHT typographic lockup: one word in cursive/italic script ('A Little'), one word in serif caps at 1.5x ('SPICY'), at brass-gradient foil (#C9A24B→#B08937→#C9A24B 3-stop). Hairline brass rule under the lockup. Small-caps support line beneath in warm-white (#EDE4D3). No burgundy fields. No additional ornaments." \
  || echo "POST 02 FAILED"

# ============================================================
# POST 03 — Hero Dish Editorial · Playful daylight
# Vertical color-block strip (cobalt, left 30%) + photo right 70%
# ============================================================
$PY $COMMON \
  --post-id BM-W-03 \
  --format hero_dish_editorial \
  --stem blue_mezcal_playful \
  --image-key B-44 \
  --subject "Raw Oysters" \
  --support "Cucumber mignonette. Seaweed salt." \
  --aspect 4:5 \
  --angle "VERTICAL COBALT STRIP · playful daylight. Photo fills the RIGHT 70% of the canvas at full scale. LEFT 30% is a solid cobalt (#1E3A8A) field with 5-10% tonal gradient (darker at bottom). Headline in the strip stacks vertically in warm cream (#F3ECD8) GT Sectra italic caps at ~110-140px (fits the strip width without clipping). Subject name verbatim. Below: small-caps Söhne support line in marigold (#F2A900) accent, one line. At the bottom of the strip: small hairline rule + tiny cream address/CTA line. 3-5% noise grain overlay on the cobalt strip. No hand-drawn ornament needed." \
  || echo "POST 03 FAILED"

# ============================================================
# POST 04 — Ingredient Anatomy · Labeled diagram (Cruffin hairline arrows)
# Isolated hero on cobalt ground + italic-serif labels with hairline curved arrows
# ============================================================
$PY $COMMON \
  --post-id BM-W-04 \
  --format ingredient_anatomy \
  --stem blue_mezcal_editorial \
  --image-key B-62 \
  --subject "Guacamole con Chicharrón" \
  --support "Avocado · Chicharrón · Lime · Salsa Macha" \
  --aspect 4:5 \
  --angle "CRUFFIN LABELED DIAGRAM · isolated hero on saturated cobalt ground. Cobalt field (#1E3A8A) full canvas with 8-12% tonal gradient (darker at corners, slightly lighter toward center — studio-spotlight feel). Hero photo centered, no cropping violence. 3-4 italic-serif labels in warm cream positioned in the negative space around the dish — each label is 2-3 words max (e.g. 'Salsa Macha', 'Lime', 'Chicharrón', 'Avocado'). Each label connects to the specific visible ingredient in the photo via a thin 1-2px hairline CURVED arrow in warm cream. Labels use GT Sectra italic at 28-36px, not huge. Arrows arc gently, never sharp angles. Top-right small-caps dateline: 'BM · Ingredient Anatomy'. Bottom hairline rule + venue address. NO hand-drawn marker arrows (that's Azteca). These are refined editorial hairlines only." \
  || echo "POST 04 FAILED"

# ============================================================
# POST 05 — Typography-First · Spanish dicho
# Oversized italic serif, single-color field, NO photo
# ============================================================
$PY $COMMON \
  --post-id BM-W-05 \
  --format quote_post \
  --stem blue_mezcal_editorial \
  --subject "Para todo mal, mezcal;" \
  --support "para todo bien, también." \
  --aspect 4:5 \
  --angle "TYPOGRAPHY-FIRST DICHO · no photo, type IS the image. Warm bone-cream ground (#F3ECD8) with 8-12% tonal paper-gradient (slightly darker bottom-right, lighter top-left — like aged paper catching light). Oversized GT Sectra or Canela italic serif headline in cobalt (#1E3A8A), breaking across 2-3 lines at 160-220px: 'Para todo mal,' / 'mezcal;' — occupies top 55% of canvas. Below, smaller italic line in the same serif, lighter weight, 90-110px: 'para todo bien, también.' — occupies middle 20%. Bottom 15%: small-caps Söhne dateline in cobalt at 26-30px: 'BLUE MEZCAL · MIDDLETOWN DE' — tracked wide. Hairline rule above the dateline. 3-5% linen paper-grain noise overlay. NO photo, NO ornament. Type IS the hero. Italic flourish on the semicolon." \
  || echo "POST 05 FAILED"

# ============================================================
# POST 06 — Promo / Event Flyer · Mezcal Monday
# Full poster treatment, masthead + illustration + info lockup
# ============================================================
$PY $COMMON \
  --post-id BM-W-06 \
  --format event_announcement \
  --stem blue_mezcal_nocturnal \
  --subject "Mezcal Monday" \
  --support "Half-off flights · 5–8pm · Espadín · Tobalá · Cuishe" \
  --aspect 4:5 \
  --angle "POSTER-LEVEL EVENT FLYER · nocturnal register. Charred black ground (#0B0B0B) with 8% tonal gradient. Top 25%: masthead 'MEZCAL MONDAY' in brass-foil-gradient serif caps (Farnham or Caponi, 140-180px, tight tracking), single horizontal line. Middle 50%: large illustrated editorial drawing in brass-hairline ink — a single agave plant OR three mezcal copitas in a row, OR a hand pouring into a copita — choose the cleanest. The illustration is LINE-ART etched-style, NOT photo, rendered in warm brass #C9A24B. Bottom 25%: small-caps info lockup in warm white (#EDE4D3): 'HALF-OFF FLIGHTS' on one line, '5 — 8 PM' on a second, tiny italic line 'Espadín · Tobalá · Cuishe' on a third. Brass hairline rules separating sections. Small venue tag at bottom edge. 5-8% paper-grain on the black field." \
  || echo "POST 06 FAILED"

# ============================================================
# POST 07 — Location/Map · Vector hand-drawn (cobalt ink on cream)
# Middletown DE, BM as landmark, agave-pin signature
# ============================================================
$PY $COMMON \
  --post-id BM-W-07 \
  --format event_announcement \
  --stem blue_mezcal_editorial \
  --subject "Find us." \
  --support "826 Kohl Ave · Middletown, DE" \
  --aspect 4:5 \
  --angle "HAND-DRAWN VECTOR MAP · cobalt ink on bone-cream ground. Warm bone-cream (#F3ECD8) full canvas with 5-8% tonal gradient. The canvas is an illustrated map of Middletown, DE drawn entirely in cobalt (#1E3A8A) hairline ink — 1-2px strokes, hand-drawn feel, not digital-precise. Streets drawn as thin parallel lines, labeled in tiny italic serif. Small cobalt-hairline silhouettes of neighborhood landmarks (church, town hall, Appoquinimink River). BLUE MEZCAL marked as a prominent location with a small hand-drawn AGAVE PLANT icon (silhouette, cobalt ink) sitting at the exact street address. Script annotation in cobalt italic script near the BM location: 'You are here.' — with a small hairline pointer arrow. Top of canvas: small-caps 'BLUE MEZCAL · 826 KOHL AVE' in cobalt. Bottom: small compass rose + scale bar + tiny italic 'Middletown, Delaware'. 3-5% linen-paper-grain noise overlay. NO photography, NO color fills, NO digital polish — this should read like an illustrated editorial map from a travel zine." \
  || echo "POST 07 FAILED"

# ============================================================
# POST 08 — Location/Map · Unreal-engine cinematic render
# 3D cartoon render of Middletown with BM as glowing landmark
# ============================================================
$PY $COMMON \
  --post-id BM-W-08 \
  --format event_announcement \
  --stem blue_mezcal_editorial \
  --subject "Find us." \
  --support "826 Kohl Ave · Middletown, DE" \
  --aspect 4:5 \
  --angle "UNREAL-ENGINE CINEMATIC 3D MAP RENDER · stylized cartoon diorama. The canvas shows a 3/4-angle bird's-eye isometric 3D cartoon render of downtown Middletown, Delaware — small stylized buildings, trees, roads, cars, rendered in a Pixar-meets-Monument-Valley art direction. Warm golden-hour lighting, volumetric rays, soft shadows. BLUE MEZCAL is a PROMINENT landmark building rendered at 1.5x scale relative to neighbors, with warm glowing windows (cobalt and marigold interior lighting spilling out), a tiny glowing 'BLUE MEZCAL' brass-foil sign above the door, and a subtle blue-mezcal-colored light plume rising from the building. Surrounding buildings are desaturated slightly to let BM hero. Top of canvas: small-caps 'FIND US' in brass-foil serif (60-80px). Bottom: small-caps '826 KOHL AVE · MIDDLETOWN DE' on hairline rule. Overall palette grounded in bone-cream, cobalt shadows, brass-foil accents. Cinematic, but NOT photorealistic — keep the stylized-cartoon 3D feel. No photography attached — build this entirely as an illustrated 3D render." \
  || echo "POST 08 FAILED"

# ============================================================
# POST 09 — Utility / DoorDash · Designed poster
# "Now On DoorDash" — full editorial treatment, no cheap text
# ============================================================
$PY $COMMON \
  --post-id BM-W-09 \
  --format operational_notice \
  --stem blue_mezcal_playful \
  --image-key B-62 \
  --subject "Now On DoorDash." \
  --support "Yes, even the guac." \
  --aspect 4:5 \
  --angle "UTILITY POSTER · editorial treatment, NEVER plain text. Cobalt (#1E3A8A) field on top 50% of canvas with 10% tonal gradient. Bone-cream (#F3ECD8) field on bottom 50%. On the cobalt half: oversized GT Sectra italic caps in warm cream (#F3ECD8) — 'Now On' on one line, 'DoorDash' on a second line in larger scale — total occupies the cobalt half at 140-180px. On the cream half (below a brass-gradient hairline rule): small-caps Söhne body line in cobalt — 'Yes, even the guac.' italic pull-quote centered. Below it: small-caps dateline 'BLUE MEZCAL · MIDDLETOWN DE' + hairline rule + small CTA line. Optional: tiny marigold accent — a small hand-drawn hairline guacamole bowl icon in marigold hairline ink, 40px, sitting at the edge of the cream half. Photo of guac may be present as a small 25% inset in the bottom-right cream zone — but this is a DESIGN-FIRST post, not photo-dominant." \
  || echo "POST 09 FAILED"

# ============================================================
# POST 10 — New Menu Masthead · Typography-only campaign reveal
# Sweetgreen repeating-text wallpaper variant, in BM register
# ============================================================
$PY $COMMON \
  --post-id BM-W-10 \
  --format typographic_poster \
  --stem blue_mezcal_editorial \
  --subject "New Menu. New Era." \
  --support "May 5 · Blue Mezcal" \
  --aspect 4:5 \
  --angle "BRUTALIST REPEATING-HEADLINE WALLPAPER · typographic campaign reveal, no photo. Bone-cream ground (#F3ECD8). The phrase 'NEW MENU · NEW ERA ·' repeats as a wallpaper pattern across the entire canvas in tight rows, each row offset horizontally by 80-120px, cobalt (#1E3A8A) GT Sectra caps at 90-120px, tight leading (1.05). The repeated phrase creates a dense typographic field — editorial restraint version of Sweetgreen's 'MONDAY BOWL DROP' wallpaper move. In the center of the canvas, a rectangular KNOCKOUT WINDOW (reversed-color inset, bone-cream field over the cobalt wallpaper) at 50% width, 25% height. Inside the window: small-caps 'MAY 5' in cobalt, hairline rule, small italic serif 'Blue Mezcal' pull-quote below. 5-8% paper-grain noise overlay. This is a campaign-teaser reveal — brutalist typographic discipline, no photo, no ornament. Type IS the image." \
  || echo "POST 10 FAILED"

echo ""
echo "=========================================================="
echo "BM WEEK TEST COMPLETE"
echo "Review each at: OUTPUT/nano_banana/blue_mezcal/BM-W-{01..10}/_GRID.jpg"
echo "=========================================================="
