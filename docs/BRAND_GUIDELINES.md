# Savora Brand Guidelines — Jackson House · Blue Mezcal · El Azteca
Built for Claude Design. Paste the JSON block at the top of any design prompt.
Last updated: 2026-04-20

---

## How to use this file in Claude Design

Paste the JSON block below (or the single brand you need) at the top of your prompt, then describe the asset:

> "Use these brand guidelines: `{…paste JSON…}`. Now create a 4:5 Instagram post template for **Jackson House** featuring an **ingredient callout** for Burrata with heirloom tomatoes."

Claude Design will pull colour, type and voice from the JSON and respect the hierarchy rules below.

---

## At-a-glance comparison

| | Jackson House | Blue Mezcal | El Azteca |
|---|---|---|---|
| Handle | @jacksonhousede | @bluemezcalrestaurant | @aztecadelaware / @aztecarestaurantrehoboth |
| Personality | Elevated · Prestige · Refined | Bold · Playful · Crafted | Warm · Family · Vibrant |
| Primary colour | Metallic Gold | Cyan Blue | Azteca Red |
| Mood | Old-world tavern, gilded, low-lit | Western-meets-mezcal, moody blues | Heritage Mexican, festive, hand-made |
| CTA | Reserve your table \| link in bio | Visit us \| link in bio | Find your nearest location \| link in bio |

---

## JACKSON HOUSE — design rules

**Essence.** Delaware Today's 2025 Best New Restaurant. The logo is an ornate gilded cartouche — the whole design system should feel like a reissued 1890s menu card: ivory paper, gold foil, western-serif display, lots of negative space. Prestige without stuffiness.

**Colour reasoning.** Gold carries the "best of" badge energy and matches the foil logo. Deep ink-black anchors the gold so it reads upscale, not flashy. Ivory replaces pure white because pure white makes gold look synthetic; a warm paper tone makes it look stamped.

**Typography reasoning.** The wordmark uses a western-serif stamped letterform — pair it with a classic transitional serif for body so the page reads like a printed menu, not a flyer. Keep sans-serif only for legal/fine-print.

**Do / Don't.**
- Do: let gold sit on ivory or deep ink; use hairline gold rules; anchor every layout with one ornate scrollwork motif borrowed from the logo.
- Don't: stack gold on bright white (cheapens it), use more than one display weight per layout, or add bright secondary colours.

---

## BLUE MEZCAL — design rules

**Essence.** Rebranded Azteca with a sharper point of view — mezcal-forward, slightly rebellious, still family-owned. Logo pairs an azure wordmark with a navy jimador (agave worker). Captions lean confident and short: "Cool and dangerous.", "Zero apologies."

**Colour reasoning.** The two blues (azure highlight + navy base) are the brand's signature contrast — keep that duality in every asset: bright headline on dark ground or vice-versa. A warm cream acts as negative space so it never feels cold/corporate. Chili-red appears only as an accent for spice/heat callouts.

**Typography reasoning.** Wordmark is a distressed slab with a saloon feel — pair it with a clean geometric sans for body so posts stay modern. Reserve the distressed type for product names only; never for long captions.

**Do / Don't.**
- Do: contrast azure and navy on every layout; treat the jimador figure as a recurring mascot/watermark; use tight headline kerning.
- Don't: use all-navy layouts (reads flat), pair with pure black (navy is the deepest tone), or apply distressed display to body text.

---

## EL AZTECA — design rules

**Essence.** The family restaurant that's been feeding the community for decades. The logo is a full-colour Aztec warrior and sunstone on black — heritage, craft, warmth. Captions are punchy and generous ("A little bit of everything, and all of it hits.").

**Colour reasoning.** The four-colour palette (red · gold · blue · green) comes straight off the warrior's headdress and the sunstone — lean into it, don't dilute it. Red is the lead (like the "El Azteca" wordmark); gold/yellow plays the sunstone role for highlights; blue and green anchor large fields so the palette feels cultural, not clown-ish.

