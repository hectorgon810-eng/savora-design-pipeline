#!/bin/bash
# BM-W-01 reroll — 4 angles × 2 backends = 8 images
# Cucumber Margarita · B-3 · playful stem
set -euo pipefail
cd "$(dirname "$0")/.."

PY="python3 scripts/nano_banana_runner.py"
COMMON="--brand blue_mezcal --format hero_dish_editorial --stem blue_mezcal_playful --image-key B-3 --subject Cucumber_Margarita --support Black_salt_rim._Cucumber_crown._Cool_and_dangerous. --count 2 --parallel 2 --backend both --aspect 4:5"

# NOTE: subject/support use underscores instead of spaces in the bash var above because of shell splitting —
# we pass the real strings directly in each call below.

SUB="Cucumber Margarita"
SUPP="Black salt rim. Cucumber crown. Cool and dangerous."

# Angle A — Frenchette cut-out on cream
$PY --brand blue_mezcal --format hero_dish_editorial --stem blue_mezcal_playful \
  --image-key B-3 --subject "$SUB" --support "$SUPP" --count 2 --parallel 2 --backend both --aspect 4:5 \
  --post-id BM-W-01-r2-A \
  --angle "FRENCHETTE CUT-OUT ON CREAM. Warm bone-cream ground (#F3ECD8) with 8-10% tonal paper gradient. Cocktail glass silhouetted as a clean cut-out, centered in the lower 55-60% of canvas. Top 35%: MIXED-WEIGHT LOCKUP in cobalt #1E3A8A — one word in italic/script ('Cucumber' in Canela Italic or Farnham Italic at 90-110px), one word in refined serif caps ('MARGARITA' in GT Sectra at 1.4x scale). Hairline cobalt rule under the lockup. Small-caps Söhne support line in cobalt below ('BLACK SALT RIM · CUCUMBER CROWN'). Bottom hairline rule + tiny dateline. 3-5% linen paper-grain noise overlay on the cream. NO ornament additions. One-color-ink discipline: everything in cobalt, no marigold, no chile-red, no green." \
  || echo "A FAILED"

# Angle B — Chomp City oversized type wraps drink
$PY --brand blue_mezcal --format hero_dish_editorial --stem blue_mezcal_playful \
  --image-key B-3 --subject "$SUB" --support "$SUPP" --count 2 --parallel 2 --backend both --aspect 4:5 \
  --post-id BM-W-01-r2-B \
  --angle "OVERSIZED TYPE WRAPS THE PHOTO · Chomp City move. Bone-cream ground (#F3ECD8) 5-10% tonal gradient. Oversized cobalt #1E3A8A GT Sectra or Canela italic caps — the single word 'CUCUMBER' filling the top 55% of canvas at ~240-320px, tight tracking (-15 to -25em), letters touching or slightly overlapping the photo edge. The drink photograph sits in the lower 50% of canvas, interacting with the letterforms (the cucumber garnish peeks OVER the baseline of 'CUCUMBER'; the glass rises up into or behind the letters). Below the photo: smaller italic script word 'Margarita.' in cobalt at 70-90px. Small-caps Söhne support line below that. Bottom hairline rule + tiny dateline. This is the bold, young-energy version of BM. No ornaments. No additional fields." \
  || echo "B FAILED"

# Angle C — Dramatic close-crop on rim + salt
$PY --brand blue_mezcal --format hero_dish_editorial --stem blue_mezcal_playful \
  --image-key B-3 --subject "$SUB" --support "$SUPP" --count 2 --parallel 2 --backend both --aspect 4:5 \
  --post-id BM-W-01-r2-C \
  --angle "DRAMATIC CLOSE-CROP ON RIM + GARNISH. The composition is an extreme macro crop of the drink — the black-salt rim fills the lower-left third, the cucumber crown dominates the center-right, beads of condensation on the glass visible. The photograph fills 65-70% of canvas, cropped tight. Negative space in the top-right 30% carries a short poetic line in cobalt italic Canela at 80-100px: 'Cool and dangerous.' — italic, one line, right-aligned with the canvas edge. Tiny small-caps Söhne subhead below in cobalt: 'CUCUMBER MARGARITA'. Hairline cobalt rule at the bottom + tiny venue dateline. The negative-space zone is bone-cream #F3ECD8 with 5% tonal gradient. Editorial. Moody. The drink IS the hero, the type is restrained poetry." \
  || echo "C FAILED"

# Angle D — Vertical cobalt strip + photo 70%
$PY --brand blue_mezcal --format hero_dish_editorial --stem blue_mezcal_playful \
  --image-key B-3 --subject "$SUB" --support "$SUPP" --count 2 --parallel 2 --backend both --aspect 4:5 \
  --post-id BM-W-01-r2-D \
  --angle "VERTICAL COBALT STRIP. Photo fills the RIGHT 70% of canvas at full scale. LEFT 30% is a solid cobalt (#1E3A8A) field with 8-12% tonal gradient (darker at bottom, catches light at top). In the strip: GT Sectra italic caps stacked vertically in warm cream (#F3ECD8) at ~100-130px, fits strip width without clipping — 'CUCUMBER' on top, 'MARGARITA' below, italic line-break. Below headline in small-caps Söhne cream: 'BLACK SALT RIM · CUCUMBER CROWN · COOL AND DANGEROUS' tracked wide across 2-3 lines. At the bottom of the strip: hairline cream rule + tiny address. 3-5% noise-grain on cobalt field. No marigold. No hand-drawn ornament. This is the clean, confident BM standard layout." \
  || echo "D FAILED"

# Build combined 4×2 grid
python3 <<'PY'
from PIL import Image, ImageDraw, ImageFont
import pathlib
root = pathlib.Path('/Users/dreamartstudio/Desktop/restaurant-design-pipeline/OUTPUT/nano_banana/blue_mezcal')
pngs = []
for angle in ['A','B','C','D']:
    d = root / f'BM-W-01-r2-{angle}'
    for fn in ['variation_G1.png','variation_O2.png']:
        p = d / fn
        if p.exists():
            pngs.append((angle, fn, p))
if not pngs:
    print('No outputs'); exit()
im0 = Image.open(pngs[0][2])
w,h = im0.size
scale = 320/w
nw,nh = int(w*scale), int(h*scale)
# Layout: 4 cols (A/B/C/D) × 2 rows (G on top, O bottom)
grid = Image.new('RGB',(nw*4, nh*2),'white')
d = ImageDraw.Draw(grid)
try: font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 28)
except: font = ImageFont.load_default()
for angle, fn, p in pngs:
    col = ord(angle) - ord('A')  # A=0, B=1, C=2, D=3
    row = 0 if 'G' in fn else 1
    im = Image.open(p).convert('RGB').resize((nw,nh), Image.LANCZOS)
    x,y = col*nw, row*nh
    grid.paste(im, (x,y))
    label = f"{angle}-{'G' if 'G' in fn else 'O'}"
    d.text((x+10, y+10), label, fill='yellow', font=font, stroke_width=2, stroke_fill='black')
out = root / 'BM-W-01-r2-COMBINED_GRID.jpg'
grid.save(out, quality=90)
print(f'Combined grid: {out}')
PY

echo ""
echo "=========================================================="
echo "BM-W-01 REROLL COMPLETE · 4 angles × 2 backends = 8 images"
echo "Combined grid: OUTPUT/nano_banana/blue_mezcal/BM-W-01-r2-COMBINED_GRID.jpg"
echo "=========================================================="
