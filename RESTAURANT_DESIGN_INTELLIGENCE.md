# RESTAURANT DESIGN INTELLIGENCE
Savora · Blue Mezcal Management Group pipeline
Owner: Hector Flores — DreamArt Studio / Savora
Version: 1.0 — 2026-04-21

---

## What this file is

The **canonical index** for the Savora restaurant design pipeline. It does not duplicate content — it points to the authoritative source for each layer. If a field appears in two places, the file linked here wins.

Read this first every session. Then open the linked files based on the task.

**Source of truth for the design system:** [`docs/INTELLIGENCE_FILE.md`](docs/INTELLIGENCE_FILE.md) — long-form intelligence briefing (Part I), Claude-to-Claude YAML decision rules (Part II), and 10 worked Nano Banana prompt examples (Part III). Everything in the brand profiles and playbooks derives from this file.

**Reference exemplars (visual targets):** `REFERENCES/_inbox/` (IMG_4099–IMG_4107) — La Bamba Ice Cream (Azteca register target), Casa Azul NYC (Blue Mezcal register target). Studied + seeded into `TASTE_INTELLIGENCE.md` before any generation.

---

## The two-layer model

```
Claude Design prompt  =  [ Brand tokens ]  +  [ Template ]  +  [ Content brief ]
Nano Banana prompt    =  [ Brand register ] + [ Composite rules ] + [ Cloudinary image + copy ]
```

**Layer 1 — Brand tokens (fixed).** Palette · typography · logo · voice · photo treatment.
**Layer 2 — Templates (modular).** The skeleton layouts — one per category.

---

## File map

```
restaurant-design-pipeline/
├── RESTAURANT_DESIGN_INTELLIGENCE.md   ← this file
├── TASTE_INTELLIGENCE.md               ← feedback log (grows every batch)
├── BRAND_PROFILES/
│   ├── jackson_house.md
│   ├── blue_mezcal.md
│   └── el_azteca.md
├── POST_TEMPLATES/
│   ├── SAVORA_POST_SYSTEM.md           ← six-category taxonomy + cohesion rules
│   ├── SAVORA_CALENDAR.md              ← 2026 date-driven calendar
│   ├── jackson-house-playbook.md       ← templates A1–F1
│   ├── blue-mezcal-playbook.md         ← templates A1–F1
│   └── el-azteca-playbook.md           ← templates A1–F1
├── STYLE_GUIDES/                       ← full visual foundations (HTML)
├── VISTA_SOCIAL_CSVS/                  ← 4 account CSVs (already scheduled Apr 17 → Aug)
├── cloudinary_urls.json                ← 360 URL map (never construct URLs by hand)
├── cloudinary_orientations.json        ← H/V per image (enforce carousel consistency)
├── CLIENTS/                            ← per-restaurant active design sub-tasks
│   ├── jackson-house/{briefs,drafts,approved}
│   ├── blue-mezcal/{briefs,drafts,approved}
│   └── el-azteca/{briefs,drafts,approved}
├── OUTPUT/
│   ├── nano_banana/{brand}/{post_id}/
│   └── claude_design/{brand}/{post_id}/
├── scripts/
│   ├── nano_banana_runner.py
│   └── claude_design_html.py
├── docs/
│   ├── BRAND_GUIDELINES.md             ← full per-brand rationale + JSON tokens
│   ├── MASTER_BUILD_FILE_v3.md         ← historical: post-by-post schedule source
│   ├── WORKFLOW_SYSTEM.md              ← CSV build pipeline
│   └── HANDOFF.md                      ← pipeline status as of Apr 17
├── .env                                ← GEMINI_API_KEY (gitignored)
├── .env.example
└── README.md
```

---

## Brand register lock

| Brand | Register | Primary language | Palette anchor | Type anchor |
|---|---|---|---|---|
| **Jackson House** | Heritage-editorial → warm-vernacular. 1890s reissued menu card. | English only | Antique Gold on Parchment Ivory · Ink Black | Rye display + Playfair Display body |
| **Blue Mezcal** | Editorial-modernist → moody-nocturnal. Mezcal-forward saloon. | English-primary, Spanish accents | Azure + Deep Navy + Warm Cream · Chili Red accent | Smokum display + DM Sans body |
| **El Azteca** | Warm-vernacular, heritage-family. Four-colour warrior palette. | Bilingual (ES-first where natural) | Azteca Red + Sunstone Gold + Warrior Blue + Chili Green on Obsidian Black | Cinzel display + Work Sans body |

Detailed tokens: `docs/BRAND_GUIDELINES.md` (JSON block, lines 73–216).
Per-brand summaries: `BRAND_PROFILES/*.md`.
Per-brand templates: `POST_TEMPLATES/{brand}-playbook.md`.

---

## The six cohesion rules (non-negotiable, apply across all three brands)

