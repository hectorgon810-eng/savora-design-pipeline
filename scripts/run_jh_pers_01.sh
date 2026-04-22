#!/bin/bash
# JH Personality Roll 01 · 6 OpenAI + 2 Gemini (3:1 ratio) · real content only
set -euo pipefail
cd "$(dirname "$0")/.."
PY="python3 scripts/nano_banana_runner.py"
COMMON="--brand jackson_house --count 1 --parallel 1 --aspect 4:5"

# --- OPENAI · 6 styles ---

# JH-O1 — Selena drink-name typography masthead
$PY $COMMON --backend openai --stem jackson_house_tavern --format typographic_poster --no-logo \
  --post-id JH-W-O1 --subject "Heard's The Last Word." --support "(It usually is.)" \
  --angle "DRINK-NAME TYPOGRAPHY MASTHEAD · Selena Series signature lockup. Deep charred-black ground (#0A0A0A) with 10% tonal gradient (warmer center). Full-canvas SCRIPT+SERIF LOCKUP of the drink name: 'Heard's' in italic warm cursive SCRIPT (Farnham Italic / Caslon Italic) at 180-220px warm cream (#F2EADF), 'THE LAST WORD.' in refined serif CAPS (Farnham Display) at 260-320px in BRASS-FOIL GRADIENT (#C9A24B→#B08937→#C9A24B 3-stop) with specular highlight, tight tracking, stacked 2-3 lines, centered-asymmetric. BRASS HAIRLINE RULE beneath the lockup. Small italic Caslon pullquote in warm cream 50-60px '(It usually is.)' centered below. BOTTOM: small-caps 'JACKSON HOUSE · 17 WOOD ST · MIDDLETOWN DE' warm cream 22-26px tracked wide one line. 5-7% film grain, paper-grain under foil type. NO photo. Type is hero." || echo "JH-O1 fail"

# JH-O2 — Hero Dish Editorial · Chimichurri Steak (Ghia split, real photo T-72)
$PY $COMMON --backend openai --stem jackson_house_tavern --format hero_dish_editorial \
  --post-id JH-W-O2 --image-key T-72 --subject "Chimichurri Steak" --support "Chimichurri. Charred rim. Mid-rare." \
  --angle "GHIA CLEAN-GROUND EDITORIAL · heritage-tavern winner. Warm cream ground (#F2EADF) divided vertically: photo RIGHT 55% at full scale, warm-cream field LEFT 45%. Left carries: brass-foil gradient (#C9A24B→#B08937→#C9A24B) serif caps lockup 'CHIMICHURRI / STEAK.' Farnham Display 120-150px stacked 2 lines tight tracking. Beneath: small-caps Trade Gothic Condensed deep charcoal 'CHIMICHURRI · CHARRED RIM · MID-RARE' tracked wide 26-30px. Hairline brass rule + tiny italic Caslon 'Jackson House' 32-36px. BOTTOM LEFT: small-caps 'DELAWARE TODAY 2025 · BEST NEW RESTAURANT' 20-24px tracked wide, hairline rule + '17 WOOD ST · MIDDLETOWN DE'. 5-7% paper-grain on cream. Brass + cream + charcoal only." || echo "JH-O2 fail"

# JH-O3 — Utility DoorDash
$PY $COMMON --backend openai --stem jackson_house_tavern --format operational_notice --no-logo \
  --post-id JH-W-O3 --subject "Now on DoorDash." --support "The whole menu. Delivered." \
  --angle "UTILITY POSTER · heritage-tavern register. Charred-black ground (#0A0A0A) 10% tonal gradient. TOP 55%: 'Now on / DoorDash.' brass-foil gradient serif caps Farnham Display 200-260px stacked 2 lines tight tracking foil+specular. Brass hairline rule beneath. MIDDLE 25%: italic Caslon pullquote warm cream 60-70px 'The whole menu. Delivered.' centered. BOTTOM 20%: small-caps Trade Gothic warm cream 22-26px tracked wide 'JACKSON HOUSE · 17 WOOD ST · MIDDLETOWN DELAWARE' + hairline rule + tiny italic 'Reserve your table · link in bio'. 5-7% film grain. No exclamation points. No emoji." || echo "JH-O3 fail"

