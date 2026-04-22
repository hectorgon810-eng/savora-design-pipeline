#!/bin/bash
# BM Roll 05 · 3 fresh branding + 3 practical post types · no scenes, no fake products
set -euo pipefail
cd "$(dirname "$0")/.."
PY="python3 scripts/nano_banana_runner.py"
COMMON="--brand blue_mezcal --format typographic_poster --count 1 --parallel 1 --aspect 4:5 --no-logo"

# --- OPENAI — typographic-precision register ---

# O7 — Typographic BM monogram stamp
$PY $COMMON --backend openai --stem blue_mezcal_editorial \
  --post-id BM-W-O7 --subject "BM" --support "Blue Mezcal · Middletown, Delaware" \
  --angle "TYPOGRAPHIC MONOGRAM STAMP · brand mark post. Warm bone-cream ground (#F3ECD8) with 8-10% paper-gradient. DEAD CENTER of canvas: an OVERSIZED LETTER LOCKUP of 'BM' (Blue Mezcal monogram) at ~900px height, rendered in cobalt (#1E3A8A) with a layered editorial treatment — the letters are old-style serif display (Farnham Display / Tiempos Headline), the 'B' and 'M' overlap slightly with the M's left stroke passing through the B's right-curve, creating a custom ligature. Slight letterpress-emboss feel (subtle inner-shadow). Around the perimeter of the monogram: a circular HAIRLINE COBALT OUTLINE at ~65% canvas diameter. Following the circle, small-caps Söhne in cobalt tracked wide: 'BLUE MEZCAL · MIDDLETOWN DELAWARE · EST 2024 ·' repeating around. At very top of canvas: tiny italic 'since 2024' centered. At very bottom: hairline cobalt rule + 'AGAVE BAR & KITCHEN' small-caps tracked wide. 5-7% paper-fiber noise. Editorial, heraldic, confident. Cobalt + cream only." || echo "O7 fail"

# O8 — Happy Hour event flyer
$PY $COMMON --backend openai --stem blue_mezcal_nocturnal \
  --post-id BM-W-O8 --subject "Happy Hour" --support "Monday–Thursday · 5–7pm · Half-off flights" \
  --angle "HAPPY HOUR FLYER · editorial poster layout, nocturnal register. Charred-black ground (#0B0B0B) with 8-10% tonal gradient (slightly warmer center). TOP 30%: masthead — 'HAPPY HOUR' in brass-foil gradient serif caps (Farnham, 180-230px), with a subtle specular highlight on the letters, tight tracking, hairline brass rule beneath. MIDDLE 40%: a single hand-drawn cobalt-blue COPITA silhouette (small ceramic mezcal cup) centered, line-art only, with a brass hairline underline. Around the copita, 3 small hand-drawn SMOKE CURLS rising (brass hairline). LOWER 25%: editorial info-lockup in warm-cream (#EDE4D3) small-caps Söhne at 32-38px, stacked: 'MONDAY — THURSDAY' on line 1, '5 — 7 PM' on line 2, 'HALF-OFF MEZCAL FLIGHTS' on line 3, each separated by hairline brass rules. BOTTOM strip: tiny dateline '826 KOHL AVE · MIDDLETOWN DELAWARE' in warm-cream small-caps, wide-tracked. 5-7% film grain overlay. No logo attachment. Brass + charred-black + cream palette only — no cobalt in this one (Nocturnal register override)." || echo "O8 fail"

