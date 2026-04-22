#!/bin/bash
# BM Personality Roll 04 · 6 fresh branding styles · no scenes, no fake places
set -euo pipefail
cd "$(dirname "$0")/.."
PY="python3 scripts/nano_banana_runner.py"
COMMON="--brand blue_mezcal --format typographic_poster --count 1 --parallel 1 --aspect 4:5 --no-logo"

# --- OPENAI — 3 rendered/typographic styles ---

# O4 — Neon sign nocturnal poster
$PY $COMMON --backend openai --stem blue_mezcal_nocturnal \
  --post-id BM-W-O4 --subject "Open late." --support "Mezcal · Cocteleria · Cocina" \
  --angle "NEON SIGN POSTER · nocturnal brand statement. Pure charred-black ground (#0B0B0B) full-canvas. Centered, the letters 'BLUE MEZCAL' glow as a COBALT NEON SIGN — tube outline in electric cobalt (#1E3A8A) with soft rim-glow, slight cobalt-halo bleed onto the black ground, subtle glass-tube highlight specular on the tube edges. Type at 340-420px, custom neon-cursive feel (like vintage bar signage), two lines 'BLUE' stacked above 'MEZCAL'. Below the neon sign at 65% canvas height: italic Canela serif in warm-cream 'Open late.' at 80-100px, one line, centered. Small-caps Söhne subhead below at 26-30px 'MEZCAL · COCTELERIA · COCINA' tracked wide. Bottom: hairline cobalt rule + tiny cream dateline '826 KOHL AVE · MIDDLETOWN DE'. 4-6% film-grain overlay, subtle radial vignette. NO photo, NO illustration. Single neon element + editorial type on black. Moody." || echo "O4 fail"

# O5 — Circular wax-seal / stamp emblem
$PY $COMMON --backend openai --stem blue_mezcal_editorial \
  --post-id BM-W-O5 --subject "Blue Mezcal" --support "Est. 2024 · Middletown, Delaware" \
  --angle "CIRCULAR BRAND SEAL / STAMP EMBLEM · editorial heraldic register. Warm bone-cream ground (#F3ECD8) with 8% paper-gradient. CENTERED on the canvas: a single LARGE CIRCULAR WAX-SEAL / STAMP EMBLEM occupying ~60% of canvas diameter. The seal is cobalt (#1E3A8A) ink impression on cream paper — looks STAMPED with slight ink-bleed around edges (NOT vector-clean). Inside the circle, concentric rings: OUTER RING carries the text 'BLUE MEZCAL · MIDDLETOWN DELAWARE · AGAVE BAR & KITCHEN ·' rendered as small-caps Söhne in cobalt tracked wide, following the circle perimeter. INNER RING: hand-drawn AGAVE-PLANT silhouette centered (cobalt ink line-art). BELOW the agave, inside the circle, small italic 'Est. 2024'. Hairline cobalt rule above and below the seal ornament — no text outside the circle except a tiny small-caps tag '826 KOHL AVE' at the very bottom. 5-7% linen paper-grain. Single-color cobalt ink only, cream ground. NO photo, NO additional illustration. This is a brand-mark post — the seal IS the brand." || echo "O5 fail"

# O6 — Vintage matchbook cover
$PY $COMMON --backend openai --stem blue_mezcal_nocturnal \
  --post-id BM-W-O6 --subject "Strike Anywhere." --support "Blue Mezcal · Middletown, DE" \
  --angle "VINTAGE MATCHBOOK COVER · brand merch aesthetic. The canvas depicts a CLOSED VINTAGE MATCHBOOK rendered flat at a slight 3° off-axis angle, filling ~75% of canvas center. The matchbook COVER is the hero — cobalt (#1E3A8A) front with warm-cream (#F3ECD8) printed design: a large GT Sectra italic caps 'BLUE MEZCAL' at the top spanning 80% of matchbook width in cream, hand-drawn agave-plant silhouette center-front (cream ink), small-caps '826 KOHL AVE · MIDDLETOWN DE' below. The matchbook's staple visible at top edge, slight paper texture, very subtle wear on corners. The matchbook sits on a warm charcoal/deep-charred tabletop (#1A1612) with a soft ambient shadow beneath. ABOVE the matchbook at upper 15% canvas: italic serif 'Strike Anywhere.' in warm-cream at 70-90px. BELOW at lower 10%: small-caps tag 'TAKE ONE WITH YOU' in warm-cream wide-tracked. 6-8% film grain. Lighting: warm tungsten 3000K from upper-left. NO additional photo. ONE object + editorial framing." || echo "O6 fail"

# --- GEMINI NB PRO — 3 painterly/illustrated styles ---

