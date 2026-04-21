# CLIENTS
Per-restaurant active design workspaces. One folder per brand.

Each client folder has three sub-folders:

- `briefs/` — incoming requests. One markdown file per brief (e.g. `2026-05-brunch-push.md`). Templated below.
- `drafts/` — work-in-progress. Raw Nano Banana + HTML outputs get copied or linked here during review.
- `approved/` — final assets ready for Vista Social / client delivery. Name files with post ID (e.g. `JH-A1-001_burrata.png`).

---

## Brief template (paste into `briefs/` as a new markdown file)

```markdown
# Brief — [Restaurant] — [Date]

## Request
[One sentence on what they need.]

## Post ID
[e.g. JH-A1-001]

## Template
[A1 / B1 / C1 / D1 / E1 / F1]

## Subject + copy
- Headline: [exact words]
- Support: [exact words]
- CTA: [if non-standard]

## Source image
- Cloudinary key: [e.g. Savora-48]
- OR new photo attached at: [path]

## Scheduling
- Target date: [YYYY-MM-DD]
- Channel: [Feed · Story · Reel · Print]

## Variations to generate
- Nano Banana: [5 · default]
- Claude Design HTML: [3 · default]

## Review notes
[Any constraints, references, do-not-use items]
```

---

## Workflow per brief

1. Drop brief into `briefs/`
2. Run both generators per brief
3. Open `OUTPUT/` folders, pick winner + log to `TASTE_INTELLIGENCE.md`
4. Copy approved file into `approved/`
5. Schedule in Vista Social (or update the relevant CSV)
