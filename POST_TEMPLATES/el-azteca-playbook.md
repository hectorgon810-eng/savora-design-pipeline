# El Azteca · Post Playbook
Layer 2 templates · Pair with `SAVORA_POST_SYSTEM.md` and El Azteca tokens from `BRAND_PROFILES/el_azteca.md`.
Version 1 · 2026-04-21

---

## Brand token quick-reference

Paste this as **Block 1** in every Claude Design prompt.

```json
{
  "brand": "El Azteca",
  "handles": ["@aztecadelaware", "@aztecarestaurantrehoboth"],
  "locations": ["859 N. DuPont Hwy, Dover, DE 19901", "20672 Coastal Highway, Rehoboth Beach, DE 19971"],
  "cta": "Find your nearest location | link in bio 📍",
  "colours": {
    "azteca_red":     "#D9262B",
    "sunstone_gold":  "#F5C518",
    "warrior_blue":   "#1B4D8F",
    "chili_green":    "#3F7E39",
    "obsidian_black": "#0A0A0A"
  },
  "fonts": {
    "display":     "Cinzel",
    "display_alt": "Trajan Pro",
    "body":        "Work Sans",
    "accent":      "Ceviche One",
    "ui":          "Inter"
  },
  "logo": "El Azteca full-colour warrior + sunstone on black box. Position bottom-center or top-left, height 120px, never recoloured.",
  "rules": ["default to obsidian-black canvas", "one dominant colour + one accent per layout", "never all four colours at equal weight", "no red-on-green type (vibrates)", "lean into step-fret and sunstone motifs at 1–2pt weight"]
}
```

---

## Template index

| # | Category | Template name | Primary use |
|---|---|---|---|
| A1 | Product / Menu | **Sunstone Hero** | Any dish or drink post (Tue/Thu graphic) |
| B1 | Recurring Weekly | **Día de la Semana** | Taco Tuesday, Margarita Monday (shared with BM) |
| C1 | Holiday / Seasonal | **Heritage Card** | Día de los Muertos, Cinco de Mayo, Mexican Independence, Guadalupe |
| D1 | Events | **Family-Table Announcement** | Special dinners, anniversary, live mariachi |
| E1 | Operational | **Plain Notice** | Closed, hours change, reservation reminder |
| F1 | Evergreen CTA | **Two-Location Ping** | Gap-filler pointing to Delaware + Rehoboth |

---

# A1 · Sunstone Hero

**Category:** A — Product / Menu
**When to use:** Tue or Thu graphic that remixes a food/drink photo already posted Mon or Fri.

