#!/bin/bash
# BM Personality Roll · 6 no-photo posts · 3 gpt-image-2 + 3 Gemini NB Pro · each a different style
set -euo pipefail
cd "$(dirname "$0")/.."
PY="python3 scripts/nano_banana_runner.py"
COMMON="--brand blue_mezcal --format typographic_poster --count 1 --parallel 1 --aspect 4:5"

# --- OPENAI (gpt-image-2) — 3 styles ---

# O1 — Cinematic 3D render interior (unreal-engine bar scene)
$PY $COMMON --backend openai --stem blue_mezcal_nocturnal \
  --post-id BM-W-O1 --subject "Another round?" --support "Cocktail Hour" \
  --angle "CINEMATIC 3D RENDER · INSIDE BLUE MEZCAL AT 11PM. Stylized cinematic unreal-engine / Pixar-quality 3D render (NOT photorealistic) of the INTERIOR of a high-end mezcal bar at night. Foreground: polished dark bar counter (charcoal wood); on it a single mezcal copita catching warm amber candlelight, a lime wedge, a votive flame. Mid-ground: blurred hand of a bartender setting down a second copita, slight motion. Background: back-bar with bottles backlit amber, cobalt-blue tile on the wall (Casa Azul), single Edison pendant. Volumetric light rays through haze. Palette: charred-black ground, amber highlights, cobalt accents, brass hardware. Warm cinematic color-grade, painted-not-plastic. UPPER-THIRD TYPE: 'Another round?' in Canela italic serif at 130-170px, warm-cream #F2EADF, tight tracking. BOTTOM: small-caps tag 'COCKTAIL HOUR · BLUE MEZCAL · MIDDLETOWN DE' at 24-28px with hairline rule above. Wong Kar-wai-via-Pixar mood." || echo "O1 fail"

# O2 — Brutalist dicho wallpaper (repeating type pattern)
$PY $COMMON --backend openai --stem blue_mezcal_editorial \
  --post-id BM-W-O2 --subject "Para todo mal, mezcal." --support "para todo bien, también." \
  --angle "BRUTALIST DICHO WALLPAPER · typographic editorial. Bone-cream ground (#F3ECD8) with 8% paper-gradient. The SPANISH DICHO phrase 'PARA TODO MAL, MEZCAL' repeats as a tight WALLPAPER PATTERN filling the entire canvas — rows stacked vertically, each row offset horizontally by ~90px (zigzag offset), cobalt (#1E3A8A) GT Sectra italic caps at 85-110px, tight leading (1.05). Every-third-row uses slightly LARGER type (1.15x) for rhythm. In the CENTER of canvas, a RECTANGULAR KNOCKOUT WINDOW (reversed-color inset — bone-cream field punching through the cobalt wallpaper) at 65% width, 30% height. INSIDE the window: small italic Canela at 42-50px 'para todo bien,' on one line, italic at the same size 'también.' on a second line, centered. Below those 2 lines, a hairline cobalt rule, then tiny small-caps 'BLUE MEZCAL · MIDDLETOWN DE'. Everything cobalt + cream. 5-8% linen paper-grain noise overlay. NO photo, NO illustration — type IS the image." || echo "O2 fail"

# O3 — Hand-painted brush wordmark (single word as painted hero)
$PY $COMMON --backend openai --stem blue_mezcal_playful \
  --post-id BM-W-O3 --subject "Mezcal." --support "A handshake in a glass." \
  --angle "HAND-PAINTED BRUSH WORDMARK · single word as painterly hero. Warm bone-cream ground (#F3ECD8) with 10-12% paper-gradient. The SINGLE WORD 'MEZCAL.' dominates the canvas at 480-560px, rendered as a HAND-PAINTED BRUSH STROKE in cobalt (#1E3A8A) ink — visible brush texture, bleed edges, a few intentional paint splatters, uneven weight, like a calligrapher's one-shot brush signature. Paint sits on a cream canvas, painted NOT digital. One tiny marigold (#F2A900) paint splatter near the final period. BELOW the wordmark at 40% canvas height: italic Canela in cobalt at 42-50px on one line 'A handshake in a glass.' italic, centered. Hairline cobalt rule below. Bottom dateline in small-caps at 24-28px 'BLUE MEZCAL · 826 KOHL AVE · MIDDLETOWN DE'. NO illustration. NO photo. ONE painted wordmark is the entire design." || echo "O3 fail"

# --- GEMINI (NB Pro) — 3 styles ---

# G1 — Hand-illustrated cocktail card (Pine & Crane painterly)
$PY $COMMON --backend gemini --stem blue_mezcal_playful \
  --post-id BM-W-G1 --subject "Cocteleria." --support "Hecha a mano. Todos los días." \
  --angle "HAND-ILLUSTRATED COCKTAIL CARD · Pine & Crane × Casa Azul painterly register. Warm bone-cream ground (#F3ECD8) with 10-12% paper-gradient. CENTER 60% of canvas: a hand-drawn painterly illustration (gouache + ink-wash feel, visible brush strokes) of THREE mezcal copitas (small ceramic cups) in a slight arc, each holding a different-hued liquid (clear, amber, pale green), a lime wedge between two of them, a smoke curl rising from one, loose hand-drawn agave-leaf silhouettes behind them. All illustration in cobalt (#1E3A8A) ink-outline + marigold (#F2A900) watercolor wash for liquid + agave-green (#4E6B3A) for leaves. TOP: bold GT Sectra italic caps 'COCTELERIA.' in cobalt at 170-210px, tight tracking. BELOW illustration: small-caps italic in cobalt 36-44px broken on 2 lines 'HECHA A MANO. / TODOS LOS DÍAS.' BOTTOM: hairline cobalt rule + small dateline. 5-7% linen paper-grain. Painterly NOT digital. Cobalt + marigold + green ONLY inside illustration." || echo "G1 fail"

