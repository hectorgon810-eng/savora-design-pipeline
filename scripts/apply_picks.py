#!/usr/bin/env python3
"""
Apply an approved.json from the Lightroom-style review into OUTPUT/PICKS/.

Default: copies all 4+ star images (--min-stars 4).

Usage:
    python3 scripts/apply_picks.py ~/Downloads/approved_blue_mezcal_123.json
    python3 scripts/apply_picks.py ~/Downloads/approved_jh_123.json --min-stars 5
    python3 scripts/apply_picks.py ~/Downloads/approved_jh_123.json --min-stars 3
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", help="Path to approved.json")
    parser.add_argument("--min-stars", type=int, default=4,
                        help="Minimum star rating to copy (default 4). Values 1-5.")
    parser.add_argument("--organize-by-stars", action="store_true",
                        help="Subfolder per star rating in PICKS/")
    args = parser.parse_args()

    payload_path = pathlib.Path(args.payload).expanduser()
    if not payload_path.exists():
        sys.exit(f"Not found: {payload_path}")

    data = json.loads(payload_path.read_text(encoding="utf-8"))
    brand = data.get("brand", "unknown")
    by_rating = data.get("by_rating", {})

    picks_dir = ROOT / "OUTPUT" / "PICKS" / brand
    picks_dir.mkdir(parents=True, exist_ok=True)

    counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    total_copied = 0
    skipped_missing = 0

    for star in (5, 4, 3, 2, 1):
        if star < args.min_stars:
            continue
        images = by_rating.get(str(star), []) or by_rating.get(star, [])
        for img in images:
            raw = pathlib.Path(img["path"])
            # Path in approved.json may be relative to OUTPUT/ (from HTTP server
            # root) — resolve against ROOT/OUTPUT if not absolute
            if not raw.is_absolute():
                src = ROOT / "OUTPUT" / raw
            else:
                src = raw
            if not src.exists():
                print(f"  ! missing: {src}")
                skipped_missing += 1
                continue
            dst_dir = picks_dir
            if args.organize_by_stars:
                dst_dir = picks_dir / f"{star}_star"
                dst_dir.mkdir(parents=True, exist_ok=True)
            tidy = pathlib.Path(img["filename"]).stem.replace("variation_", "V")
            star_prefix = f"{star}s_" if args.organize_by_stars else f"{star}s_"
            dst = dst_dir / f"{star_prefix}{img['batch']}_{tidy}.png"
            shutil.copy2(src, dst)
            counts[star] += 1
            total_copied += 1

    print()
    print(f"✓ Copied {total_copied} image(s) to {picks_dir}")
    for star in (5, 4, 3, 2, 1):
        if counts[star]:
            print(f"    {star}★ : {counts[star]}")
    if skipped_missing:
        print(f"! Skipped {skipped_missing} missing file(s)")


if __name__ == "__main__":
    main()