# G4 — Cut-paper collage (mixed-media)
$PY $COMMON --backend gemini --stem blue_mezcal_playful \
  --post-id BM-W-G4 --subject "Hecho a mano." --support "Blue Mezcal · Cocteleria" \
  --angle "CUT-PAPER COLLAGE · mixed-media brand statement. Warm bone-cream ground (#F3ECD8) with 10% paper-gradient and visible paper-texture (like construction paper). The canvas shows a HAND-CUT PAPER COLLAGE arrangement: overlapping cut-out pieces of colored paper — a cobalt (#1E3A8A) agave leaf cut from construction paper with visible knife edges, a marigold (#F2A900) copita silhouette cut-out, an agave-green (#4E6B3A) lime-wedge cut-out, all arranged in a loose asymmetric composition center-canvas. Each cut-paper piece has a 1-2px visible paper edge, a soft drop-shadow beneath (showing they're layered cut paper), and slight deckled/torn edges on a few pieces. TYPOGRAPHIC SCRAPS: small rectangular strips of newsprint-paper carrying phrases like 'mezcal' and 'blue mezcal' in mixed serif + sans ransom-note feel, pasted into the composition. TOP of canvas: large hand-painted brush caps 'HECHO A MANO.' in cobalt at 140-180px (painted NOT digital). BOTTOM: hairline cobalt rule + 'BLUE MEZCAL · COCTELERIA' small-caps. Painterly, handmade, NOT digital. Pinterest editorial-craft vibe." || echo "G4 fail"

# G5 — Painted mezcal pour (abstract liquid)
$PY $COMMON --backend gemini --stem blue_mezcal_playful \
  --post-id BM-W-G5 --subject "Slow pour." --support "Mezcal · Blue Mezcal" \
  --angle "PAINTED MEZCAL POUR · abstract brand statement. Warm bone-cream ground (#F3ECD8) with 10-12% paper-gradient. The canvas shows a SINGLE GESTURAL BRUSH PAINTING of liquid mezcal being poured — a vertical hand-painted ribbon of golden-amber (#D4A556) watercolor streaming diagonally from upper-right toward lower-left, with soft marigold (#F2A900) highlights at the edges, subtle cobalt (#1E3A8A) shadows where the liquid catches light, and a few deliberate paint splatters around the stream. ABSTRACT — no glass, no bottle, just the liquid itself treated as painted gesture. Brush strokes visible, paint bleed on paper, NOT digital-clean. TOP of canvas at 15% height: italic cobalt Canela serif 'Slow pour.' at 120-150px, one line, centered. BOTTOM: small-caps 'MEZCAL · BLUE MEZCAL · MIDDLETOWN DE' at 30-36px tracked wide, hairline cobalt rule above. 6-8% watercolor-paper texture. Painterly abstract brand mood-post." || echo "G5 fail"

# G6 — Risograph zine poster
$PY $COMMON --backend gemini --stem blue_mezcal_playful \
  --post-id BM-W-G6 --subject "Drink slow." --support "Blue Mezcal · Est. 2024" \
  --angle "RISOGRAPH ZINE POSTER · handcrafted print aesthetic. Warm bone-cream paper ground (#F3ECD8) with strong visible paper texture. Full-canvas single-color RISOGRAPH print in cobalt (#1E3A8A) — characteristic riso qualities: grainy ink, slight misregistration (1-2px channel offset on parts of the design), halftone-dot shading in shadow areas (coarse 30-45° halftone dots), slight uneven ink distribution, a few paper specks. CENTER composition: a large stylized AGAVE PLANT silhouette rendered in riso-cobalt with halftone-dot interior shading (the agave is the hero illustration, takes 55% of canvas). ABOVE the agave: bold GT Sectra italic caps 'DRINK SLOW.' in cobalt riso-print at 180-220px, slight misregistration makes one letter have a faint agave-green (#4E6B3A) offset ghost. BELOW the agave: small-caps 'BLUE MEZCAL · EST 2024 · MIDDLETOWN DE' tracked wide. Hairline cobalt rule at bottom. 8-10% paper-fiber texture. Authentic riso-print feel — like a one-color poster from a zine-collective screen printer." || echo "G6 fail"

# Grid: 3x2 (top=OpenAI, bot=Gemini)
python3 <<'PY'
from PIL import Image, ImageDraw, ImageFont
import pathlib
root = pathlib.Path('/Users/dreamartstudio/Desktop/restaurant-design-pipeline/OUTPUT/nano_banana/blue_mezcal')
layout = [
    ('O4', 'BM-W-O4', 'OpenAI · Neon nocturnal'),
    ('O5', 'BM-W-O5', 'OpenAI · Wax seal'),
    ('O6', 'BM-W-O6', 'OpenAI · Matchbook'),
    ('G4', 'BM-W-G4', 'Gemini · Cut-paper collage'),
    ('G5', 'BM-W-G5', 'Gemini · Painted pour'),
    ('G6', 'BM-W-G6', 'Gemini · Riso zine'),
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
out = root/'BM-W-PERS-04-COMBINED.jpg'
grid.save(out, quality=92)
print(f'grid: {out}')
PY

echo ""
echo "=========================================================="
echo "BM PERSONALITY ROLL 04 COMPLETE · 6 FRESH styles"
echo "Combined: OUTPUT/nano_banana/blue_mezcal/BM-W-PERS-04-COMBINED.jpg"
echo "=========================================================="
