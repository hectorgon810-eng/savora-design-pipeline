# Blue Mezcal · Post Playbook
Layer 2 templates · Pair with `SAVORA_POST_SYSTEM.md` and Blue Mezcal tokens from `BRAND_GUIDELINES.md`.
Version 1 · 2026-04-20

---

## Brand token quick-reference

Paste this as **Block 1** in every Claude Design prompt.

```json
{
  "brand": "Blue Mezcal",
  "handle": "@bluemezcalrestaurant",
  "address": "826 Kohl Ave, Middletown, DE 19709",
  "cta": "Visit us | link in bio 📍",
  "colours": {
    "azure":      "#2FA9D8",
    "deep_navy":  "#184B66",
    "warm_cream": "#F6F1E7",
    "chili_red":  "#C1272D"
  },
  "fonts": {
    "display": "Smokum",
    "body":    "DM Sans",
    "accent":  "Permanent Marker",
    "ui":      "Inter"
  },
  "logo": "Blue Mezcal primary — azure 'BLUE' + cream-outline 'MEZCAL' + navy jimador. Position bottom-center, height 120px, 8% opacity white scrim underneath.",
  "rules": ["no pure black", "no pure white", "no centred body copy", "never more than two fonts on one asset"]
}
```

---

## Template index

| # | Category | Template name | Primary use |
|---|---|---|---|
| A1 | Product / Menu | **Block-Headline Hero** | Any dish or drink post (Tue/Thu graphic) |
| B1 | Recurring Weekly | **Day-of-Week Anchor** | Margarita Monday, Taco Tuesday, etc. |
| C1 | Holiday / Seasonal | **Seasonal Card** | Cinco de Mayo, Día de los Muertos |
| D1 | Events | **Date Announcement** | New menu launch, live music, pop-up |
| E1 | Operational | **Plain Notice** | Closed, hours change, reservation reminder |
| F1 | Evergreen CTA | **Location Ping** | Come visit us |

---

# A1 · Block-Headline Hero

**Category:** A — Product / Menu
**When to use:** Tue or Thu graphic post that remixes a food/drink photo already posted on the prior Mon or Fri.

