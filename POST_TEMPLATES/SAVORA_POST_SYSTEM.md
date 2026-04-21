# Savora Post System
Shared post architecture for Jackson House · Blue Mezcal · El Azteca.
Version 1 · 2026-04-20 · Maintained by DreamArt Studio

---

## 1 · What this is

This document is the **single source of truth** for how graphic posts are built across all three Savora restaurants. It is read before every Claude Design session and pasted at the top of every design prompt.

**Goals:**
- Every post per brand feels like it was made by the same designer.
- Every post across Savora's three brands feels like part of one family.
- New post types (holidays, events, announcements) fit into the system instead of creating their own.
- Operator (the poster) can brief Claude Design in under two minutes.

---

## 2 · The two-layer model

**Layer 1 — Brand Tokens (fixed).** Colour, type, logo, voice, photo treatment. Pulled from the brand style guide. Never changes per post.

**Layer 2 — Template Library (modular).** The skeleton layouts defined in each brand playbook. Swappable.

```
Claude Design prompt = [ Brand tokens ] + [ One template ] + [ Content brief ]
```

This is the only way prompts stay short enough for Claude Design to execute reliably.

---

## 3 · Post category taxonomy

Every graphic post belongs to exactly one of these six categories.

| # | Category | Covers | Cadence |
|---|---|---|---|
| A | **Product / Menu** | Dish hero, drink hero, ingredient callout, new-menu launch | Mon + Fri (photo) · Tue + Thu (graphic) |
| B | **Recurring Weekly** | Margarita Monday · Taco Tuesday · Thirsty Thursday · Weekend Brunch | Same slot every week |
| C | **Holiday / Seasonal** | Cinco de Mayo · Día de los Muertos · Valentine's · St. Patrick's · Mother's / Father's Day · NYE | Calendar-triggered |
| D | **Events** | Live music · Private event · Menu launch · Pop-up · Collab | Announcement + day-of |
| E | **Operational** | Closed today · Hours change · Reservation reminder · Gift cards · Hiring | As needed |
| F | **Evergreen CTA** | Come visit us · Reservations · Follow us · Location ping | Gap filler |

If a post doesn't fit in one of these six, we don't post it until it does.

---

## 4 · The six cohesion rules (non-negotiable)

Every graphic post across every brand must pass all six.

1. **Type lock.** Only fonts listed in the brand style guide. No substitutions, no system fonts.
2. **Colour lock.** Only hex codes from the brand palette. No freehand colour.
3. **Logo lock.** Logo sits in exactly one of three positions: bottom-left, bottom-center, or top-right. Never free-floating. Scale locked to the style guide.
4. **Grid lock.** 4:5 (1080×1350) for feed, 9:16 (1080×1920) for Stories/Reels. Never square. 48px safe margin on all sides.
5. **Voice lock.** Caption follows the brand caption formula. No marketing-speak ("amazing", "must-try", "foodie").
6. **One-hero rule.** One focal element per post — one dish, one message, one date. No two competing headlines.

If a draft breaks any of these, it goes back for revision, not out.

---

## 5 · How to prompt Claude Design

Use this three-block structure every time. Copy-paste in order.

```
BLOCK 1 — BRAND TOKENS
[Paste the JSON block for the brand from BRAND_GUIDELINES.md.]

BLOCK 2 — TEMPLATE
[Paste the template spec from the brand playbook, e.g. "Template A1 · Product Hero · Block-headline".]

BLOCK 3 — CONTENT BRIEF
- Post type: [A / B / C / D / E / F]
- Subject: [dish name, holiday, event]
- Headline: [exact words]
- Support line: [exact words, ≤8 words]
- Photo: [Cloudinary URL or "use token colour fill"]
- CTA line: [address + bio line]
- Date / time context (if any): [e.g. "Monday April 21" or "Closed today"]

DELIVER: 4:5 feed (1080×1350). If the post type is A or B, also deliver 9:16 Story (1080×1920).
```

Keep the brief terse. Never exceed 500 words total in a single Claude Design prompt.

---

## 6 · Weekly cadence (new)

Proposal to stagger photo posts and graphic posts so the feed never looks template-heavy.

| Day | Post type | Source |
|---|---|---|
| Monday | **A — Product photo** (from Vista Social CSV) | Existing scheduled post |
| Tuesday | **A or B — Graphic remix** (reuses Mon's photo as bed, or a Recurring Weekly anchor) | New Claude Design output |
| Wednesday | *(rest day or Reel)* | |
| Thursday | **B or C — Graphic** (Thirsty Thursday, or seasonal) | New Claude Design output |
| Friday | **A — Product photo** (from Vista Social CSV) | Existing scheduled post |
| Weekend | *(optional F · Evergreen)* | |

Categories D and E drop in ad hoc and displace the nearest scheduled slot.

---

## 7 · Cross-brand family rules

The three brands must feel like relatives, not strangers.

- **Shared grid.** 48px margins, 4:5, left-aligned across all three.
- **Shared caption formula.** `[Subject]. [emoji]\n\n[One punchy line.]\n\n📍 [Address]\n[CTA]`
- **Shared category taxonomy.** A–F above, same meaning across all three brands.
- **Shared posting day logic.** Mon + Fri photo, Tue + Thu graphic.

What makes each brand distinct is only: palette, typography, voice examples, photography style. Everything else is shared.

---

## 8 · File map

```
/Users/dreamartstudio/Desktop/CLAUDE/
├── BRAND_GUIDELINES.md              ← Layer 1 tokens (all three brands)
├── STYLE_GUIDES/                    ← Full brand foundation (visual)
│   ├── jackson-house-style-guide.html
│   ├── blue-mezcal-style-guide.html
│   └── el-azteca-style-guide.html
└── POST_TEMPLATES/                  ← Layer 2 templates
    ├── SAVORA_POST_SYSTEM.md        ← This file
    ├── blue-mezcal-playbook.md
    ├── jackson-house-playbook.md
    └── el-azteca-playbook.md
```

---

## 9 · What this system deliberately excludes

- **Stories.** Separate system. Use the Tue/Thu graphic as the story asset if needed.
- **Reels covers.** Separate spec in the brand style guide.
- **Ads.** Meta ads follow a different framework — see `How Winning Restaurant Ads on Meta Drive Real Conversions in 2026.pdf`.
- **Menu PDFs, merch, signage.** Out of scope for social. Use the brand style guide directly.

---

*End of system doc. Read brand playbook next.*
