# HANDOFF — Blue Mezcal Management Group Social Media
# Created April 17, 2026
# Drop this into a fresh Claude chat to continue work seamlessly

---

## WHERE WE ARE

**Status:** All 4 Vista Social CSVs built and ready to import (or imported — ask user).

**4 Instagram accounts scheduled:**
| Account | Posts | Date Range |
|---|---|---|
| @jacksonhousede | 38 | Apr 17 → Aug 24 |
| @bluemezcalrestaurant | 36 (15 own + 21 Azteca cross) | Apr 17 → Aug 21 |
| @aztecadelaware | 23 | Apr 17 → Jul 3 |
| @aztecarestaurantrehoboth | 23 | Apr 17 → Jul 3 |

**Cadence:** Monday + Friday
**Content usage:** 194 of 360 images = 54%

---

## KEY FILES — ALL IN `/Users/dreamartstudio/Desktop/CLAUDE/`

### Scripts (re-runnable)
- `build_csvs_v4.py` — generates the 4 Vista Social CSVs
- `build_preview.py` — generates visual `SCHEDULE_PREVIEW.html` for review
- `build_tracker.py` — generates `CONTENT_TRACKER.xlsx`

### Data
- `cloudinary_urls.json` — 360 image URLs by filename (AZ-1, B-3, T-9, Savora-50, etc.)
- `cloudinary_orientations.json` — H/V orientation for each image
- `csv_output/` — the 4 Vista Social CSVs
- `SCHEDULE_PREVIEW.html` — visual timeline of all posts
- `CONTENT_TRACKER.xlsx` — filterable spreadsheet of all 360 images

### Reference docs
- `MASTER_BUILD_FILE_v3.md` — superseded-ish source of truth for posts/captions/orientations
- `WORKFLOW_SYSTEM.md` — documented end-to-end workflow
- `UNUSED_IMAGES_INVENTORY.md` — 165 unused images catalogued by group
- `caption_updates_final.md` — latest caption changes
- `CLAUDE_CODE_BRIEF_v2.md` — original project brief
- Handoffs: `Jackson_House_Handoff_v2.md`, `BlueMezcal_Handoff_v2.txt`, `Azteca_Handoff_v2.txt`
- Captions: `jackson_house_captions_v2.md`, `blue_mezcal_captions_v2.md`, `azteca_captions_v2.md`

---

## PROJECT RULES (CRITICAL — PROPAGATE TO NEW CHATS)

### Image hosting (Cloudinary)
- Cloud name: `dkp42tunc`
- API key: `833335963611723`
- Secret: `uhiIua7kgZac9WVNMo-Sx06etAo`
- All 360 images live at `res.cloudinary.com/dkp42tunc/image/upload/...`
- URL map is in `cloudinary_urls.json` — never construct URLs manually

### Vista Social CSV format (REQUIRED)
```
<caption>,image,<url>,YYYY-MM-DD H:MM am/pm
```
- **No header row**
- **Multi-image posts = multiple rows**, same caption text, one URL per row
- 4 columns only: message, type, link, time

### Posting times (account-specific)
| Account | Mon | Fri | Rationale |
|---|---|---|---|
| @jacksonhousede | 11:30 am | 5:30 pm | Lunch hook → Fri dinner trigger |
| @bluemezcalrestaurant | 5:00 pm | 5:30 pm | Dinner-focused both days |
| @aztecadelaware | 5:00 pm | 5:30 pm | Dover dinner spot |
| @aztecarestaurantrehoboth | 11:00 am | 4:30 pm | Beach tourists |

### Cross-posting rules
- Azteca food/cocktails → CAN post on Blue Mezcal ✅
- Blue Mezcal NEW menu food → Blue Mezcal ONLY ❌
- BM cocktails (no Azteca logo) → Blue Mezcal only
- Millionaire Margarita (B-30/31/32, Azteca logo) → both

### Already posted — DO NOT RE-POST (from Vista Social report Mar 16-Apr 13)
- **JH:** Passionfruit Salmon, Bison Ribeye (Savora-32 to 43), Dilly Dally Dirty Martini (Apr 13), It's Giving Miami
- **BM:** Espresso Martini, Millionaire Margarita (both versions), Churros, Appetizer Sampler, Fried Ice Cream, Guac Queso Fresco, Seafood Fajitas, Enchiladas, Mixed Fajitas, Birria, Street Tacos
- **Azteca:** Appetizer Sampler, Guac QF, Seafood Fajitas, Enchiladas Mexicanas, Mixed Fajitas, Birria Tacos, Chicken Tacos, Fried Ice Cream (tortilla)

### Scheduling constraints
- **Blue Mezcal new menu embargo: May 5, 2026** (no BM own food before this date)
- **Azteca seafood cross-posts → end of BM schedule** (Rehoboth coastal angle)
- **BM own seafood (Raw Oysters, Parillada) → post freely after May 5** (it's new menu)

### Content sequencing rules (enforced in `build_csvs_v4.py`)
- Orientation-safe carousels (no H/V mixing; auto-drops mismatches)
- No 2 adjacent posts share sub-category
- No 3+ consecutive food OR drink posts
- Lifestyle/BTS spread across full schedule
- JH-28 "Behind the bar" carousel dropped T-41 (was too similar to T-40 solo team shot)

---

## USER PREFERENCES (IMPORTANT)

- **Autonomous execution** — user prefers Claude make educated guesses rather than asking repeated questions. They often don't have answers either.
- **Terse, direct answers** — no sycophantic openers or padding.
- **Strategic feel over predictable patterns** — don't do "Mon=drinks, Fri=food" or 4-drinks-in-a-row.
- **Savora is a separate Instagram account** (not yet in pipeline) for portfolio/showcase. Rule: clients must post first, then Savora reposts with 2-week buffer.

---

## USER'S PENDING QUESTIONS (pick up here)

User has "a few questions" they want to ask in a new chat. Unknown what they are yet — let them lead. Likely candidates based on recent context:

1. **Savora IG handle + posting cadence** — not yet set up
2. **Savora caption voice** — portfolio showcase? Different from clients?
3. **How to handle the 165 unused images** — more posts? Collages? Stories?
4. **Content-type-specific posting times** (more granular than account-level)
5. **Adding more posts from unused pool** — user mentioned "yes to adding unused content for all, but not yet"

---

## HOW TO PICK UP SEAMLESSLY

1. Read this file first
2. Skim `WORKFLOW_SYSTEM.md` for the full pipeline
3. Check `SCHEDULE_PREVIEW.html` in browser to see current state visually
4. Check `CONTENT_TRACKER.xlsx` for image-level status
5. Ask user: "I see you mentioned you had a few questions. What's first?"

---

## AUTO-MEMORY NOTES

Memory files at `/Users/dreamartstudio/.claude/projects/-Users-dreamartstudio-Desktop/memory/` already include:
- User: Savora team (Pedro + Jose), DreamArt Studio
- Project: Savora Marketing phase 1
- Feedback: Autonomous execution preference
- Feedback: Footage handling (G-RAID master)
- Reference: Savora KB, client files

All context should auto-load in new chats.

---

## QUICK COMMANDS

```bash
# Regenerate all 4 CSVs
cd /Users/dreamartstudio/Desktop/CLAUDE && python3 build_csvs_v4.py

# Refresh visual preview
python3 build_preview.py

# Rebuild content tracker
python3 build_tracker.py

# Open CSV folder
open csv_output/
```