# O9 — Type-only team masthead editorial
$PY $COMMON --backend openai --stem blue_mezcal_editorial \
  --post-id BM-W-O9 --subject "Behind the bar." --support "The team · Blue Mezcal" \
  --angle "TYPE-ONLY TEAM MASTHEAD · editorial credits page register. Warm bone-cream ground (#F3ECD8) with 10% paper-gradient. Composition resembles a magazine masthead / credits page. TOP 20%: italic cobalt Canela serif 'Behind the bar.' at 130-160px, italic, centered. Hairline cobalt rule beneath. MIDDLE 60%: a typographic CREDITS STACK — set in alternating serif italic + small-caps Söhne lines, cobalt ink, centered, at 32-38px body size. The lines read (each on its own row, alternating italic serif title + small-caps role): 'Selena' (serif italic) / 'HEAD BARTENDER' (small-caps) / hairline rule / 'Marco' (serif italic) / 'CHEF DE CUISINE' (small-caps) / hairline rule / 'Elena' (serif italic) / 'SOMMELIER' (small-caps) / hairline rule / 'The House' (serif italic) / 'HOSPITALITY' (small-caps). Each name-role pair separated by thin cobalt hairline rules. BOTTOM 10%: small italic cobalt 'The ones who pour, plate, and welcome you.' at 28-32px, centered, above a final hairline rule + 'BLUE MEZCAL · 826 KOHL AVE · MIDDLETOWN DE' small-caps tag. Editorial magazine-credits discipline — NO photo, NO illustration, just elegant typographic list. 5-7% paper-grain." || echo "O9 fail"

# --- GEMINI NB PRO — painterly register ---

# G7 — Vertical painted MEZCAL letterform
$PY $COMMON --backend gemini --stem blue_mezcal_playful \
  --post-id BM-W-G7 --subject "Mezcal." --support "Hand-poured · Blue Mezcal" \
  --angle "VERTICAL PAINTED LETTERFORM · bold brand statement. Warm bone-cream ground (#F3ECD8) with 10-12% paper-gradient. The single word 'MEZCAL.' runs VERTICALLY down the canvas, one letter per row, stacked: M / E / Z / C / A / L — each letter at ~240-300px, rendered as a HAND-PAINTED GOUACHE brush-stroke in cobalt (#1E3A8A), visible brush texture, slight color variation per letter (some darker, some lighter cobalt bleeding into each other), a few paint splatters flanking the letters. The final period is a large marigold (#F2A900) paint dot. Right side of canvas: a vertical running italic Canela serif pullquote in cobalt at 44-52px, rotated 90° to read UP the canvas: 'Hand-poured. Slow. Aged seven years.' TOP: tiny small-caps 'BLUE MEZCAL' centered above the painted M. BOTTOM: hairline cobalt rule + 'MIDDLETOWN · DE' small-caps. Painterly NOT digital — visible brush strokes, cream paper texture, a few paint splatters. Editorial-bold brand mood-post." || echo "G7 fail"

# G8 — New drink launch teaser (painted silhouette)
$PY $COMMON --backend gemini --stem blue_mezcal_playful \
  --post-id BM-W-G8 --subject "New." --support "Mezcal Negroni · Friday, May 5" \
  --angle "NEW DRINK LAUNCH TEASER · painted silhouette reveal. Warm bone-cream ground (#F3ECD8) with 12% paper-gradient (darker bottom-right). CENTER of canvas: a SINGLE PAINTED SILHOUETTE of a cocktail glass — a coupe or a rocks glass depending on what reads best — rendered in deep cobalt (#1E3A8A) gouache with visible brush texture, the drink inside painted in a velvet burgundy (#4A1621) wash to suggest a Negroni. Hand-painted smoke curl rises from the top in brass-amber (#C9A24B) wash. Painted silhouette occupies ~55% canvas height, center-right. LEFT UPPER: a marigold (#F2A900) CIRCULAR 'NEW' badge (like a wax-stamp disc) at 150px diameter, white-cream small-caps 'NEW' reversed out. RIGHT UPPER: italic cobalt Canela at 90-110px 'Mezcal Negroni.' as a callout line. BOTTOM: small-caps 'FRIDAY · MAY 5 · LAUNCH NIGHT' at 32-38px in cobalt, hairline rule above. Small dateline 'BLUE MEZCAL · MIDDLETOWN DE'. Painterly NOT digital, 6-8% watercolor-paper texture." || echo "G8 fail"