### Visual spec
- Background: **obsidian black (#0A0A0A)** full bleed.
- Photo full-bleed across top 70% of canvas, darkened slightly along the bottom edge with a 120px gradient to black for type legibility.
- **Sunstone ring motif** in sunstone gold (#F5C518) at 18% opacity, 800px wide, centred behind the photo as a subtle backdrop before the photo loads (visible at photo edges).
- **Dish name** in Cinzel 64pt all-caps Azteca red (#D9262B), left-aligned, 48px from left, starting y=980.
- **Support line** in Work Sans Medium 24pt sunstone gold, left-aligned, 16px below dish name.
- **Step-fret border**: 2px Azteca red step-fret pattern running along the bottom 40px of the canvas, full width.
- Logo bottom-right, 100px tall, above step-fret border.

### Layout skeleton (1080 × 1350)

```
┌────────────────────────────────────────┐
│                                        │
│   [full-bleed photo, sunstone ring     │
│    faintly behind it — top 70%]        │
│                                        │
│                                        │
│   ─── gradient to black ───            │
│                                        │
│  CÓCTEL DE CAMARÓN.                    │
│  ↑ Cinzel 64pt red, caps, left         │
│  Twenty shrimp. Azteca sauce. Avocado. │
│  ↑ Work Sans 24pt gold                 │
│                                        │
│                          [LOGO]        │
│ ━━━━ step-fret red border ━━━━━━━━    │
└────────────────────────────────────────┘
```

### Content brief

- Dish/drink name (Spanish first where natural): `CÓCTEL DE CAMARÓN.`
- Support line (≤ 10 words): `Twenty shrimp. Azteca sauce. Avocado.`
- Photo: `https://res.cloudinary.com/dkp42tunc/image/upload/.../AZ-22_<id>.jpg`

### Paste-ready Claude Design prompt

```
Design a 4:5 (1080×1350) Instagram feed post for El Azteca.

[BLOCK 1 — tokens from el-azteca-playbook.md]

[BLOCK 2 — Template A1 · Sunstone Hero]
- Background: obsidian black #0A0A0A full bleed
- Sunstone ring motif in sunstone gold #F5C518 at 18% opacity, 800px wide, centred behind the photo area
- Photo full-bleed across top 70% of canvas (y=0 to y=945), with 120px vertical gradient to black along the bottom edge
- Dish name "CÓCTEL DE CAMARÓN." in Cinzel 64pt all-caps Azteca red #D9262B, left-aligned, x=48, y=980
- Support line "Twenty shrimp. Azteca sauce. Avocado." in Work Sans Medium 24pt sunstone gold #F5C518, left-aligned, x=48, y=1060
- 2px step-fret border in Azteca red along bottom 40px of canvas, full width
- Logo bottom-right, 100px tall, above step-fret border

[BLOCK 3 — brief]
- Subject: Cóctel de Camarón
- Photo: use Cloudinary URL supplied

Deliver: one 1080×1350 composition.
```

---

# B1 · Día de la Semana

**Category:** B — Recurring Weekly
**When to use:** Taco Tuesday, Margarita Monday, Thirsty Thursday. Same template, rotating day + feature.

### Visual spec
- Background: **Azteca red (#D9262B)** — the one template where red is the full canvas.
- **Top half:** day wordmark in Cinzel all-caps 104pt obsidian black, left-aligned, single dominant word (e.g. "MARTES."). Sub-head in Work Sans Medium 24pt sunstone gold directly under.
- **Bottom half:** oval-masked photo of this week's feature, 60% width, centred, 4px sunstone gold border ring.
- **Small step-fret accent** in sunstone gold at 40% opacity, bottom-right corner, 200px wide.
- Logo bottom-center, 100px.

### Content brief

- Day wordmark (Spanish-first): `MARTES.`
- Sub-head: `Taco Tuesday. 2-for-1 birria.`
- Photo: taco / birria cutout on neutral background

### Paste-ready Claude Design prompt

```
Design a 4:5 El Azteca weekly recurring post.

[BLOCK 1 tokens]

[BLOCK 2 · Template B1 · Día de la Semana]
- Background: Azteca red #D9262B flat
- Top wordmark "MARTES." in Cinzel all-caps 104pt obsidian black #0A0A0A, left-aligned, 48px from left, y=180
- Sub-head "Taco Tuesday. 2-for-1 birria." in Work Sans Medium 24pt sunstone gold #F5C518, left-aligned, 24px below wordmark
- Oval-masked photo of feature, 60% width, centred at y=760, 4px sunstone gold border ring
- Step-fret accent in sunstone gold at 40% opacity, 200px wide, bottom-right corner
- Logo bottom-center, 100px

Deliver 1080×1350 + 9:16 Story variant.
```

---

# C1 · Heritage Card

**Category:** C — Holiday / Seasonal
**When to use:** Día de los Muertos, Cinco de Mayo, Mexican Independence (Sep 16), Hispanic Heritage Month, Our Lady of Guadalupe (Dec 12).

### Visual spec
- Background: **obsidian black (#0A0A0A)**. The four-colour palette appears only in one decorative motif, never across the whole layout.
- **Motif** (top 40%): a large heritage illustration — marigold for Día de los Muertos, agave for Cinco, warrior silhouette for Independence — rendered as line art in the dominant-for-this-holiday colour at 90% opacity.
- **Headline** stacked two lines in Cinzel 80pt all-caps, colour is the dominant-for-this-holiday (red for Cinco, sunstone for Independence, warrior blue for Guadalupe), centred.
- **Date** in Work Sans Bold 28pt parchment-like off-white (#EFE7D4) centred below headline.
- **Message** (one or two lines) in Work Sans Regular 22pt sunstone gold centred.
- Logo bottom-center, 100px.

### Content brief (example: Día de los Muertos)

- Motif: `marigold line-art, sunstone gold, top 40% of canvas`
- Headline (2 lines): `DÍA DE LOS / MUERTOS.`
- Date: `November 1–2.`
- Message: `Altares, memorias, y buena comida.`

### Paste-ready Claude Design prompt

```
Design a 4:5 El Azteca Día de los Muertos heritage card.

[BLOCK 1 tokens]

[BLOCK 2 · Template C1 · Heritage Card]
- Background: obsidian black #0A0A0A full bleed
- Marigold flower illustration in sunstone gold #F5C518 line art at 90% opacity, 900px wide, centred horizontally, top 40% of canvas
- Headline "DÍA DE LOS / MUERTOS." in Cinzel 80pt all-caps sunstone gold #F5C518, stacked two lines, centred, y=650
- Date "November 1–2." in Work Sans Bold 28pt off-white #EFE7D4, centred, 32px below headline
- Message "Altares, memorias, y buena comida." in Work Sans Regular 22pt sunstone gold #F5C518, centred, 32px below date
- Logo bottom-center, 100px

Deliver 1080×1350 + 9:16 Story variant.
```

**Holiday → dominant colour map**
| Holiday | Motif | Dominant colour |
|---|---|---|
| Cinco de Mayo | Agave line-art | Azteca red |
| Mexican Independence (Sep 16) | Eagle-and-serpent silhouette | Sunstone gold |
| Hispanic Heritage (Sep 15 – Oct 15) | Step-fret band | Azteca red |
| Día de los Muertos (Nov 1–2) | Marigold | Sunstone gold |
| Guadalupe (Dec 12) | Rose wreath | Warrior blue |

---

# D1 · Family-Table Announcement

**Category:** D — Events
**When to use:** Special dinners, anniversary, live mariachi, new combo launches.

### Visual spec
- Background: photo of the dish/scene full bleed, darkened 35% (black overlay).
- **Date banner** horizontal sunstone gold strip across the middle (height 88px, full-width less 48px margin). Inside: date in Cinzel 34pt all-caps obsidian black, tracked +0.15em.
- **Headline** above band: two-line Cinzel 58pt all-caps sunstone gold.
- **Support** below band: one or two lines Work Sans Medium 22pt off-white (#EFE7D4).
- Logo bottom-center, 100px.

### Content brief

- Headline (2 lines): `LIVE / MARIACHI.`
- Date banner: `SATURDAY · JUNE 13 · 7PM`
- Support: `Dover location. / Reservations recommended.`

### Paste-ready Claude Design prompt

```
Design a 4:5 El Azteca event announcement (live mariachi).

[BLOCK 1 tokens]

[BLOCK 2 · Template D1 · Family-Table Announcement]
- Full-bleed photo of a live-music / dinner scene with 35% black overlay for legibility
- Headline "LIVE / MARIACHI." in Cinzel 58pt all-caps sunstone gold #F5C518, stacked two lines, left-aligned, upper third, 48px from left
- Horizontal sunstone-gold band mid-canvas at y=700, 88px tall, full-width less 48px margin
  - Inside: "SATURDAY · JUNE 13 · 7PM" in Cinzel all-caps 34pt obsidian black #0A0A0A, tracked +0.15em, centred in band
- Support "Dover location. / Reservations recommended." in Work Sans Medium 22pt off-white #EFE7D4, two lines, left-aligned, 48px below band
- Logo bottom-center, 100px

Deliver 1080×1350 + 9:16 Story variant.
```

---

# E1 · Plain Notice

**Category:** E — Operational
**When to use:** Closed, hours change, reservation reminders, gift cards, hiring.

### Visual spec
- Background: **warrior blue (#1B4D8F)** flat. No photo.
- **Headline** in Cinzel 92pt all-caps sunstone gold, left-aligned, stacked.
- **Body** in Work Sans Regular 22pt off-white #EFE7D4 at 85% opacity, up to 3 lines.
- **Step-fret accent** in sunstone gold at 30% opacity, 240px wide, bottom-right.
- Logo bottom-left, 100px.

### Content brief

- Notice (2 lines): `CERRADO / HOY.`
- Body: `Reabrimos mañana a las 11am. / Thank you for your patience.`

### Paste-ready Claude Design prompt

```
Design a 4:5 El Azteca operational notice.

[BLOCK 1 tokens]

[BLOCK 2 · Template E1 · Plain Notice]
- Background: warrior blue #1B4D8F flat (no photo)
- Headline "CERRADO / HOY." in Cinzel all-caps 92pt sunstone gold #F5C518, stacked two lines, left-aligned, 48px from left, y=220
- Body "Reabrimos mañana a las 11am. / Thank you for your patience." in Work Sans Regular 22pt off-white #EFE7D4 at 85% opacity, two lines, left-aligned, below headline
- Step-fret accent in sunstone gold at 30% opacity, 240px wide, bottom-right
- Logo bottom-left, 100px

Deliver 1080×1350 + 9:16 Story variant.
```

---

# F1 · Two-Location Ping (Evergreen CTA)

**Category:** F — Evergreen CTA
**When to use:** Gap-filler pointing followers to both locations.

### Visual spec
- Background: **obsidian black (#0A0A0A)** full bleed.
- **Big call-out** in Cinzel all-caps 88pt Azteca red, three lines max: "DOS / LOCATIONS. / UNA FAMILIA."
- **Two address blocks** side-by-side in Work Sans Medium 18pt off-white:
  - Left: "DOVER / 859 N. DuPont Hwy"
  - Right: "REHOBOTH / 20672 Coastal Hwy"
  - Separated by a vertical 2px sunstone gold rule.
- **CTA** below: "Find your nearest location · link in bio" in Work Sans Medium 20pt sunstone gold, centred.
- Logo top-center, 80px.

### Content brief

- Call-out (3 lines): `DOS / LOCATIONS. / UNA FAMILIA.`
- Two addresses as above.

### Paste-ready Claude Design prompt

```
Design a 4:5 El Azteca evergreen two-location post.

[BLOCK 1 tokens]

[BLOCK 2 · Template F1 · Two-Location Ping]
- Background: obsidian black #0A0A0A full bleed
- Small logo top-center, 80px, y=120
- Call-out "DOS / LOCATIONS. / UNA FAMILIA." in Cinzel all-caps 88pt Azteca red #D9262B, stacked three lines, centred, y=260
- Two address blocks side-by-side at y=900, centred horizontally, separated by a 2px vertical sunstone gold #F5C518 rule 80px tall:
  - Left block: "DOVER" in Cinzel 22pt sunstone gold + "859 N. DuPont Hwy" in Work Sans 18pt off-white #EFE7D4
  - Right block: "REHOBOTH" in Cinzel 22pt sunstone gold + "20672 Coastal Hwy" in Work Sans 18pt off-white
- CTA "Find your nearest location · link in bio" in Work Sans Medium 20pt sunstone gold, centred, 60px below address blocks

Deliver 1080×1350 only (feed-only template).
```

---

## Category → Template quick-map

| Need to post… | Use this template | Notes |
|---|---|---|
| Tue/Thu dish remix | A1 Sunstone Hero | Reuses Mon/Fri photo |
| Margarita Monday / Taco Tuesday | B1 Día de la Semana | Spanish-first day wordmark |
| Día de los Muertos / Cinco / Independence | C1 Heritage Card | Dominant-colour motif per holiday |
| Live mariachi / special dinner | D1 Family-Table Announcement | Photo bed, gold date band |
| Closed / hours change | E1 Plain Notice | Warrior-blue flat |
| Gap-filler / two locations | F1 Two-Location Ping | Black flat, side-by-side address |

---

*End of El Azteca playbook. For brand foundation see `BRAND_PROFILES/el_azteca.md`; for cohesion rules see `SAVORA_POST_SYSTEM.md`.*
