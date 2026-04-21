# Restaurant Design Pipeline
Savora · Blue Mezcal Management Group
Two-track design generator: Nano Banana (Gemini 2.5 Flash Image) + Claude Design HTML.

---

## One-minute tour

- **Brands:** Jackson House · Blue Mezcal · El Azteca
- **Tracks:** Nano Banana produces 5 PNG variations per post; Claude Design produces 3 HTML variations.
- **Feedback loop:** every batch writes to `TASTE_INTELLIGENCE.md`. Pipeline stays in supervised mode until ≥20 decisions logged per brand (60 total).
- **Source of truth for posts:** `VISTA_SOCIAL_CSVS/{brand}.csv` (already imported to Vista Social).
- **Image URL map:** `cloudinary_urls.json` — 360 images, never construct URLs by hand.

Read `RESTAURANT_DESIGN_INTELLIGENCE.md` first every session.

---

## Setup (one-time)

```bash
cd /Users/dreamartstudio/Desktop/restaurant-design-pipeline

# 1. Create .env (already opened for you — paste key, save, close)
cp .env.example .env
# then edit .env and set GEMINI_API_KEY=...

# 2. Install Python deps
python3 -m pip install google-genai python-dotenv Pillow
```

That's it. No build step. No node. Scripts run directly.

---

## Generate one post (both tracks)

### Track A — Nano Banana (5 PNG variations)

```bash
python3 scripts/nano_banana_runner.py \
  --brand blue_mezcal \
  --post-id BM-A1-001 \
  --template A1 \
  --image-key B-35 \
  --subject "HOMBRE Old Fashioned" \
  --support "Branded ice cube. Bourbon underneath."

# output: OUTPUT/nano_banana/blue_mezcal/BM-A1-001/variation_{1..5}.png
open OUTPUT/nano_banana/blue_mezcal/BM-A1-001/
```

### Track B — Claude Design (3 HTML variations)

```bash
python3 scripts/claude_design_html.py \
  --brand blue_mezcal \
  --post-id BM-A1-001 \
  --template A1 \
  --image-key B-35 \
  --subject "HOMBRE Old Fashioned" \
  --support "Branded ice cube. Bourbon underneath."

# output: OUTPUT/claude_design/blue_mezcal/BM-A1-001/variation_{1..3}.html
open OUTPUT/claude_design/blue_mezcal/BM-A1-001/variation_1.html
```

Each HTML file renders at 1080×1350. Use browser zoom 50% to see full frame.

---

## Directory map

```
restaurant-design-pipeline/
├── RESTAURANT_DESIGN_INTELLIGENCE.md   ← read first
├── TASTE_INTELLIGENCE.md               ← feedback log (grows every batch)
├── README.md                           ← this file
├── BRAND_PROFILES/                     ← per-brand quick reference
│   ├── jackson_house.md
│   ├── blue_mezcal.md
│   └── el_azteca.md
├── POST_TEMPLATES/                     ← templates A1–F1 per brand
│   ├── SAVORA_POST_SYSTEM.md           ← six-category taxonomy
│   ├── SAVORA_CALENDAR.md              ← 2026 holiday calendar
│   ├── jackson-house-playbook.md
│   ├── blue-mezcal-playbook.md
│   └── el-azteca-playbook.md
├── STYLE_GUIDES/                       ← HTML style guides
├── VISTA_SOCIAL_CSVS/                  ← 4 account CSVs (already scheduled)
├── CLIENTS/                            ← per-restaurant active work
│   ├── jackson-house/{briefs,drafts,approved}
│   ├── blue-mezcal/{briefs,drafts,approved}
│   └── el-azteca/{briefs,drafts,approved}
├── OUTPUT/                             ← generator outputs
│   ├── nano_banana/{brand}/{post_id}/
│   └── claude_design/{brand}/{post_id}/
├── scripts/
│   ├── nano_banana_runner.py
│   └── claude_design_html.py
├── cloudinary_urls.json                ← 360 image URL map
├── cloudinary_orientations.json        ← H/V per image
├── docs/                               ← full brand docs + pipeline history
├── .env                                ← GEMINI_API_KEY (gitignored)
├── .env.example
└── .gitignore
```

---

## Feedback loop

After each batch, review variations and log the decision to `TASTE_INTELLIGENCE.md`:

- Which variation won
- Winner attributes (composition, palette, typography)
- Rejection tags for each loser
- **Rule learned** — the portable pattern to bias future batches

Until each brand has ≥20 logged decisions, don't run autonomous batches. The feedback loop *is* the pipeline.

---

## Rules that never bend

- **Never regenerate food.** Nano Banana composites the real Cloudinary image. The photo stays photographically identical; design is built around it.
- **Never use default fonts** (Poppins, Montserrat, Open Sans, Roboto).
- **Never skip feedback logging.** The taste file is the whole point.
- **Never ship without the six cohesion rules** (`SAVORA_POST_SYSTEM.md` §4).

---

## Adding a template or variation

1. Open the brand playbook (`POST_TEMPLATES/{brand}-playbook.md`)
2. Define the template spec (layout skeleton + paste-ready prompt)
3. For HTML track: add a renderer in `scripts/claude_design_html.py` under `RENDERERS`
4. For Nano Banana: no code change needed — the template stem is read from the playbook narrative and the brand tokens dict

---

## Related projects

- Savora website v3 — `~/Desktop/savora/` (locked)
- Savora template demo — `~/Desktop/savora-template-jackson/` (Jackson demo)
- Original CSV build scripts — `~/Desktop/CLAUDE/` (pre-pipeline, migrated here)
- CLL podcast pipeline — `~/Desktop/CLL_PIPELINE/` (separate; API keys file pattern referenced)
