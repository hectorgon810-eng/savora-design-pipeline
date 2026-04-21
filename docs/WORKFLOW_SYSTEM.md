# VISTA SOCIAL CSV WORKFLOW — Blue Mezcal Management Group
# Documented April 14, 2026
# This is the repeatable system for building and importing social media CSVs

---

## OVERVIEW

Photography → Image logging/handoff → Caption writing → Question resolution → Cloudinary upload → CSV generation → Vista Social import

---

## TOOLS & ACCOUNTS

- **Cloudinary** (image hosting): cloud name `dkp42tunc`
  - API Key: 833335963611723
  - Folders: root level, filenames with hash suffix (e.g. `AZ-1_obtubj`)
  - URL mapping script pulls real URLs via API → `cloudinary_urls.json`

- **Vista Social** (scheduling): vistasocial.com
  - Accounts connected: jacksonhousede, bluemezcalrestaurant, aztecadelaware, aztecarestaurantrehoboth

- **Claude Code** (CSV generation): `build_csvs_v2.py`
  - Uses `cloudinary_urls.json` for real URLs
  - Outputs to `/Desktop/CLAUDE/csv_output/`

---

## VISTA SOCIAL CSV FORMAT

```
message,type,link,time
```

Rules:
- NO header row
- Column 1: Caption text (can be multiline)
- Column 2: `image` (or `video`)
- Column 3: Cloudinary URL (one per row)
- Column 4: Date+time as `YYYY-MM-DD H:MM am` or `now` or `queue next`
- Carousels = multiple rows with IDENTICAL caption, one image per row, same datetime
- No quotes needed unless content has commas (Python csv module handles this)

---

## FILE STRUCTURE

```
/Desktop/CLAUDE/
├── MASTER_BUILD_FILE_v3.md          ← Single source of truth for all posts
├── WORKFLOW_SYSTEM.md               ← This file
├── OPEN_QUESTIONS_CONTEXT.txt       ← Template for resolving client questions
├── cloudinary_urls.json             ← Auto-generated URL map (360 images)
├── build_csvs_v2.py                 ← CSV generator script
├── csv_output/
│   ├── jacksonhousede.csv
│   ├── bluemezcalrestaurant.csv
│   ├── aztecadelaware.csv
│   └── aztecarestaurantrehoboth.csv
├── Jackson_House_Handoff_v2.md      ← Image log + groupings
├── jackson_house_captions_v2.md     ← All JH captions
├── BlueMezcal_Handoff_v2.txt        ← Image log + groupings
├── blue_mezcal_captions_v2.md       ← All BM captions
├── Azteca_Handoff_v2.txt            ← Image log + groupings
├── azteca_captions_v2.md            ← All AZ captions
├── caption_updates_final.md         ← Resolved name updates
└── CLAUDE_CODE_BRIEF_v2.md          ← Project brief + open items tracker
```

---

## PROCESS — STEP BY STEP

### 1. SHOOT & UPLOAD
- Shoot images → G-RAID master vault
- Duplicate needed clips into `/savora/clients/[restaurant]/footage/`
- Compress and upload to Cloudinary (root level, naming: `PREFIX-NUMBER.jpg`)

### 2. LOG IMAGES
- Create handoff file with image groups (e.g. `AZ-1 through AZ-100`)
- Tag each image: primary pick, strong alternate, alternate, held
- Note orientation (H/V) for every image
- Define carousel groupings with orientation-safe slides

### 3. WRITE CAPTIONS
- Format: `[Dish/Drink Name]. [emoji] → punchy line(s) → 📍 address → CTA`
- Keep short — 2-4 lines max before the address
- Match brand voice per restaurant

### 4. RESOLVE QUESTIONS
- Generate `OPEN_QUESTIONS_CONTEXT.txt` with all blockers
- Take to Claude chat for client Q&A
- Bring confirmed answers back → update handoff + caption files

### 5. BUILD MASTER FILE
- Consolidate everything into one `MASTER_BUILD_FILE`
- Pre-resolve all orientation conflicts
- Tag cross-posts with account routing
- Flag already-posted items for removal
- Define scheduling rules (start date, cadence, embargoes)

### 6. GENERATE CLOUDINARY URL MAP
```bash
# Pulls all image URLs from Cloudinary API → cloudinary_urls.json
python3 build_csvs_v2.py  # URL fetch is built into the script
```

### 7. GENERATE CSVs
```bash
cd /Desktop/CLAUDE && python3 build_csvs_v2.py
```
Outputs 4 CSV files to `csv_output/`

### 8. IMPORT TO VISTA SOCIAL
- Publishing → Bulk Schedule → Import CSV
- Select profile(s) → Upload CSV → Review → Confirm
- One CSV per Instagram account
- Import order doesn't matter

---

## SCHEDULING RULES

- Posting days: Monday + Friday
- Time: 11:30 AM ET
- Never post same dish/drink back-to-back
- Alternate food/drink/lifestyle categories
- Lead with strongest visual content
- Blue Mezcal new menu food: not before launch date
- Cross-posts: same date across all accounts
- Already-posted items: check Vista Social report, remove from CSV

---

## ORIENTATION RULES

- Carousels must NOT mix H (horizontal) and V (vertical) images
- Lead image sets the ratio — all slides must match
- If conflict: drop the mismatched slide, not the lead
- Solo posts: any orientation OK

---

## CROSS-POSTING RULES

| Content | Blue Mezcal | Azteca DEL | Azteca RHB |
|---------|-------------|------------|------------|
| Azteca food | ✅ | ✅ | ✅ |
| Azteca cocktails | ✅ | ✅ | ✅ |
| BM new menu food | ✅ | ❌ | ❌ |
| BM cocktails (no AZ logo) | ✅ | ❌ | ❌ |
| Millionaire Marg (AZ logo) | ✅ | ✅ | ✅ |

---

## CURRENT STATUS (April 14, 2026)

| Account | Posts Scheduled | Date Range | Weeks |
|---------|----------------|------------|-------|
| @jacksonhousede | 33 | Apr 17 → Aug 7 | ~16.5 |
| @bluemezcalrestaurant | 18 | Apr 17 → Jun 8 | ~9 |
| @aztecadelaware | 23 | Apr 17 → Jul 3 | ~11.5 |
| @aztecarestaurantrehoboth | 23 | Apr 17 → Jul 3 | ~11.5 |

---

## FOR NEXT SHOOT

1. Name images with consistent prefix + number (e.g. `AZ-106`, `B-95`, `T-109`)
2. Log orientation immediately
3. Upload to Cloudinary same day
4. Run `build_csvs_v2.py` with new posts appended
5. Import new CSV to Vista Social (it adds to existing schedule)
