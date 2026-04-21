# Jackson House · Post Playbook
Layer 2 templates · Pair with `SAVORA_POST_SYSTEM.md` and Jackson House tokens from `BRAND_PROFILES/jackson_house.md`.
Version 1 · 2026-04-21

---

## Brand token quick-reference

Paste this as **Block 1** in every Claude Design prompt.

```json
{
  "brand": "Jackson House",
  "handle": "@jacksonhousede",
  "address": "17 Wood St, Middletown, DE 19709",
  "cta": "Reserve your table | link in bio 📍",
  "colours": {
    "antique_gold":    "#C9A24A",
    "ink_black":       "#0F0F0F",
    "parchment_ivory": "#F5EEDE",
    "aged_brass":      "#8B6B2F"
  },
  "fonts": {
    "display":     "Rye",
    "display_alt": "IM Fell English SC",
    "body":        "Playfair Display",
    "accent":      "Cormorant Garamond Italic",
    "ui":          "Inter"
  },
  "logo": "Jackson House ornate gilded cartouche — gold foil on dark or ivory. Position bottom-center or bottom-left, height 120px, never inverted.",
  "rules": ["no pure white", "gold never on pure white", "one display weight per layout", "hairline gold rules only", "ornate motif pulled from logo"]
}
```

---

## Template index

| # | Category | Template name | Primary use |
|---|---|---|---|
| A1 | Product / Menu | **Menu-Card Hero** | Any dish or drink post (Tue/Thu graphic) |
| B1 | Recurring Weekly | **Brunch Anchor** | Sunday brunch feature (if brunch service) |
| C1 | Holiday / Seasonal | **Stamped Card** | St. Patrick's, Thanksgiving, NYE, Mother's/Father's Day |
| D1 | Events | **Award Badge** | Delaware Today Best New 2025, live music, private events |
| E1 | Operational | **Notice Card** | Closed, hours change, reservation reminders |
| F1 | Evergreen CTA | **Reservation Ping** | Gap-filler reservation prompt |

---

# A1 · Menu-Card Hero

**Category:** A — Product / Menu
**When to use:** Tue or Thu graphic that remixes a food/drink photo already posted on the prior Mon or Fri.