# JH-O4 — New drink teaser · Bite The Bulleit (real cocktail, no photo, bold script+serif)
$PY $COMMON --backend openai --stem jackson_house_tavern --format typographic_poster --no-logo \
  --post-id JH-W-O4 --subject "Bite The Bulleit." --support "Bourbon. Bite. Bulleit." \
  --angle "DRAMATIC DRINK-NAME POSTER · Selena Series bold moment. Deep oxblood ground (#5B1A1A) 12% tonal gradient (warmer top, almost-black corners). SCRIPT+SERIF LOCKUP of the name 'Bite The Bulleit.' centered — 'Bite' in italic warm SCRIPT (Farnham Italic) at 180-220px warm cream, 'THE BULLEIT.' in refined serif CAPS (Farnham Display) at 280-340px BRASS-FOIL gradient with subtle specular, stacked 2 lines slight asymmetric tilt, tight tracking. Brass hairline rule beneath. Small italic Caslon pullquote warm cream 50-60px 'Bourbon. Bite. Bulleit.' centered. BOTTOM: small-caps 'JACKSON HOUSE · 17 WOOD ST · MIDDLETOWN DE' warm cream 22-26px tracked wide + hairline rule. 5-7% film grain, paper-grain under foil. NO photo. Heritage-luxe cocktail drop poster." || echo "JH-O4 fail"

# JH-O5 — Wine Dinner event flyer (real event format)
$PY $COMMON --backend openai --stem jackson_house_tavern --format event_announcement --no-logo \
  --post-id JH-W-O5 --subject "Wine Dinner." --support "Five courses. Five wines. One evening." \
  --angle "HERITAGE EVENT POSTER · wine dinner flyer, editorial register. Deep forest-green ground (#1F3B2D) 12% tonal gradient (deeper corners, warmer center). TOP 30%: 'WINE / DINNER.' brass-foil gradient serif caps Farnham Display 220-270px stacked 2 lines tight tracking. Brass hairline rule beneath headline. MIDDLE 40%: a HAND-ETCHED ILLUSTRATION of a single wine glass + a decanter + sprig of rosemary as still-life (engraving register, hairline pen-and-ink) rendered in brass-foil line-art. LOWER 25%: small-caps warm cream info 30-36px 'FIVE COURSES · FIVE WINES · ONE EVENING' tracked wide one line + hairline brass rule + 'JACKSON HOUSE · 17 WOOD ST · MIDDLETOWN DE' small-caps 20-24px + tiny italic 'Reserve · link in bio'. 6-8% film grain. Forest-green + brass + warm cream. NO photo." || echo "JH-O5 fail"

# JH-O6 — Type-only editorial quote (brand voice)
$PY $COMMON --backend openai --stem jackson_house_tavern --format quote_post --no-logo \
  --post-id JH-W-O6 --subject "You already know." --support "Jackson House · Middletown, Delaware" \
  --angle "TYPOGRAPHIC BRAND-VOICE QUOTE POST · no photo, type IS the image. Deep charred-black ground (#0A0A0A) 10% tonal gradient. Centered on canvas: the phrase 'You already know.' in BRASS-FOIL GRADIENT (#C9A24B→#B08937→#C9A24B 3-stop with specular highlight) refined serif caps Farnham Display at 280-340px, tight tracking (-15em), centered. Brass hairline rule beneath at 40% canvas width. BOTTOM: small-caps 'JACKSON HOUSE · DELAWARE TODAY 2025 · BEST NEW RESTAURANT' warm cream 22-26px tracked wide + hairline rule + tiny '17 WOOD ST · MIDDLETOWN DE'. 5-7% film grain, paper-grain under foil type. Single brass-foil statement on black. Confident. Quiet." || echo "JH-O6 fail"

# --- GEMINI NB PRO · 2 painterly styles ---

# JH-G1 — Cocktail Spotlight · Grapefruitty Tuti painted (Selena Series)
$PY $COMMON --backend gemini --stem jackson_house_tavern --format typographic_poster --no-logo \
  --post-id JH-W-G1 --subject "Grapefruitty Tuti." --support "Care free, spirit free." \
  --angle "FRENCHETTE CUT-OUT + SCRIPT-SERIF LOCKUP · Selena Series painted cocktail. Warm cream ground (#F2EADF) 10% paper-gradient. CENTER 50%: HAND-PAINTED GOUACHE cocktail glass silhouette (highball) rendered in rose-pink + grapefruit-amber watercolor wash, grapefruit wedge + strawberry garnish painted on top, loose brush texture, one-color-family discipline. TOP: 'Grapefruitty' italic Caslon warm charcoal (#1A1612) 140-170px, 'TUTI.' serif caps Farnham Display deep charcoal 1.4x stacked 2 lines tight tracking. BELOW painted glass: italic serif pullquote charcoal 50-60px 'Care free, spirit free.' centered. BOTTOM: small-caps charcoal 22-26px 'JACKSON HOUSE · 17 WOOD ST · MIDDLETOWN DE' + hairline rule. 6-8% paper-grain. Painted illustration NOT photo. Cream + charcoal + rose-pink only." || echo "JH-G1 fail"