**Typography reasoning.** Wordmark reads like carved stone — pair with a contemporary geometric sans for menus so heritage headlines and clean body text coexist. Reserve the carved-stone display for dish names and section headers only.

**Do / Don't.**
- Do: use black as the primary canvas (matches logo box); let one colour dominate per layout with a second as accent; lean into Aztec pattern motifs (sunstone rings, step-fret borders).
- Don't: use all four colours at equal weight in one layout (chaos), put red type on green fills (vibrates), or use white-on-black-only — always warm it with gold.

---

## MACHINE-READABLE BRAND GUIDELINES (paste into Claude Design)

```json
{
  "brand_guidelines": {
    "jackson_house": {
      "name": "Jackson House",
      "handle": "@jacksonhousede",
      "address": "17 Wood St, Middletown, DE 19709",
      "cta": "Reserve your table | link in bio 📍",
      "personality": ["elevated", "prestige", "refined"],
      "one_liner": "Delaware's Best New Restaurant 2025 — reissued 1890s menu card energy: ivory paper, gold foil, old-west serifs.",
      "colours": {
        "primary": "#C9A24A",
        "primary_name": "Antique Gold",
        "secondary": ["#0F0F0F", "#F5EEDE"],
        "secondary_names": ["Ink Black", "Parchment Ivory"],
        "accent": "#8B6B2F",
        "accent_name": "Aged Brass",
        "usage": {
          "primary": "Headlines, logo foil, ornamental rules, dish names. Always on ink or parchment — never on pure white.",
          "ink_black": "Primary background for hero posts and quote overlays. Also used for body type when layout is ivory.",
          "parchment_ivory": "Primary background for menu-card style layouts. Replaces pure white in every context.",
          "aged_brass": "Sub-heads, secondary rules, price chips. Provides a warmer-darker step between gold and black."
        },
        "reasoning": "The logo's gold foil on parchment is the brand. Pure white reads synthetic against the foil; ivory preserves the stamped-menu feel. Black anchors the gold so it reads upscale rather than flashy."
      },
      "typography": {
        "display": "Rye",
        "display_alt": "IM Fell English SC",
        "body": "Playfair Display",
        "accent": "Cormorant Garamond Italic",
        "ui": "Inter",
        "hierarchy": "Display (Rye, 48–96pt, tracked tight): dish/drink names and hero headlines. Body (Playfair Display, 16–20pt): captions, menu copy. Accent (Cormorant Italic): pull-quotes, one-line taglines. UI (Inter, 12pt): fine print, disclaimers only.",
        "reasoning": "Rye echoes the logo's western-serif stamp without copying it. Playfair Display gives menu-card prestige for body text. Cormorant Italic introduces softness for quotes so the brand doesn't feel purely masculine."
      },
      "visual_language": "Ornate cartouche frames pulled from the logo; hairline gold rules separating sections; generous ivory negative space; single-dish hero photography shot warm/low-key; no stock icons; occasional wax-seal or stamp motif.",
      "post_voice": "Confident, warm, understated. One punchy line after the dish name, let the image do the work. Never explain the dish unless it's new.",
      "voice_examples": [
        "Dilly Dally Dirty Martini. 🍸 / You already know.",
        "Burrata. 🍅 / Some things don't need to be complicated.",
        "Cornbread Muffins. 🧈 / Warm out of the oven. Butter melts on contact."
      ],
      "product_categories": ["cocktails", "artisanal mains", "brunch mocktails", "BTS/culture (team, training, bar craft)", "award callouts (Best New Delaware 2025)"]
    },

    "blue_mezcal": {
      "name": "Blue Mezcal",
      "handle": "@bluemezcalrestaurant",
      "address": "826 Kohl Ave, Middletown, DE 19709",
      "cta": "Visit us | link in bio 📍",
      "personality": ["bold", "playful", "crafted"],
      "one_liner": "Rebranded Azteca with an edge — mezcal-forward, slightly rebellious, still family at its core.",
      "colours": {
        "primary": "#2FA9D8",
        "primary_name": "Azure",
        "secondary": ["#184B66", "#F6F1E7"],
        "secondary_names": ["Deep Navy", "Warm Cream"],
        "accent": "#C1272D",
        "accent_name": "Chili Red",
        "usage": {
          "primary": "Headlines, wordmarks, highlight strokes. The hero of every layout.",
          "deep_navy": "Backgrounds, dark fills, body type when on cream. Substitutes for pure black — never use pure black in this brand.",
          "warm_cream": "Negative space, body backgrounds. Replaces pure white to keep the brand warm.",
          "chili_red": "Spice/heat callouts only — spicy margarita, house salsa, chili rim drinks. Maximum 10% of any layout."
        },
        "reasoning": "The two blues are the entire brand's signal — one must lead, the other must anchor, in every asset. Cream keeps it warm (these are family operators, not a cold concept bar). Red is earned, not decorative."
      },
      "typography": {
        "display": "Smokum",
        "display_alt": "Rye",
        "body": "DM Sans",
        "accent": "Permanent Marker",
        "ui": "Inter",
        "hierarchy": "Display (Smokum, 56–100pt): drink names, hero headlines, product launches. Body (DM Sans, 16–18pt): captions, menu copy — always clean, never distressed. Accent (Permanent Marker): one handwritten word per asset max, for promos/limited runs. UI (Inter): prices, disclaimers.",
        "reasoning": "Smokum echoes the distressed saloon-slab of the wordmark. DM Sans keeps long copy legible on mobile. Permanent Marker is a controlled dose of personality — one word, one use."
      },
      "visual_language": "Jimador silhouette as recurring watermark; tight azure/navy colour blocking (diagonal splits, horizontal bands); bold kerned headlines; agave/mezcal bottle stills; moody low-lit cocktail photography with azure rim-light.",
      "post_voice": "Bold, direct, a little cocky. Three-beat structure: feature + texture + attitude. Leans Spanish-English code-switching for select posts.",
      "voice_examples": [
        "Cucumber Margarita. 🥒 / Black salt rim. Cucumber crown. Cool and dangerous.",
        "Spicy Margarita. 🌶️ / Chili-Tajín rim. Pineapple leaf. Built for heat seekers.",
        "Millionaire Margarita. 💰 / Gold rim. Zero apologies."
      ],
      "product_categories": ["signature cocktails (Millionaire, HOMBRE, Cucumber, Espresso)", "new-menu food (launching May 5 2026)", "oyster/seafood boards", "shareable apps (guacamole, parrillada)", "launch/menu announcements", "frozen trios & tray drinks"]
    },

    "el_azteca": {
      "name": "El Azteca",
      "handle": ["@aztecadelaware", "@aztecarestaurantrehoboth"],
      "address": "Two locations: Delaware + Rehoboth Beach (addresses TBD — confirm with client)",
      "cta": "Find your nearest location | link in bio 📍",
      "personality": ["warm", "family", "vibrant"],
      "one_liner": "Heritage Mexican restaurant with two locations — the four-colour warrior palette, served generously.",
      "colours": {
        "primary": "#D9262B",
        "primary_name": "Azteca Red",
        "secondary": ["#F5C518", "#1B4D8F", "#3F7E39"],
        "secondary_names": ["Sunstone Gold", "Warrior Blue", "Chili Green"],
        "accent": "#0A0A0A",
        "accent_name": "Obsidian Black",
        "usage": {
          "primary": "Wordmarks, dish names, section headers, CTAs. Always reads as the brand voice.",
          "sunstone_gold": "Highlights, stars, featured-dish markers, price emphasis. The sunstone = the badge.",
          "warrior_blue": "Background fields (large solid blocks), trust markers (years in business, family-owned).",
          "chili_green": "Fresh/salsa/guac callouts; sub-accent for food authenticity markers.",
          "obsidian_black": "Primary canvas — matches logo box. Every asset should default to black ground with one dominant colour + one accent."
        },
        "reasoning": "The four-colour palette comes straight from the warrior's headdress and sunstone — the design system's job is to preserve that cultural saturation without turning it into a parade float. Rule: one colour dominates + one accent per layout. Black ground carries them all."
      },
      "typography": {
        "display": "Cinzel",
        "display_alt": "Trajan Pro",
        "body": "Work Sans",
        "accent": "Ceviche One",
        "ui": "Inter",
        "hierarchy": "Display (Cinzel, 48–96pt, all-caps): dish names, section headers — carved-stone heritage feel. Body (Work Sans, 16–18pt): captions, ingredients, descriptions. Accent (Ceviche One): promos, specials, daily features (the font has a handpainted taquería feel). UI (Inter, 12pt): prices, disclaimers.",
        "reasoning": "Cinzel mirrors the carved-serif feel of the El Azteca wordmark without copying it. Work Sans keeps menu copy modern so the heritage type doesn't drag into dated territory. Ceviche One is the 'hand-painted window sign' voice — reserved for daily specials and limited promos."
      },
      "visual_language": "Sunstone ring motifs; step-fret Aztec pattern borders (1–2pt, never maximalist); full-bleed food photography on black; gold rule separators; heritage + warmth signaling (decades in business, family-owned, two locations).",
      "post_voice": "Warm, abundant, playful confidence. Posts communicate generosity (portion, variety, value) and family credibility. Bilingual dish names (Spanish first, English second) where natural.",
      "voice_examples": [
        "Appetizer Sampler. 🔥 / A little bit of everything, and all of it hits.",
        "Made to Order Guacamole. 🥑 / Fresh avocado, queso fresco, and zero shortcuts.",
        "Guacamole. But make it octopus. 🐙 / Not your average appetizer.",
        "Cóctel de Camarón. 🍤 / Twenty shrimp. Azteca sauce. Avocado. You're welcome."
      ],
      "product_categories": ["tacos & birria", "molcajete guacamole (classic + octopus)", "mixed grill parrilladas", "margaritas (Millionaire is the flagship)", "desserts (churros, flan, fried ice cream)", "full-table spread hero shots", "family/heritage callouts"]
    }
  },

  "shared_system": {
    "instagram_post_specs": {
      "feed_ratio": "4:5 (1080x1350)",
      "reels_cover": "9:16 (1080x1920)",
      "story": "9:16 (1080x1920)"
    },
    "caption_structure": "[Dish/Drink Name]. [emoji]\\n\\n[One punchy line.]\\n\\n📍 [Address]\\n[CTA]",
    "group_posting_schedule": "Monday (images) · Wednesday (video, JH only) · Friday (images). All three brands post Mon/Fri.",
    "cross_post_rules": {
      "azteca_to_blue_mezcal": "Azteca food + drinks may post on Blue Mezcal.",
      "blue_mezcal_to_azteca": "Blue Mezcal new-menu food (B-44+) is EXCLUSIVE — never cross-post to Azteca.",
      "millionaire_margarita": "El Azteca logo version → Blue Mezcal only. Azteca logo version → all three accounts."
    }
  }
}
```

---

## Notes on rationale (for the humans)

- **Ivory over white for Jackson House** — gold foil + pure white looks printed-at-Staples. Ivory is the single biggest upgrade.
- **Two blues, not one, for Blue Mezcal** — the logo uses both; losing the navy flattens the brand.
- **Black canvas for El Azteca** — the logo itself sits in a black box. Respecting that gives the four headdress colours somewhere to breathe.
- **Typography pairings are all Google Fonts-available** — Rye, Playfair Display, Cormorant, Cinzel, Work Sans, DM Sans, Smokum, Ceviche One, Inter, Permanent Marker. No licensing blockers for Claude Design or web.
- **Voice examples were extracted from `jackson_house_captions_v2.md`, `blue_mezcal_captions_v2.md`, `azteca_captions_v2.md`** — these are the client-approved lines, not invented. Claude Design should keep future copy within that cadence.
- **Hex codes are derived from the logo PNGs** in `/Users/dreamartstudio/Desktop/CLIENTS/[BRAND]/branding/`. Re-run a colour-picker on the print-spec logos before sending to a printer; on-screen-to-print drift of ±5 on R/G/B is normal.
