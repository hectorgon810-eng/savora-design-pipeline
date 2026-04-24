# El Azteca — Feedback Log

## 2026-04-23 — Round 1 review (50 images, 2×5★ / 20×4★)

### STYLE ANCHORS (5★)
- **BULK-021** — typography weight matches logo. Use as reference.
- **BULK-024** — typography weight matches logo. Use as reference.

### CRITICAL FIXES

**1. Wrong-arrow labeling (suspected CSV bug)**
- Guac being labeled "octopus guac" in output → CSV row probably has octopus in guac's name field.
- Action: audit `briefs/` CSV. Confirm no mislabeled rows. Especially: guac, salsas, proteins.

**2. Menu mismatch across locations (HIGH RISK)**
- Rehoboth vs Camden vs Dover have different menus.
- If octopus only at Rehoboth, posting it on Camden account = brand damage.
- Action: menu cross-reference task spawned. Each menu item must be tagged with which locations carry it.
- Until map exists: do NOT post any item Hector hasn't verified for that location.

**3. Typography weight**
- 2★ images have chunky/heavy generic bold sans.
- Target: weight + letterform feel of the **actual Azteca logo**. Lighter than default bold.
- Update BRAND_PROFILES/el-azteca typography spec to reference the logo, not "bold serif" generic.

**4. Arrow/callout rule**
- NO arrows on obvious items: meat, steak, chicken, rice, beans, lettuce, cheese, tortilla.
- Arrows ONLY for small detail items the model can label reliably (specific sauce, specific garnish Hector confirmed).
- Machine mislabels small items more often than it gets them right. Safer to skip.

**5. Logo handling (IDENTITY LOCK)**
- No redesigned logo. If image shows drawn Azteca logo, it must be the actual logo illustrated — not reinvented.
- BULK-047 leaked "La Bamba" text — add negative prompt: no "La Bamba", no invented brand names.

**6. No fake specials**
- No "holiday menu", "seasonal special", "cumbia night", "upcoming" claims unless Hector verifies first.
- Cumbia night: pending verification.

### POSITIVE — DO MORE OF

- **Reviewer-quote posts.** Hector gave 5★ to 2 images using this format. Scrape Google reviews per location, turn top quotes into posts. This is the "usable → great" upgrade.
- Use real menu items only, real logo only, typography matched to logo weight.

### PROMPT NEGATIVES TO ADD

```
- no "La Bamba" text
- no invented restaurant names
- no arrows on meat/steak/rice/beans/tortilla/cheese/lettuce
- no "special menu" / "holiday menu" / "cumbia night" claims
- no redesigned logo (must be actual El Azteca logo if drawn)
- typography weight: match logo weight, not generic bold
```