# JH-G2 — Cultural Alfred-register post
$PY $COMMON --backend gemini --stem jackson_house_tavern --format typographic_poster --no-logo \
  --post-id JH-W-G2 --subject "On patience." --support "Some things are worth the wait." \
  --angle "ETCHED CULTURAL EDITORIAL · Alfred register. Warm cream ground (#F2EADF) 10-12% paper-gradient. TOP 18%: italic warm-charcoal Caslon serif 'On patience.' 130-160px italic centered. MIDDLE 50%: HAND-ETCHED pen-and-ink LINE-ART ILLUSTRATION of a cast-iron skillet with a steak on it (crosshatch shading, engraving register) rendered in deep charcoal hairline. Detailed but restrained. BELOW: SHORT BODY PARAGRAPH warm charcoal Caslon 30-34px 3-4 lines centered: 'A 28-day dry-age. / A four-hour braise. / A reservation made a week ahead. / Some things are worth the wait.' Hairline brass rule beneath body. BOTTOM: small-caps charcoal 22-26px 'JACKSON HOUSE · DELAWARE TODAY 2025 · BEST NEW RESTAURANT' tracked wide + tiny 'MIDDLETOWN DE'. 5-7% linen paper-grain. Single-ink deep charcoal only. NO photo. NO brass foil (this is the cream-ground editorial variant)." || echo "JH-G2 fail"

# Grid 4x2
python3 <<'PY'
from PIL import Image, ImageDraw, ImageFont
import pathlib
root = pathlib.Path('/Users/dreamartstudio/Desktop/restaurant-design-pipeline/OUTPUT/nano_banana/jackson_house')
layout = [
    ('O1', 'JH-W-O1', 'OpenAI · Heard\'s Last Word'),
    ('O2', 'JH-W-O2', 'OpenAI · Chimichurri Ghia'),
    ('O3', 'JH-W-O3', 'OpenAI · DoorDash utility'),
    ('O4', 'JH-W-O4', 'OpenAI · Bite The Bulleit'),
    ('O5', 'JH-W-O5', 'OpenAI · Wine Dinner'),
    ('O6', 'JH-W-O6', 'OpenAI · You already know'),
    ('G1', 'JH-W-G1', 'Gemini · Grapefruitty painted'),
    ('G2', 'JH-W-G2', 'Gemini · Alfred cultural'),
]
pngs = []
for tag, folder, label in layout:
    p = root / folder / 'variation_1.png'
    if p.exists(): pngs.append((tag, label, p))
if not pngs: print('none'); exit()
im0 = Image.open(pngs[0][2])
w,h = im0.size
scale = 380/w
nw,nh = int(w*scale), int(h*scale)
grid = Image.new('RGB', (nw*4, nh*2), 'white')
d = ImageDraw.Draw(grid)
try: fb = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 30)
except: fb = ImageFont.load_default()
try: fs = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 16)
except: fs = ImageFont.load_default()
for i, (tag, label, p) in enumerate(pngs):
    row, col = divmod(i, 4)
    im = Image.open(p).convert('RGB').resize((nw,nh), Image.LANCZOS)
    x, y = col*nw, row*nh
    grid.paste(im, (x,y))
    d.text((x+10, y+10), tag, fill='yellow', font=fb, stroke_width=3, stroke_fill='black')
    d.text((x+10, y+nh-24), label, fill='white', font=fs, stroke_width=2, stroke_fill='black')
out = root/'JH-W-PERS-01-COMBINED.jpg'
grid.save(out, quality=92)
print(f'grid: {out}')
PY

echo ""
echo "=========================================================="
echo "JH ROLL 01 COMPLETE · 6 OpenAI + 2 Gemini (3:1 ratio)"
echo "=========================================================="