# G9 — Editorial magazine cover mood
$PY $COMMON --backend gemini --stem blue_mezcal_playful \
  --post-id BM-W-G9 --subject "Blue Mezcal Quarterly" --support "Spring 2026 · Issue Two" \
  --angle "EDITORIAL MAGAZINE COVER · imagined as a quarterly print title. Warm bone-cream ground (#F3ECD8) with 12% paper-gradient. The canvas is designed as the COVER OF A MAGAZINE titled 'BLUE MEZCAL QUARTERLY'. TOP 18%: masthead — bold cobalt GT Sectra caps 'BLUE MEZCAL' at 200-240px tight tracking, below it in smaller cobalt italic serif 'Quarterly' at 90-110px, stacked. Hairline cobalt rule beneath. CENTER 55%: a HAND-PAINTED gouache portrait of a single AGAVE PLANT in cobalt + agave-green (#4E6B3A) + marigold (#F2A900) highlights, loose painterly strokes, centered. Around the agave, 3 small italic cobalt cover-line teasers (like magazine cover lines) scattered asymmetrically: 'The Slow Craft' top-left, 'On Agave Varieties' center-right, 'Selena's Five Favourite Pours' bottom-left, each at 32-40px italic Canela with a small hairline arrow pointing inward toward the agave. LOWER 15%: small-caps 'SPRING 2026 · ISSUE TWO' tracked wide in cobalt, hairline rule beneath, bottom dateline '826 KOHL AVE · MIDDLETOWN DE'. 6-8% linen paper-grain. Editorial magazine discipline, painterly illustration, NOT photographic, NOT vector-clean. A quarterly you'd subscribe to." || echo "G9 fail"

# Grid 3x2
python3 <<'PY'
from PIL import Image, ImageDraw, ImageFont
import pathlib
root = pathlib.Path('/Users/dreamartstudio/Desktop/restaurant-design-pipeline/OUTPUT/nano_banana/blue_mezcal')
layout = [
    ('O7', 'BM-W-O7', 'OpenAI · BM Monogram stamp'),
    ('O8', 'BM-W-O8', 'OpenAI · Happy Hour flyer'),
    ('O9', 'BM-W-O9', 'OpenAI · Team masthead'),
    ('G7', 'BM-W-G7', 'Gemini · Vertical painted MEZCAL'),
    ('G8', 'BM-W-G8', 'Gemini · New drink teaser'),
    ('G9', 'BM-W-G9', 'Gemini · Magazine cover'),
]
pngs = []
for tag, folder, label in layout:
    p = root / folder / 'variation_1.png'
    if p.exists(): pngs.append((tag, label, p))
if not pngs: print('none'); exit()
im0 = Image.open(pngs[0][2])
w,h = im0.size
scale = 400/w
nw,nh = int(w*scale), int(h*scale)
grid = Image.new('RGB', (nw*3, nh*2), 'white')
d = ImageDraw.Draw(grid)
try: fb = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 32)
except: fb = ImageFont.load_default()
try: fs = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 18)
except: fs = ImageFont.load_default()
for i, (tag, label, p) in enumerate(pngs):
    row, col = divmod(i, 3)
    im = Image.open(p).convert('RGB').resize((nw,nh), Image.LANCZOS)
    x, y = col*nw, row*nh
    grid.paste(im, (x,y))
    d.text((x+10, y+10), tag, fill='yellow', font=fb, stroke_width=3, stroke_fill='black')
    d.text((x+10, y+nh-28), label, fill='white', font=fs, stroke_width=2, stroke_fill='black')
out = root/'BM-W-PERS-05-COMBINED.jpg'
grid.save(out, quality=92)
print(f'grid: {out}')
PY

echo ""
echo "=========================================================="
echo "BM ROLL 05 COMPLETE · 6 styles (3 branding + 3 practical)"
echo "Combined: OUTPUT/nano_banana/blue_mezcal/BM-W-PERS-05-COMBINED.jpg"
echo "=========================================================="