### Visual spec
- Background: the photo at full bleed, slightly desaturated (-10 saturation) so type reads.
- Headline in a small **warm-cream (#F6F1E7) block** tucked into a corner — not full-width. Block height ≈ 180px, width fits text + 40px padding.
- Inside the block: dish name in Smokum 44pt, deep-navy (#184B66), left-aligned.
- One-line support underneath the block in DM Sans Medium 22pt, warm-cream with navy drop-shadow (8px, 40% opacity).
- Logo bottom-center, 120px tall.
- No callouts, no arrows, no ingredient labels. This is the "Casa Azul octopus" restraint level.

### Layout skeleton (1080 × 1350)

```
┌────────────────────────────────────────┐
│ [full-bleed photo of dish, -10 sat]    │
│                                        │
│                                        │
│   ┌──────────────────────┐             │
│   │  HOMBRE              │             │
│   │  Old Fashioned.      │   ← cream   │
│   └──────────────────────┘     block   │
│   Branded ice cube. Bourbon underneath.│
│                                        │
│                                        │
│              [ Blue Mezcal logo ]      │
└────────────────────────────────────────┘
```

### Content brief (the only thing that changes per post)

- Dish/drink name: `HOMBRE Old Fashioned`
- Support line (≤ 8 words): `Branded ice cube. Bourbon underneath.`
- Photo: `https://res.cloudinary.com/dkp42tunc/image/upload/v1776182456/B-35_<id>.jpg`

### Paste-ready Claude Design prompt

```
Design a 4:5 (1080×1350) Instagram feed post for Blue Mezcal.

[BLOCK 1 — tokens from blue-mezcal-playbook.md]

[BLOCK 2 — Template A1 · Block-Headline Hero]
- Full-bleed photo background (dish or drink), -10 saturation
- Warm-cream #F6F1E7 block tucked into lower-left, ~180px tall, width = text + 40px padding
- Inside block: "HOMBRE Old Fashioned." in Smokum 44pt deep-navy #184B66, left-aligned, two lines if needed
- Directly under the block: "Branded ice cube. Bourbon underneath." in DM Sans Medium 22pt warm-cream with subtle navy drop-shadow
- Logo bottom-center, 120px tall
- No arrows, no labels, no extra type

[BLOCK 3 — brief]
- Subject: HOMBRE Old Fashioned
- Photo: use Cloudinary URL supplied
- CTA: "826 Kohl Ave · Middletown · Visit us · link in bio"

Deliver: one 1080×1350 composition.
```

---

# B1 · Day-of-Week Anchor

**Category:** B — Recurring Weekly
**When to use:** Standing weekly posts. Same template every week, only date + cocktail rotates.

### Visual spec
- Background: deep-navy (#184B66) with a soft azure radial glow in the upper-right (10% opacity).
- **Top half:** the day-of-week wordmark in Smokum 96pt azure, left-aligned, single word dominant (e.g. "MONDAYS."). Sub-head in DM Sans Medium 22pt warm-cream directly under.
- **Bottom half:** the week's cocktail photo in a soft-edged oval mask, 60% of width, centred.
- Logo bottom-right, 100px tall.
- Chili-red only appears if the week's drink is a heat drink.

### Layout skeleton

```
┌────────────────────────────────────────┐
│  MARGARITA                             │
│  MONDAYS.        ← Smokum azure 96pt   │
│                                        │
│  This week: Cucumber.                  │
│                                        │
│        ┌─────────────────┐             │
│        │   [drink photo] │             │
│        │   oval-masked   │             │
│        └─────────────────┘             │
│                                        │
│  826 Kohl Ave · Middletown       LOGO  │
└────────────────────────────────────────┘
```

### Content brief

- Day wordmark: `MARGARITA MONDAYS.`
- This week's drink: `Cucumber.`
- Photo: single drink cutout on neutral background
- Heat drink? (yes / no): `no`

### Paste-ready Claude Design prompt

```
Design a 4:5 Instagram post for Blue Mezcal — weekly recurring template.

[BLOCK 1 tokens]

[BLOCK 2 · Template B1]
- Background: deep-navy #184B66 with soft azure radial glow top-right (10% opacity)
- Top half: "MARGARITA / MONDAYS." Smokum 96pt azure #2FA9D8, left-aligned
- Sub-head: "This week: Cucumber." DM Sans Medium 22pt warm-cream
- Bottom half: oval-masked drink photo, 60% width, centred
- Logo bottom-right, 100px
- No chili red (not a heat drink)
- Footer: "826 Kohl Ave · Middletown" DM Sans Regular 16pt warm-cream 70% opacity bottom-left

Deliver 1080×1350. Then same composition at 9:16 for Story.
```

### Rotation plan
- Week 1: Cucumber Margarita
- Week 2: Spicy Margarita (red accent turns on)
- Week 3: Millionaire Margarita (gold override — see note in style guide)
- Week 4: Frozen BAD HOMBRE tray

---

# C1 · Seasonal Card

**Category:** C — Holiday / Seasonal
**When to use:** Cinco de Mayo, Día de los Muertos, Valentine's, St. Paddy's, Mother's Day, NYE.

### Visual spec
- Background: warm-cream (#F6F1E7) — seasonal cards flip the brand canvas to cream so they stand out in the grid without screaming.
- **Headline** in Smokum 72pt deep-navy, stacked two lines, left-aligned.
- **Date** in DM Sans Bold 28pt chili-red (this is one of the only times red appears).
- Small line-drawing motif in azure (e.g. agave for Cinco, marigold for Día de los Muertos) sitting bottom-right at 40% opacity.
- Logo bottom-left, 100px.

### Layout skeleton

```
┌────────────────────────────────────────┐
│  CINCO                                 │
│  DE MAYO.      ← Smokum navy 72pt      │
│                                        │
│  Tuesday, May 5.    ← DM Sans red 28pt │
│                                        │
│  Margaritas all night.                 │
│  Come early.                           │
│                                        │
│                        ╱\__  ← agave   │
│  LOGO                 ╱    \  sketch   │
└────────────────────────────────────────┘
```

### Content brief

- Occasion: `CINCO DE MAYO.`
- Date: `Tuesday, May 5.`
- Message (≤ 10 words): `Margaritas all night. Come early.`
- Motif: `agave line-drawing, bottom-right, 40% opacity azure`

### Paste-ready Claude Design prompt

```
Design a 4:5 post for Blue Mezcal — Cinco de Mayo seasonal card.

[BLOCK 1 tokens]

[BLOCK 2 · Template C1]
- Background: warm-cream #F6F1E7
- Headline "CINCO / DE MAYO." Smokum 72pt deep-navy #184B66, stacked two lines, left-aligned, 48px from left
- Date "Tuesday, May 5." DM Sans Bold 28pt chili-red #C1272D, below headline
- Message "Margaritas all night. / Come early." DM Sans Regular 22pt deep-navy, two lines
- Agave line-drawing in azure #2FA9D8 at 40% opacity, bottom-right corner, 280px tall
- Logo bottom-left, 100px
- No photo on this template

Deliver 1080×1350 + 9:16 Story variant.
```

---

# D1 · Date Announcement

**Category:** D — Events
**When to use:** New menu launches (May 5 launch is coming), live music, pop-ups, collabs.

### Visual spec
- Background: photo of the dish/scene at full bleed, darkened 30% (0 0 0 / 30% overlay) so type reads.
- **Date banner** in a thin cream horizontal strip across the middle (height 80px). Inside: "MAY 5 · 2026" in DM Sans Bold 32pt deep-navy, tracked wide.
- **Headline** above the banner: two-line Smokum 56pt warm-cream.
- **Support** below the banner: one line DM Sans Medium 22pt warm-cream.
- Logo bottom-center, 100px.

### Layout skeleton

```
┌────────────────────────────────────────┐
│ [photo, -30% bed]                      │
│                                        │
│  New Menu.      ← Smokum cream 56pt    │
│  Here.                                 │
│                                        │
│ ━━━ MAY 5 · 2026 ━━━  ← cream band     │
│                                        │
│  Oysters. Parrillada. Tacos.           │
│  Come hungry.                          │
│                                        │
│               [ LOGO ]                 │
└────────────────────────────────────────┘
```

### Content brief

- Headline (2 lines): `New Menu. / Here.`
- Date banner: `MAY 5 · 2026`
- Support (≤ 12 words): `Oysters. Parrillada. Tacos. Come hungry.`
- Photo: B-72 (full-table launch spread)

### Paste-ready Claude Design prompt

```
Design a 4:5 post for Blue Mezcal — event announcement (new menu launch).

[BLOCK 1 tokens]

[BLOCK 2 · Template D1]
- Full-bleed photo (use B-72 launch spread Cloudinary URL), with 30% black overlay for legibility
- Headline "New Menu. / Here." Smokum 56pt warm-cream, stacked, left-aligned upper-third
- Horizontal cream band mid-canvas, 80px tall, full-width less 48px margin — inside: "MAY 5 · 2026" DM Sans Bold 32pt deep-navy, tracked +0.15em, centred in band
- Support "Oysters. Parrillada. Tacos. / Come hungry." DM Sans Medium 22pt warm-cream, below band, left-aligned
- Logo bottom-center, 100px

Deliver 1080×1350 + 9:16 Story variant.
```

---

# E1 · Plain Notice

**Category:** E — Operational
**When to use:** Closed today, early close, hours change, reservation reminders, gift cards, hiring.

### Visual spec
- Background: deep-navy (#184B66). Flat. No photo.
- **Notice headline** in Smokum 80pt warm-cream, left-aligned, stacked to fit.
- **Body** in DM Sans Regular 22pt warm-cream 80% opacity, up to 3 lines.
- Tiny agave line-sketch azure 30% opacity bottom-right at 200px tall — ties the category back to the brand without making the notice feel promotional.
- Logo bottom-left.

### Layout skeleton

```
┌────────────────────────────────────────┐
│  CLOSED         ← Smokum cream 80pt    │
│  TODAY.                                │
│                                        │
│  Reopening tomorrow at 4pm.            │
│  Thanks for your patience.             │
│                                        │
│                                        │
│                                ╱\__    │
│  LOGO                         ╱    \   │
└────────────────────────────────────────┘
```

### Content brief

- Notice: `CLOSED / TODAY.`
- Reason / detail (≤ 18 words): `Reopening tomorrow at 4pm. Thanks for your patience.`

### Paste-ready Claude Design prompt

```
Design a 4:5 post for Blue Mezcal — operational notice (closed today).

[BLOCK 1 tokens]

[BLOCK 2 · Template E1]
- Background: deep-navy #184B66 flat (no photo, no gradient)
- Headline "CLOSED / TODAY." Smokum 80pt warm-cream, stacked, left-aligned, 48px from left, starting at y=200px
- Body "Reopening tomorrow at 4pm. / Thanks for your patience." DM Sans Regular 22pt warm-cream at 80% opacity, two lines, under headline
- Agave line-sketch azure at 30% opacity, bottom-right, 200px tall
- Logo bottom-left, 100px

Deliver 1080×1350 + 9:16 Story variant.
```

---

# F1 · Location Ping (Evergreen CTA)

**Category:** F — Evergreen CTA
**When to use:** Gap filler. When nothing else is scheduled and the feed needs rhythm.

### Visual spec
- Background: azure (#2FA9D8) flat. This is the one template where azure is the full canvas — makes it visually different from product posts so the feed breathes.
- **Call-out** in Smokum 88pt deep-navy, three lines max: "We / pour / mezcal." (or similar brand-voice riff).
- **Address band** horizontal cream strip at bottom-third: `826 Kohl Ave · Middletown, DE`
- **CTA** below band: `Visit us · link in bio` DM Sans Medium 22pt deep-navy.
- Logo top-right, 80px.

### Layout skeleton

```
┌────────────────────────────────────────┐
│                              [LOGO]    │
│                                        │
│  We                                    │
│  pour        ← Smokum navy 88pt        │
│  mezcal.                               │
│                                        │
│                                        │
│ ━━ 826 Kohl Ave · Middletown, DE ━━    │
│                                        │
│  Visit us · link in bio                │
└────────────────────────────────────────┘
```

### Content brief

- Call-out (3 lines max): `We / pour / mezcal.`
- Address: `826 Kohl Ave · Middletown, DE`

### Paste-ready Claude Design prompt

```
Design a 4:5 post for Blue Mezcal — evergreen location ping.

[BLOCK 1 tokens]

[BLOCK 2 · Template F1]
- Background: azure #2FA9D8 flat
- Call-out "We / pour / mezcal." Smokum 88pt deep-navy, stacked three lines, left-aligned upper-half
- Horizontal cream band bottom-third, 80px tall, full-width less 48px margin, contains "826 Kohl Ave · Middletown, DE" DM Sans Bold 26pt deep-navy tracked +0.1em, centred
- Below band: "Visit us · link in bio" DM Sans Medium 22pt deep-navy, left-aligned
- Logo top-right, 80px

Deliver 1080×1350 only (no Story variant — this template is feed-only).
```

---

## Category → Template quick-map

| Need to post… | Use this template | Notes |
|---|---|---|
| Tue/Thu dish remix | A1 Block-Headline Hero | Reuses Mon/Fri photo |
| Margarita Monday / Taco Tuesday | B1 Day-of-Week Anchor | Rotate drink, keep template |
| Cinco de Mayo | C1 Seasonal Card | Cream flip, dated |
| May 5 menu launch | D1 Date Announcement | Photo bed, cream date band |
| Closed for private event | E1 Plain Notice | Flat navy, no photo |
| Gap-filler / "we're here" | F1 Location Ping | Azure flat, feed-only |

---

## What's NOT in this pilot

- A2 Ingredient Callout (the La Bamba-style labeled post) — held; user direction is "simpler, not avant-garde"
- A3 Full-Menu Reveal (grid of dishes) — held for second pass
- B2 Brunch Weekend anchor — held; add if/when brunch becomes a BM service
- C2 Día de los Muertos specific — variant of C1, add on calendar approach
- D2 Live Music night — variant of D1
- E2 Gift Cards — variant of E1
- F2 Rehoboth vs Delaware (Azteca-only) — lives in Azteca playbook

These are added to the playbook after the pilot templates are validated in a real post.

---

*End of Blue Mezcal playbook. Jackson House and El Azteca playbooks follow the same six-template structure with brand-specific tokens.*
