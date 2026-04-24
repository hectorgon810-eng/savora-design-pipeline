# Pipeline Gotchas — read before running

Operational landmines that aren't obvious from the code. Review before a fresh laptop / fresh Claude picks this up.

---

## 1. OpenAI org verification (gpt-image-2 access)

- `gpt-image-2` requires **verified organization** on OpenAI. If the org isn't verified, the API returns 403 "Your organization must be verified to use the model `gpt-image-2`."
- Verification runs through Persona ID check. Usually instant–15 min, occasionally **24–72 hours**.
- **Check status BEFORE queuing a batch:** https://platform.openai.com/settings/organization/general → look for "Verified" badge.
- If you get blocked mid-run, posts fail silently with 403; the runner logs `! gpt-image-2 errored: PermissionDeniedError`. No partial output — start over once verified.

## 2. OpenAI billing hard limit

- Separate from org verification. `gpt-image-2` requests fail with 400 `Billing hard limit has been reached` when the usage cap hits even a few cents below the limit.
- **Raise before every big batch:** https://platform.openai.com/settings/organization/limits → Hard limit to at least $20 for a 150-post batch.
- 100 images at 1024×1280 tier ≈ $4. 300 images ≈ $12. Buffer accordingly.

## 3. Cloudinary folder convention (when apply_feed.py ships)

- Upload new generated PNGs nested by brand + YYYY-MM for auditability:
  ```
  savora-gen/
    blue_mezcal/
      2026-05/
      2026-06/
    jackson_house/
    azteca/
    savora/
  ```
- Vista Social doesn't care about path structure. WE will care 3 months in when auditing which post went out for which brand on which month. Flat folders are pain to reorganize later; per-brand + per-month is effectively free to set now.
- `apply_feed.py` (not yet built) should default to this layout.

## 4. El Azteca menu-per-location delta

- **Unresolved factual-integrity risk.** Vista Social CSVs for Camden (Delaware) and Rehoboth show IDENTICAL dish lists. User believes menus actually DIFFER between locations.
- If Octopus Guacamole is Rehoboth-only and Camden's Vista account scheduled it, there's already cross-contamination upstream we can't detect from CSV alone.
- Pipeline locks only verify subject strings against voice seeds, NOT against per-location menus. This is a blind spot.
- **Preventive:** `bulk_build.py --location {camden|dover|rehoboth}` flag exists — restrict asset pool when location-specific batches are needed. Default (no flag) runs all AZ assets.
- **Resolution path:** Hector collects current menus per location (physical photo or PDF from each manager), then maintains a per-location allowlist in `bulk_build.py` — a simple dict of which AZ dishes are served where. Until that lands, assume cross-location drift is possible.

## 5. Posting rhythm vs retainer contract

- Feed composer defaults to **5x-week rhythm**: Mon + Tue + Thu + Fri. Wed = reserved for video (per Hector's current post schedule). Sat + Sun = off.
- Vista-scheduled posts may already live on Wed/Sat/Sun from earlier campaigns — composer shows them on their exact dates, but the *new-post auto-fill* only targets Tue + Thu.
- **Verify against the BMMG retainer deliverable language** before exporting any feed JSON that becomes a Vista CSV. If the signed contract says "7 posts/week" or "daily", either:
  - Adjust `generate_slot_dates()` in `scripts/build_feed_composer.py` to include the required days, OR
  - Renegotiate the deliverable language with the client.
- Current allowed set: `{0: Mon, 1: Tue, 3: Thu, 4: Fri}` in the `allowed` set. Add `2` to include Wed, `5` for Sat, `6` for Sun.

## 6. Real-image-lock vs AI-hallucinated dish photos

- `REAL-IMAGE IDENTITY LOCK` is baked into every prompt but both NB-Pro and gpt-image-2 occasionally "re-interpret" the reference photo when the angle demands extreme crop or cut-out silhouettes.
- Spot-check every 4★+ approved image before posting. If the dish is subtly wrong (different plating, extra garnish, different glass shape), reject and re-run.
- Bedrock rule: Savora does NOT serve AI-generated food photography. Real photos only, designed around — never regenerated.

## 7. Logo-identity-lock implementation

- Post-gen PIL composite pastes the REAL logo PNG at bottom-right of every output regardless of what the model drew. This is the actual enforcement — the prompt-level `LOGO IDENTITY LOCK` block is just belt-and-suspenders.
- If a logo looks off, check `BRAND_PROFILES/logos/{brand}.png` first — that file IS the ground truth. Replacing that PNG updates every future generation.

## 8. localStorage session collision

- Reviewer + feed composer use `localStorage` with keys versioned by brand + image count. If two batches happen to have the same count, the older session may bleed into the newer review.
- Safety: both scripts bump the version suffix (`_v5_`, `_v3_`) on inventory-breaking changes. If you see stale state, bump the version literal in `STORAGE_KEY` OR open browser devtools → Application → Local Storage → clear site data.

## 9. Safari vs Chrome for reviewer/composer

- Safari caches HTML aggressively. After a rebuild, hard-refresh (Cmd+Option+E then Cmd+R) or open in Chrome.
- Chrome generally more reliable for the feed composer's drag-drop and scroll-overflow CSS. Default to Chrome.

## 10. Running commands from correct cwd

- `bulk_build.py`, `build_tinder_review.py`, `build_feed_composer.py` all resolve paths relative to `ROOT = pathlib.Path(__file__).resolve().parent.parent`. Safe from any cwd when called via `python3 /full/path/script.py`.
- But `apply_picks.py` expects relative paths in the JSON and resolves against `ROOT / OUTPUT/`. Run from any cwd — it figures out the root.
- Background bash `run_in_background=True` with chained `cd ... && python3 scripts/...` occasionally fails because the subshell's working dir doesn't persist. Use absolute paths or run the python directly without `cd`.