Pulled from `POST_TEMPLATES/SAVORA_POST_SYSTEM.md`. Every asset passes all six or it goes back.

1. **Type lock** — only fonts from the brand style guide. No system fonts, no substitutes.
2. **Colour lock** — only hex codes from the brand palette. No freehand colour.
3. **Logo lock** — bottom-left, bottom-center, or top-right. Never free-floating. Scale per brand guide.
4. **Grid lock** — 4:5 (1080×1350) feed, 9:16 (1080×1920) Story/Reel. Never square. 48px safe margin.
5. **Voice lock** — brand caption formula only. No marketing-speak ("amazing", "must-try", "foodie").
6. **One-hero rule** — one focal element per post. One dish, one message, one date.

---

## Post category taxonomy (shared across brands)

| # | Category | Covers | Cadence |
|---|---|---|---|
| **A** | Product / Menu | Dish hero · drink hero · ingredient callout · new-menu launch | Mon + Fri photo · Tue + Thu graphic |
| **B** | Recurring Weekly | Margarita Monday · Taco Tuesday · Thirsty Thursday · Brunch | Same slot every week |
| **C** | Holiday / Seasonal | Cinco de Mayo · Día de los Muertos · Mother's Day · NYE | Calendar-triggered |
| **D** | Events | Live music · Menu launch · Pop-up · Collab | Announcement + day-of |
| **E** | Operational | Closed · Hours · Reservation reminder · Gift cards · Hiring | As needed |
| **F** | Evergreen CTA | Visit us · Reserve · Follow us | Gap filler |

If a post doesn't fit one of these six, we don't post it until it does.

Calendar: `POST_TEMPLATES/SAVORA_CALENDAR.md`.

---

## Two parallel tracks

### Track A — Nano Banana (Gemini 2.5 Flash Image)
- Runner: `scripts/nano_banana_runner.py`
- 5 variations per post, saved to `OUTPUT/nano_banana/{brand}/{post_id}/variation_N.png`
- **Composite, do NOT regenerate food.** The Cloudinary photo must stay photographically identical. Design is built *around* it.
- Multi-turn pattern: turn 1 establishes brand template; turn 2 composites the reference image + copy.

### Track B — Claude Design (HTML)
- Generator: `scripts/claude_design_html.py`
- 3 HTML variations per post, saved to `OUTPUT/claude_design/{brand}/{post_id}/variation_N.html`
- Self-contained HTML, Cloudinary URL referenced directly, Google Fonts CDN for type.
- Open in Safari / Chrome for review at 1080×1350.

---

## Post-type selection logic

Before drafting any asset:

1. **Read the CSV.** What's already scheduled for this brand this week? Avoid format repetition within a 7-day window.
   Files: `VISTA_SOCIAL_CSVS/*.csv`
2. **Read the image.** Single dish (A1 hero), multi-component (A2 ingredient anatomy), room/ambiance (F1 reservation), beverage (A1 drink hero), people (BTS).
3. **Check the calendar.** Upcoming holidays? Weekly recurring slot (Taco Tuesday, Margarita Monday)?
   File: `POST_TEMPLATES/SAVORA_CALENDAR.md`
4. **Match format to register.** Blue Mezcal quote posts = editorial italic on cobalt. Azteca quote posts = chunky display on pink/red. Jackson House = serif on ivory.

---

## Feedback loop (the whole point)

After each batch (5 NB variations OR 3 HTML variations), present the feedback UI.

Schema + decision log: `TASTE_INTELLIGENCE.md`.

Every decision writes:
- Post ID · Format · Winner · Winner attributes (composition, palette, typography, texture)
- Rejected variations with reason tags + notes
- **Rule learned** — the portable pattern extracted from the decision

**Autonomous-readiness threshold:** ≥20 decisions per brand (60 total) AND clear patterns in "rule learned" sections. Until then, every batch goes through the feedback UI.

---

## Rules that never bend

- Never regenerate a restaurant's food photography via Nano Banana. Composite the real Cloudinary image.
- Never use default fonts (Poppins, Montserrat, Open Sans, Roboto) for anything.
- Never center-lock composition unless ceremonial (logo moments, wordmark-only posts).
- Never output without checking brand register first.
- Never skip feedback logging — the taste file is the whole point.
- Never assume. If image, format, or copy is ambiguous, ask.

---

## Session start checklist

1. Read this file.
2. Read `TASTE_INTELLIGENCE.md` — note latest rules per brand.
3. Read `VISTA_SOCIAL_CSVS/{brand}.csv` — identify scheduled posts + gaps.
4. Confirm `.env` has `GEMINI_API_KEY`.
5. Confirm `OUTPUT/` folders exist.
6. Ask: which brand + post type first? Or suggest next 3 posts based on CSV gaps + calendar.

---

*End of intelligence index. Do not add implementation detail here. Implementation lives in the linked files — this stays thin.*