# G2 — Painted aerial map / neighborhood vibe
$PY $COMMON --backend gemini --stem blue_mezcal_editorial \
  --post-id BM-W-G2 --subject "Find us." --support "826 Kohl Ave · Middletown, DE" \
  --angle "PAINTED AERIAL MAP · gouache + watercolor travel-poster register. Warm bone-cream ground (#F3ECD8). Full-canvas painted bird's-eye view of downtown Middletown, Delaware rendered in GOUACHE illustration style — streets as thin hand-painted cobalt (#1E3A8A) lines, small buildings as hand-painted cobalt silhouettes with slight ink-bleed, trees as loose marigold (#F2A900) + agave-green (#4E6B3A) brush dabs, river as a meandering pale-cobalt wash. BLUE MEZCAL is a prominent hand-painted marigold-and-cobalt building landmark, slightly larger, with a painted glowing halo around it. Hand-painted script annotation 'You are here.' in cobalt italic pointing at BM location with a hand-drawn arrow. TOP of canvas: small-caps 'BLUE MEZCAL' in cobalt at 60-80px with hairline rule beneath. BOTTOM: small compass rose + scale bar + tiny italic '826 Kohl Ave · Middletown, DE'. 8-10% watercolor-paper texture. Painted illustration NOT clean vector, NOT 3D render — think vintage travel-poster aesthetic." || echo "G2 fail"

# G3 — Etched engraving editorial (Alfred-register brand-voice post)
$PY $COMMON --backend gemini --stem blue_mezcal_editorial \
  --post-id BM-W-G3 --subject "On the slow things." --support "Mezcal is not hurried. Neither are we." \
  --angle "ETCHED ENGRAVING EDITORIAL · brand-voice cultural post, Alfred 'Our Commitment' register. Warm bone-cream ground (#F3ECD8) with 10% paper-gradient. TOP 20%: italic cobalt Canela serif headline 'On the slow things.' at 110-140px, italic, tight tracking, centered. MIDDLE 50%: a HAND-ETCHED / ENGRAVED line-art illustration of a traditional MEZCAL STILL (palenque copper pot still with wooden cover, steam rising) rendered in cobalt (#1E3A8A) hairline ink with crosshatch shading — like a 19th-century engraving OR an Alfred restaurant illustration. Detailed but restrained. BELOW illustration: a SHORT BODY PARAGRAPH in warm cobalt Söhne regular at 30-34px, 3-4 lines, centered: 'Mezcal is not hurried. / The agave takes seven years. / The fire takes three days. / The pour takes a moment. / Everything worth it takes time.' Hairline cobalt rule beneath body. BOTTOM: small-caps dateline 'BLUE MEZCAL · 826 KOHL AVE · MIDDLETOWN DE'. 5-7% linen paper-grain. Single-ink editorial discipline — cobalt only, NO marigold, NO photo." || echo "G3 fail"

# Build 3x2 grid (top row OpenAI, bottom row Gemini)
python3 <<'PY'
from PIL import Image, ImageDraw, ImageFont
import pathlib
root = pathlib.Path('/Users/dreamartstudio/Desktop/restaurant-design-pipeline/OUTPUT/nano_banana/blue_mezcal')
layout = [
    ('O1', 'BM-W-O1', 'OpenAI · Cinematic 3D'),
    ('O2', 'BM-W-O2', 'OpenAI · Dicho wallpaper'),
    ('O3', 'BM-W-O3', 'OpenAI · Brush wordmark'),
    ('G1', 'BM-W-G1', 'Gemini · Illustrated card'),
    ('G2', 'BM-W-G2', 'Gemini · Painted map'),
    ('G3', 'BM-W-G3', 'Gemini · Etched editorial'),
]
pngs = []
for tag, folder, label in layout:
    p = root / folder / 'variation_1.png'
    if p.exists(): pngs.append((tag, label, p))
if not pngs:
    print('none'); exit()
im0 = Image.open(pngs[0][2])
w,h = im0.size
scale = 400/w
nw,nh = int(w*scale), int(h*scale)
grid = Image.new('RGB', (nw*3, nh*2 + 40), 'white')
d = ImageDraw.Draw(grid)
try: font_big = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 32)
except: font_big = ImageFont.load_default()
try: font_sm = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 18)
except: font_sm = ImageFont.load_default()
for i, (tag, label, p) in enumerate(pngs):
    row, col = divmod(i, 3)
    im = Image.open(p).convert('RGB').resize((nw,nh), Image.LANCZOS)
    x, y = col*nw, row*nh
    grid.paste(im, (x,y))
    d.text((x+10, y+10), tag, fill='yellow', font=font_big, stroke_width=3, stroke_fill='black')
    d.text((x+10, y+nh-28), label, fill='white', font=font_sm, stroke_width=2, stroke_fill='black')
out = root/'BM-W-PERS-03-COMBINED.jpg'
grid.save(out, quality=92)
print(f'grid: {out}')
PY

echo ""
echo "=========================================================="
echo "BM PERSONALITY ROLL 03 COMPLETE · 6 styles · 3 OpenAI + 3 Gemini"
echo "Combined: OUTPUT/nano_banana/blue_mezcal/BM-W-PERS-03-COMBINED.jpg"
echo "=========================================================="