### Visual spec
- Background: **parchment ivory (#F5EEDE)** — never pure white, never photo-full-bleed. The photo sits inside a framed window in the upper two-thirds.
- Photo window: 900×900px, centred horizontally, top margin 120px. Hairline gold (#C9A24A) rule 1px inside the window edge, then ornate 4px gold corner-bracket at each corner (pulled from logo cartouche).
- **Dish name** below the photo window in **Rye 56pt ink-black (#0F0F0F)**, centred, single line.
- **Support line** below in **Cormorant Garamond Italic 26pt aged brass (#8B6B2F)**, centred, one line.
- Footer: hairline gold rule (1px, 60% width) → address in Playfair Display 14pt ink-black → "Reserve your table · link in bio" in Playfair Italic 14pt aged brass.
- Logo bottom-center, 100px tall, below footer.

### Layout skeleton (1080 × 1350)

```
┌────────────────────────────────────────┐
│                                        │
│   ╔══════════════════════════════╗     │
│   ║                              ║     │
│   ║      [photo of dish]         ║     │
│   ║                              ║     │
│   ║                              ║     │
│   ╚══════════════════════════════╝     │
│                                        │
│        BURRATA.   ← Rye 56pt black     │
│   Some things don't need  ← Cormorant  │
│       to be complicated.     italic    │
│                                        │
│  ─────────────────────────────────     │
│   17 Wood St · Middletown, DE          │
│   Reserve your table · link in bio     │
│                                        │
│              [ LOGO ]                  │
└────────────────────────────────────────┘
```

### Content brief

- Dish/drink name: `BURRATA.`
- Support line (≤ 10 words): `Some things don't need to be complicated.`
- Photo: `https://res.cloudinary.com/dkp42tunc/image/upload/.../Savora-31_<id>.jpg`

### Paste-ready Claude Design prompt

```
Design a 4:5 (1080×1350) Instagram feed post for Jackson House.

[BLOCK 1 — tokens from jackson-house-playbook.md]

[BLOCK 2 — Template A1 · Menu-Card Hero]
- Background: parchment ivory #F5EEDE, flat (NEVER pure white)
- Photo window: 900×900px centred, top margin 120px, with 1px inner gold rule and 4px ornate gold corner-brackets
- Dish name "BURRATA." in Rye 56pt ink-black #0F0F0F, centred, directly below photo window with 48px gap
- Support line "Some things don't need to be complicated." in Cormorant Garamond Italic 26pt aged brass #8B6B2F, centred, 16px below dish name
- Hairline gold rule (1px, 60% width, centred) 80px below support line
- Address "17 Wood St · Middletown, DE" in Playfair Display 14pt ink-black, centred
- CTA "Reserve your table · link in bio" in Playfair Italic 14pt aged brass, centred
- Logo bottom-center, 100px tall, below CTA

[BLOCK 3 — brief]
- Subject: Burrata
- Photo: use Cloudinary URL supplied

Deliver: one 1080×1350 composition.
```

---

# B1 · Brunch Anchor

**Category:** B — Recurring Weekly
**When to use:** Sunday brunch graphic (if brunch service is running). Same template every week, only featured dish or mocktail rotates.

### Visual spec
- Background: **ink black (#0F0F0F)** — this template flips the brand to black ground so it reads visually distinct from product posts.
- **Top band:** "BRUNCH" wordmark in Rye 92pt antique gold (#C9A24A), letter-spaced +0.05em, centred, top 160px.
- **Sub-head:** "Sundays, 10am–2pm." in Cormorant Garamond Italic 28pt parchment ivory, centred under wordmark.
- **Middle:** oval-masked photo of the featured dish/mocktail, 70% width, centred, soft gold-foil border ring 2px.
- **Bottom:** "This week: [Dish/Mocktail Name]" in Playfair Display SmallCaps 22pt antique gold, centred.
- Logo bottom-center, 100px tall.

### Content brief

- Sub-head: `Sundays, 10am–2pm.`
- This week's feature: `Nada De Mango.`
- Photo: featured brunch item, ideally cutout or neutral background

### Paste-ready Claude Design prompt

```
Design a 4:5 Jackson House brunch anchor post.

[BLOCK 1 tokens]

[BLOCK 2 · Template B1 · Brunch Anchor]
- Background: ink black #0F0F0F flat
- Top wordmark "BRUNCH" in Rye 92pt antique gold #C9A24A, letter-spacing +0.05em, centred, top 160px
- Sub-head "Sundays, 10am–2pm." in Cormorant Garamond Italic 28pt parchment ivory #F5EEDE, centred, 24px below wordmark
- Oval-masked photo of featured brunch item, 70% width, centred, 2px gold-foil border ring
- Bottom line "This week: Nada De Mango." in Playfair Display SmallCaps 22pt antique gold, centred, 60px below photo
- Logo bottom-center, 100px

Deliver 1080×1350 + 9:16 Story variant.
```

---

# C1 · Stamped Card

**Category:** C — Holiday / Seasonal
**When to use:** St. Patrick's, Thanksgiving, NYE, Mother's/Father's Day, July 4th.

### Visual spec
- Background: **parchment ivory (#F5EEDE)**. Subtle paper texture (light grain noise, 5% opacity).
- **Headline** stacked two lines in Rye 76pt ink-black, centred.
- **Date** in IM Fell English SC 32pt aged brass, centred, below headline.
- **One-line tagline** in Cormorant Garamond Italic 24pt aged brass, centred, below date.
- **Wax-seal motif** at bottom-center, 180px wide — a circular gold-foil seal with a simple Jackson House "JH" monogram inside. Looks stamped.
- Logo (small, 80px) at top-center above headline.

### Content brief

- Occasion headline (2 lines): `MOTHER'S / DAY.`
- Date: `Sunday, May 10.`
- Tagline (≤ 10 words): `Reservations open. Flowers on us.`

### Paste-ready Claude Design prompt

```
Design a 4:5 Jackson House Mother's Day card.

[BLOCK 1 tokens]

[BLOCK 2 · Template C1 · Stamped Card]
- Background: parchment ivory #F5EEDE with subtle paper grain noise at 5% opacity
- Small logo top-center, 80px, 200px from top
- Headline "MOTHER'S / DAY." in Rye 76pt ink-black #0F0F0F, stacked two lines, centred
- Date "Sunday, May 10." in IM Fell English SC 32pt aged brass #8B6B2F, centred, 40px below headline
- Tagline "Reservations open. Flowers on us." in Cormorant Garamond Italic 24pt aged brass, centred, 24px below date
- Wax-seal motif: circular antique-gold #C9A24A seal 180px wide, centred bottom, with "JH" monogram in IM Fell English 28pt ink-black inside
- No photo

Deliver 1080×1350 + 9:16 Story variant.
```

---

# D1 · Award Badge

**Category:** D — Events
**When to use:** Delaware Today Best New Restaurant 2025 callouts (anniversary, press, referrals), live music announcements, private-event hires.

### Visual spec
- Background: **ink black (#0F0F0F)**, full bleed.
- **Badge**: circular gold-foil seal 480px wide, centred vertically, with "DELAWARE TODAY" arched top in Cormorant SmallCaps 18pt ink-black, "2025" centred large in Rye 96pt ink-black, "BEST NEW RESTAURANT" arched bottom in Cormorant SmallCaps 18pt ink-black.
- **Pre-headline** above badge: "We were named" in Cormorant Garamond Italic 26pt parchment ivory, centred.
- **Sub-line** below badge: "Thank you, Delaware." in Rye 36pt antique gold, centred.
- Logo bottom-center, 100px tall.

### Content brief (usually stable — this is the award post)

- Pre-headline: `We were named`
- Badge text: `DELAWARE TODAY · 2025 · BEST NEW RESTAURANT`
- Sub-line: `Thank you, Delaware.`

### Paste-ready Claude Design prompt

```
Design a 4:5 Jackson House award-badge post (Delaware Today 2025 Best New).

[BLOCK 1 tokens]

[BLOCK 2 · Template D1 · Award Badge]
- Background: ink black #0F0F0F flat, full bleed
- Pre-headline "We were named" in Cormorant Garamond Italic 26pt parchment ivory #F5EEDE, centred, top third
- Gold-foil seal: circular 480px wide, centred vertically, antique-gold #C9A24A fill
  - Arched top text: "DELAWARE TODAY" in Cormorant SmallCaps 18pt ink-black
  - Centre large: "2025" in Rye 96pt ink-black
  - Arched bottom text: "BEST NEW RESTAURANT" in Cormorant SmallCaps 18pt ink-black
  - Ornate hairline gold border inside the seal edge
- Sub-line "Thank you, Delaware." in Rye 36pt antique gold #C9A24A, centred, 60px below seal
- Logo bottom-center, 100px

Deliver 1080×1350 + 9:16 Story variant.
```

---

# E1 · Notice Card

**Category:** E — Operational
**When to use:** Closed today, early close, hours change, reservation reminders, gift cards.

### Visual spec
- Background: **parchment ivory (#F5EEDE)**. Flat, no texture.
- **Notice headline** in Rye 84pt ink-black, stacked 2 lines, centred.
- **Body** in Playfair Display 22pt ink-black, up to 3 lines, centred below headline with 48px gap.
- **Hairline gold frame** 16px inside the canvas edge — single 1px rule, no corners, just a plain rectangle. Keeps it feeling menu-card even as a plain notice.
- Logo bottom-center, 100px.

### Content brief

- Notice (2 lines): `CLOSED / TODAY.`
- Body (≤ 20 words): `Back tomorrow at 5pm. / Holding your reservation. Thank you.`

### Paste-ready Claude Design prompt

```
Design a 4:5 Jackson House operational notice.

[BLOCK 1 tokens]

[BLOCK 2 · Template E1 · Notice Card]
- Background: parchment ivory #F5EEDE flat, no texture
- Hairline gold #C9A24A frame: 1px rectangle, 16px inside each canvas edge
- Headline "CLOSED / TODAY." in Rye 84pt ink-black #0F0F0F, stacked two lines, centred, starting 280px from top
- Body "Back tomorrow at 5pm. / Holding your reservation. Thank you." in Playfair Display 22pt ink-black, two lines, centred, 48px below headline
- Logo bottom-center, 100px

Deliver 1080×1350 + 9:16 Story variant.
```

---

# F1 · Reservation Ping (Evergreen CTA)

**Category:** F — Evergreen CTA
**When to use:** Gap-filler. Feed needs rhythm and no other scheduled content.

### Visual spec
- Background: **ink black (#0F0F0F)**, full bleed. This is the one template where black is the full canvas — flips visually from A1 so the feed breathes.
- **Big call-out** in Rye 104pt antique gold, stacked three lines: "Come. / Sit. / Stay."
- **Horizontal gold-foil band** mid-canvas, 72px tall, 80% width, centred — contains "17 WOOD ST · MIDDLETOWN, DE" in IM Fell English SC 22pt ink-black, letter-spaced +0.1em.
- **CTA** below band: "Reserve your table · link in bio" in Cormorant Garamond Italic 22pt parchment ivory, centred.
- Logo top-center, 80px.

### Content brief

- Call-out (3 lines): `Come. / Sit. / Stay.`
- Address band: `17 WOOD ST · MIDDLETOWN, DE`

### Paste-ready Claude Design prompt

```
Design a 4:5 Jackson House evergreen reservation post.

[BLOCK 1 tokens]

[BLOCK 2 · Template F1 · Reservation Ping]
- Background: ink black #0F0F0F flat, full bleed
- Small logo top-center, 80px, 140px from top
- Call-out "Come. / Sit. / Stay." in Rye 104pt antique gold #C9A24A, stacked three lines, centred, starting 260px from top
- Horizontal antique-gold band mid-canvas at y=900, 72px tall, 80% width, centred
  - Inside: "17 WOOD ST · MIDDLETOWN, DE" in IM Fell English SC 22pt ink-black, letter-spaced +0.1em, centred
- CTA "Reserve your table · link in bio" in Cormorant Garamond Italic 22pt parchment ivory #F5EEDE, centred, 48px below band

Deliver 1080×1350 only (feed-only template).
```

---

## Category → Template quick-map

| Need to post… | Use this template | Notes |
|---|---|---|
| Tue/Thu dish remix | A1 Menu-Card Hero | Reuses Mon/Fri photo |
| Sunday brunch | B1 Brunch Anchor | Rotate feature dish/mocktail |
| St. Patrick's · Thanksgiving · Mother's Day · NYE | C1 Stamped Card | Ivory flip, dated, wax-seal motif |
| Delaware Today 2025 callout | D1 Award Badge | Black ground, gold seal |
| Closed for private event · Hours change | E1 Notice Card | Ivory, plain, menu-card feel |
| Gap-filler / reservations | F1 Reservation Ping | Black flat, gold band |

---

*End of Jackson House playbook. For brand foundation see `BRAND_PROFILES/jackson_house.md`; for cohesion rules see `SAVORA_POST_SYSTEM.md`.*
