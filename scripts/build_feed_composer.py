#!/usr/bin/env python3
"""
Feed Composer v2 — Slot-based IG feed scheduler + drag-drop composer.

Auto-assigns Mon/Tue/Thu/Fri dates from TODAY → Aug 31 to every post (existing scheduled
posts keep their original dates; new generated posts + picks get auto-slotted
into the first available Tue/Thu).

Controls:
  - Drag from pool → slot: replaces that slot's post (evicted goes to pool)
  - Drag between slots: SWAPS the two posts (dates stay, content swaps)
  - Click cell: cycle accept → reject → pending
  - Right-click: toggle carousel
  - Export: feed_{brand}_{timestamp}.json — full schedule ready for Vista CSV

Usage:
  python3 scripts/build_feed_composer.py --brand blue_mezcal
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import subprocess
import sys
from datetime import date, datetime, timedelta

ROOT = pathlib.Path(__file__).resolve().parent.parent

BRAND_CONFIG = {
    "blue_mezcal": {
        "name": "Blue Mezcal",
        "csv": "bluemezcalrestaurant.csv",
        "post_times": {0: "17:00", 1: "17:00", 3: "17:30", 4: "17:30"},
        "theme": {
            "ink": "#1E3A8A", "ground": "#F3ECD8", "accent": "#C9A24B",
            "muted": "#8a7c5c", "hairline": "rgba(30, 58, 138, 0.18)",
            "font_hero": "'Fraunces', serif", "font_ui": "'Outfit', sans-serif",
            "google_fonts": "family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400&family=Outfit:wght@400;500;600;700",
        },
    },
    "jackson_house": {
        "name": "Jackson House",
        "csv": "jacksonhousede.csv",
        "post_times": {0: "17:30", 1: "17:30", 3: "18:00", 4: "18:00"},
        "theme": {
            "ink": "#F2EADF", "ground": "#0C0B0A", "accent": "#C9A24B",
            "muted": "#7a6e55", "hairline": "rgba(201, 162, 75, 0.22)",
            "font_hero": "'Playfair Display', serif", "font_ui": "'Outfit', sans-serif",
            "google_fonts": "family=Playfair+Display:ital,wght@0,500;0,700;1,500;1,700&family=Outfit:wght@400;500;600;700",
        },
    },
    "azteca": {
        "name": "El Azteca",
        "csv": "aztecadelaware.csv",
        "post_times": {0: "17:00", 1: "17:00", 3: "17:30", 4: "17:30"},
        "theme": {
            "ink": "#18140f", "ground": "#F8F2DF", "accent": "#E63946",
            "muted": "#7a6e55", "hairline": "rgba(230, 57, 70, 0.24)",
            "font_hero": "'Alfa Slab One', serif", "font_ui": "'Outfit', sans-serif",
            "google_fonts": "family=Alfa+Slab+One&family=Outfit:wght@400;500;600;700",
        },
    },
    "aztecarestaurantrehoboth": {
        "name": "Azteca Rehoboth",
        "csv": "aztecarestaurantrehoboth.csv",
        "post_times": {0: "11:00", 4: "16:30"},
        "theme": {
            "ink": "#18140f", "ground": "#F8F2DF", "accent": "#E63946",
            "muted": "#7a6e55", "hairline": "rgba(230, 57, 70, 0.24)",
            "font_hero": "'Alfa Slab One', serif", "font_ui": "'Outfit', sans-serif",
            "google_fonts": "family=Alfa+Slab+One&family=Outfit:wght@400;500;600;700",
        },
    },
}


def generate_slot_dates(end_date: date) -> list[date]:
    """Mon/Tue/Thu/Fri today→end_date. Wed=video, Sat/Sun=off. 5x-week rhythm.
    Tue + Thu = new generated-post days. Mon + Fri = existing scheduled Vista days."""
    today = date.today()
    d = today
    out = []
    # Allowed: Mon(0), Tue(1), Thu(3), Fri(4). Skip Wed(2), Sat(5), Sun(6).
    allowed = {0, 1, 3, 4}
    while d <= end_date:
        if d.weekday() in allowed:
            out.append(d)
        d += timedelta(days=1)
    return out


def parse_vista_datetime(value: str) -> datetime | None:
    """Parse known Vista CSV date formats."""
    text = value.strip()
    for fmt in ("%Y-%m-%d %I:%M %p", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def slot_time_for_date(cfg: dict, d: date) -> str:
    return cfg.get("post_times", {}).get(d.weekday(), "17:00")


def load_scheduled(brand: str) -> list[dict]:
    cfg = BRAND_CONFIG[brand]
    csv_path = ROOT / "VISTA_SOCIAL_CSVS" / cfg["csv"]
    if not csv_path.exists():
        return []
    out = []
    seen_urls = set()
    with csv_path.open() as f:
        for row in csv.reader(f):
            if len(row) < 4:
                continue
            caption = row[0]
            kind = row[1] if len(row) > 1 else "image"
            url = row[2] if len(row) > 2 else ""
            sched = row[3] if len(row) > 3 else ""
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            first_line = caption.split("\n")[0].strip().rstrip(". ")
            out.append({
                "id": f"sched_{len(out)}",
                "source": "scheduled",
                "url": url,
                "caption": caption,
                "caption_preview": first_line[:70],
                "original_date": sched,
                "original_time": (
                    parse_vista_datetime(sched).strftime("%H:%M")
                    if parse_vista_datetime(sched) else ""
                ),
                "status": "accepted",
            })
    return out


def load_unscheduled(brand: str) -> list[dict]:
    base = ROOT / "OUTPUT" / "nano_banana" / brand
    if not base.exists():
        return []
    out = []
    for folder in sorted(base.iterdir()):
        if not folder.is_dir() or not folder.name.startswith("BULK-"):
            continue
        png = folder / "variation_1.png"
        if not png.exists():
            continue
        plog = folder / "prompts.jsonl"
        subject = ""
        support = ""
        if plog.exists():
            try:
                d = json.loads(plog.read_text().strip())
                subject = d.get("subject", "")
                support = d.get("support", "")
            except Exception:
                pass
        rel = str(png.relative_to(ROOT / "OUTPUT"))
        out.append({
            "id": f"bulk_{folder.name}",
            "source": "bulk",
            "batch": folder.name,
            "url": rel,
            "caption": f"{subject}\n{support}".strip(),
            "caption_preview": subject[:70] or folder.name,
            "status": "pending",
        })
    return out


def load_picks(brand: str) -> list[dict]:
    picks = ROOT / "OUTPUT" / "PICKS" / brand
    if not picks.exists():
        return []
    out = []
    for png in sorted(picks.iterdir()):
        if not png.name.endswith(".png"):
            continue
        rel = str(png.relative_to(ROOT / "OUTPUT"))
        out.append({
            "id": f"pick_{png.stem}",
            "source": "picks",
            "filename": png.name,
            "url": rel,
            "caption": png.stem.replace("_", " "),
            "caption_preview": png.stem[:70],
            "status": "accepted",
        })
    return out


def build_slots(brand: str, scheduled: list[dict], new_posts: list[dict]) -> list[dict]:
    """Build date slots today→Aug 31 (no Wed). Pre-fill ONLY with scheduled
    Vista-CSV posts matching exact date. Everything else stays empty for the
    user to drag-drop from pool."""
    cfg = BRAND_CONFIG[brand]
    end = date(2026, 8, 31)
    all_dates = generate_slot_dates(end)
    scheduled_by_date = {}
    for p in scheduled:
        parsed = parse_vista_datetime(p.get("original_date", ""))
        try:
            dt = parsed.date() if parsed else datetime.strptime(
                p["original_date"].split(" ")[0], "%Y-%m-%d"
            ).date()
            scheduled_by_date.setdefault(dt, []).append(p)
        except Exception:
            scheduled_by_date.setdefault(None, []).append(p)

    # Include scheduled-post dates that may fall on non-Tue days
    slot_dates = set(all_dates)
    for d in scheduled_by_date.keys():
        if d is not None and d >= date.today():
            slot_dates.add(d)
    sorted_dates = sorted(slot_dates)

    slots = []
    new_queue = list(new_posts)
    for d in sorted_dates:
        dow = d.strftime("%a")
        time_str = slot_time_for_date(cfg, d)
        # Priority 1: Vista-scheduled post matching this exact date
        post = None
        if d in scheduled_by_date and scheduled_by_date[d]:
            post = scheduled_by_date[d].pop(0)
            time_str = post.get("original_time") or (
                parse_vista_datetime(post.get("original_date", "")).strftime("%H:%M")
                if parse_vista_datetime(post.get("original_date", "")) else time_str
            )
        # Priority 2: on Tue/Thu (new-post days) auto-fill from pool
        elif d.weekday() in (1, 3) and new_queue:
            post = new_queue.pop(0)
        slots.append({
            "date": d.isoformat(),
            "dow": dow,
            "time": time_str,
            "post": post,
        })

    leftover = scheduled_by_date.get(None, [])
    # Remaining unassigned new posts go to pool
    return slots, leftover, new_queue


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Feed · {brand_name}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?{google_fonts}&display=swap" rel="stylesheet">
<style>
:root {{
  --font-hero: {font_hero};
  --font-ui: {font_ui};
  --ink: {ink};
  --ground: {ground};
  --accent: {accent};
  --muted: {muted};
  --hairline: {hairline};
  --soft: color-mix(in oklab, var(--ground) 92%, #000 4%);
  --softer: color-mix(in oklab, var(--ground) 86%, #000 6%);
  --shadow-md: 0 1px 2px rgba(0,0,0,0.18), 0 8px 24px rgba(0,0,0,0.10);
  --shadow-lg: 0 6px 18px rgba(0,0,0,0.22), 0 24px 48px rgba(0,0,0,0.16);
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
  --radius-sm: 4px;
  --radius-md: 10px;
  --radius-lg: 14px;
}}
[data-theme="light"] {{
  --ground: #f5f1e8;
  --ink: #1a1814;
  --muted: #6b6259;
  --hairline: rgba(0,0,0,0.10);
  --soft: rgba(0,0,0,0.025);
  --softer: rgba(0,0,0,0.05);
  --shadow-md: 0 1px 2px rgba(0,0,0,0.06), 0 6px 18px rgba(0,0,0,0.06);
  --shadow-lg: 0 8px 22px rgba(0,0,0,0.10), 0 24px 60px rgba(0,0,0,0.10);
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  min-height: 100dvh; background: var(--ground); color: var(--ink);
  font-family: var(--font-ui); overflow: hidden;
  -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
  font-feature-settings: "ss01", "kern";
}}
body {{ display: flex; flex-direction: column; }}

header {{
  padding: 18px 28px 16px;
  display: flex; justify-content: space-between; align-items: center;
  gap: 24px;
  border-bottom: 1px solid var(--hairline);
  background: color-mix(in oklab, var(--ground) 96%, transparent);
  backdrop-filter: blur(12px);
  z-index: 10;
}}
header .brand-block {{ display: flex; flex-direction: column; gap: 4px; }}
header .wordmark {{
  font-family: var(--font-hero); font-style: italic; font-size: 26px;
  color: var(--ink); letter-spacing: -0.015em; line-height: 1;
}}
header .wordmark em {{ font-style: normal; font-weight: 500; letter-spacing: -0.01em; }}
header .wordmark .sep {{ color: var(--muted); margin: 0 8px; font-style: normal; }}
header .kicker {{
  font-size: 9.5px; color: var(--muted); letter-spacing: 0.26em;
  text-transform: uppercase; font-weight: 600;
}}
header .center-bar {{
  display: flex; gap: 8px; align-items: center;
}}
header .stats {{
  display: flex; gap: 16px; font-size: 10px; color: var(--muted);
  letter-spacing: 0.18em; text-transform: uppercase; font-weight: 600;
}}
header .stats span {{ display: flex; align-items: baseline; gap: 6px; }}
header .stats b {{
  color: var(--ink); font-weight: 700; font-size: 16px; letter-spacing: -0.01em;
  font-variant-numeric: tabular-nums; font-family: var(--font-hero);
}}
header .save-pill {{
  font-size: 9px; letter-spacing: 0.2em; text-transform: uppercase;
  color: var(--muted); padding: 5px 11px; border-radius: 999px;
  border: 1px solid var(--hairline); display: flex; align-items: center; gap: 6px;
  font-weight: 600;
}}
header .save-pill::before {{
  content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--accent);
  box-shadow: 0 0 0 3px color-mix(in oklab, var(--accent) 20%, transparent);
}}
header .header-actions {{ display: flex; gap: 8px; align-items: center; }}
.icon-btn {{
  background: transparent; color: var(--ink); border: 1px solid var(--hairline);
  border-radius: 999px; width: 36px; height: 36px;
  display: inline-flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 14px; transition: all 0.15s var(--ease);
  font-family: var(--font-ui);
}}
.icon-btn:hover {{ border-color: var(--accent); color: var(--accent); }}

main {{
  flex: 1;
  display: grid;
  grid-template-columns: 300px minmax(420px, 1fr) 340px;
  grid-template-rows: minmax(0, 1fr);
  gap: 16px;
  padding: 16px;
  overflow: hidden;
  min-height: 0;
  height: calc(100dvh - 140px); /* explicit bound so feed-wrap definitely scrolls */
}}
body.mode-client main {{
  grid-template-columns: minmax(440px, 1fr) 360px;
  max-width: 1180px;
  margin: 0 auto;
  width: 100%;
}}
body.mode-client .internal-only {{ display: none !important; }}
body.mode-client .client-only {{ display: initial !important; }}
body.mode-client .feed {{ max-width: 720px; }}
body.mode-client .feed-wrap {{ max-height: calc(100dvh - 230px); }}
body.mode-client .slot.empty {{ display: none; }}

.pane {{
  background: color-mix(in oklab, var(--ground) 94%, #000 2%);
  border: 1px solid var(--hairline);
  border-radius: 10px;
  padding: 14px;
  overflow: hidden;
  display: flex; flex-direction: column;
  min-height: 0;  /* flex overflow fix — without this, children don't scroll */
}}
.pane h3 {{ font-family: var(--font-hero); font-style: italic; font-weight: 400; font-size: 18px; color: var(--ink); }}
.pane .meta {{ font-size: 10px; color: var(--muted); letter-spacing: 0.16em; text-transform: uppercase; margin-bottom: 10px; }}

/* Pool (left) */
.pool-tabs {{ display: flex; gap: 4px; margin-bottom: 10px; }}
.pool-tabs button {{
  flex: 1; background: transparent; border: 1px solid var(--hairline);
  color: var(--muted); padding: 6px 10px; font-size: 9px; font-weight: 600;
  letter-spacing: 0.14em; text-transform: uppercase; border-radius: 4px;
  cursor: pointer; font-family: var(--font-ui);
  transition: all 0.15s var(--ease);
}}
.pool-tabs button.active {{ background: var(--ink); color: var(--ground); border-color: var(--ink); }}
.pool {{ overflow-y: auto; padding-right: 4px; flex: 1; min-height: 0; max-height: calc(100dvh - 300px); }}
.pool-card {{
  background: var(--ground); border: 1px solid var(--hairline);
  border-radius: 6px; margin-bottom: 8px; padding: 6px;
  cursor: grab; transition: transform 0.15s var(--ease), border-color 0.15s var(--ease);
  display: grid; grid-template-columns: 56px 1fr; gap: 8px; align-items: center;
}}
.pool-card:hover {{ transform: translateX(2px); border-color: var(--accent); }}
.pool-card img {{ width: 56px; height: 70px; object-fit: cover; border-radius: 3px; background: #eee; }}
.pool-card .info {{ overflow: hidden; }}
.pool-card .caption {{ font-size: 11px; color: var(--ink); font-weight: 500; line-height: 1.3; max-height: 2.6em; overflow: hidden; }}
.pool-card .tag {{ font-size: 9px; color: var(--accent); letter-spacing: 0.1em; text-transform: uppercase; margin-top: 2px; font-weight: 600; }}

/* Feed (center) */
.feed-wrap {{ overflow-y: scroll; overflow-x: hidden; padding: 4px; flex: 1; min-height: 0; scrollbar-width: auto; max-height: calc(100dvh - 230px); }}
.feed-wrap::-webkit-scrollbar {{ width: 12px; }}
.feed-wrap::-webkit-scrollbar-track {{ background: color-mix(in oklab, var(--ground) 80%, #000 4%); border-radius: 6px; }}
.feed-wrap::-webkit-scrollbar-thumb {{ background: var(--accent); border-radius: 6px; border: 2px solid transparent; background-clip: padding-box; }}
.feed-wrap::-webkit-scrollbar-thumb:hover {{ border-width: 1px; }}
.pool::-webkit-scrollbar {{ width: 10px; }}
.pool::-webkit-scrollbar-thumb {{ background: var(--accent); border-radius: 5px; opacity: 0.5; }}
.pool::-webkit-scrollbar-track {{ background: transparent; }}
.feed {{
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 3px;
  max-width: 960px;
  margin: 0 auto;
}}
.slot {{
  position: relative;
  aspect-ratio: 1 / 1;
  background: color-mix(in oklab, var(--ground) 80%, #000 4%);
  border: 2px solid transparent;
  border-radius: 2px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.15s var(--ease), transform 0.15s var(--ease);
}}
.slot:hover {{ z-index: 3; transform: scale(1.04); }}
.slot img {{ width: 100%; height: 100%; object-fit: cover; display: block; background: color-mix(in oklab, var(--ground) 70%, #000 10%); }}
.slot.empty {{ background: repeating-linear-gradient(45deg, color-mix(in oklab, var(--ground) 85%, #000 3%), color-mix(in oklab, var(--ground) 85%, #000 3%) 6px, color-mix(in oklab, var(--ground) 80%, #000 5%) 6px, color-mix(in oklab, var(--ground) 80%, #000 5%) 12px); border-color: var(--hairline); }}
.slot.empty::after {{ content: "drop"; position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 9px; color: var(--muted); letter-spacing: 0.2em; text-transform: uppercase; }}
.slot .date-badge {{
  position: absolute; top: 4px; left: 4px; padding: 2px 6px;
  background: rgba(0,0,0,0.78); color: #fff;
  font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase;
  border-radius: 3px; font-weight: 600; font-variant-numeric: tabular-nums;
}}
.slot .source-badge {{
  position: absolute; top: 4px; right: 4px; padding: 2px 6px;
  background: var(--accent); color: var(--ground);
  font-size: 8px; letter-spacing: 0.14em; text-transform: uppercase;
  border-radius: 3px; font-weight: 700;
}}
.slot.status-accepted {{ border-color: #4caf50; }}
.slot.status-rejected {{ border-color: #e77e7e; opacity: 0.55; }}
.slot.status-pending {{ border-color: color-mix(in oklab, var(--accent) 65%, transparent); }}
.slot.carousel::before {{
  content: "⎘"; position: absolute; bottom: 4px; right: 4px;
  background: var(--ink); color: var(--ground);
  width: 18px; height: 18px; border-radius: 50%;
  font-size: 12px; display: flex; align-items: center; justify-content: center; font-weight: 700;
  z-index: 2;
}}
.slot.drag-over {{ border-color: var(--accent); transform: scale(1.06); }}
.slot.selected {{ outline: 2px solid var(--accent); outline-offset: -5px; }}

/* Inspector */
.inspector-empty {{
  flex: 1; display: grid; place-items: center; text-align: center;
  color: var(--muted); font-size: 12px; line-height: 1.5;
  border: 1px dashed var(--hairline); border-radius: 6px; padding: 18px;
}}
.inspector-content {{ overflow-y: auto; padding-right: 4px; flex: 1; min-height: 0; }}
.preview-card {{ border: 1px solid var(--hairline); border-radius: 6px; overflow: hidden; background: var(--ground); margin-bottom: 12px; }}
.preview-card img {{ width: 100%; aspect-ratio: 4 / 5; object-fit: cover; display: block; background: color-mix(in oklab, var(--ground) 70%, #000 10%); }}
.field {{ margin-bottom: 12px; }}
.field label {{
  display: block; margin-bottom: 5px; font-size: 9px; color: var(--muted);
  letter-spacing: 0.16em; text-transform: uppercase; font-weight: 700;
}}
.field input, .field textarea, .field select {{
  width: 100%; border: 1px solid var(--hairline); border-radius: 5px;
  background: color-mix(in oklab, var(--ground) 92%, #000 3%);
  color: var(--ink); font-family: var(--font-ui); font-size: 12px;
  padding: 9px 10px; outline: none;
}}
.field textarea {{ min-height: 118px; resize: vertical; line-height: 1.45; }}
.segmented {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; }}
.segmented button {{
  border: 1px solid var(--hairline); background: transparent; color: var(--muted);
  border-radius: 4px; padding: 8px 6px; font-family: var(--font-ui);
  font-size: 9px; text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700;
}}
.segmented button.active {{ background: var(--ink); color: var(--ground); border-color: var(--ink); }}
.micro-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
.inspector-actions {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 12px; }}

footer {{
  padding: 10px 18px; border-top: 1px solid var(--hairline);
  display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;
  background: color-mix(in oklab, var(--ground) 94%, transparent);
}}
button.action {{
  background: transparent; border: 1px solid var(--hairline); color: var(--ink);
  padding: 9px 18px; font-size: 10px; font-weight: 600;
  letter-spacing: 0.18em; text-transform: uppercase;
  border-radius: 999px; cursor: pointer; font-family: var(--font-ui);
  transition: all 0.15s var(--ease);
}}
button.action:hover {{ background: color-mix(in oklab, var(--ground) 80%, #000 6%); }}
button.action.primary {{ background: var(--ink); color: var(--ground); border-color: var(--ink); }}
button.action.primary:hover {{ background: var(--accent); border-color: var(--accent); color: var(--ground); }}

.hint {{ font-size: 10px; color: var(--muted); letter-spacing: 0.04em; margin-top: 8px; line-height: 1.6; }}
.hint kbd {{ background: var(--hairline); padding: 1px 5px; border-radius: 2px; font-family: 'SF Mono', monospace; font-size: 9px; color: var(--ink); }}
.client-only {{ display: none !important; }}
.mode-pill {{
  display: inline-flex; align-items: center; gap: 6px;
  border: 1px solid var(--hairline); border-radius: 999px;
  padding: 5px 9px; font-size: 9px; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--muted); margin-left: 10px;
}}
.suggest-note {{
  border: 1px solid var(--hairline); border-radius: 6px;
  padding: 10px; color: var(--muted); font-size: 11px;
  line-height: 1.45; margin-bottom: 12px;
}}
</style>
</head>
<body>
<header>
  <div>
    <div class="wordmark"><em>{brand_name}</em> · Feed Scheduler <span class="mode-pill" id="modePill">Internal</span></div>
    <div class="kicker" id="modeKicker">Today → Aug 31 · Mon/Tue/Thu/Fri slots · Drag to swap</div>
  </div>
  <div class="stats">
    <span>Slots<b id="sSlots">0</b></span>
    <span>Filled<b id="sFilled">0</b></span>
    <span>Accepted<b id="sAccepted">0</b></span>
    <span>Rejected<b id="sRejected">0</b></span>
    <span>Pool<b id="sPool">0</b></span>
  </div>
</header>

<main>
  <div class="pane internal-only">
    <h3>Content pool</h3>
    <div class="meta">Drag into feed</div>
    <div class="pool-tabs">
      <button class="active" data-tab="all">All <span id="tAll">0</span></button>
      <button data-tab="new">New <span id="tNew">0</span></button>
      <button data-tab="picks">Picks <span id="tPicks">0</span></button>
    </div>
    <div class="pool" id="pool"></div>
    <div class="hint">
      <kbd>drag</kbd> pool → slot replaces it<br>
      <kbd>drag</kbd> slot → slot swaps<br>
      <kbd>click</kbd> slot cycles status<br>
      <kbd>right-click</kbd> slot marks carousel<br>
      <kbd>Export</kbd> when ready
    </div>
  </div>

  <div class="pane">
    <h3>Feed · most recent top</h3>
    <div class="meta">IG 3-col preview · {slot_count} Mon/Tue/Thu/Fri slots</div>
    <div class="feed-wrap"><div class="feed" id="feed"></div></div>
  </div>

  <div class="pane">
    <h3>Post inspector</h3>
    <div class="meta">Caption · CTA · crop-safe export</div>
    <div id="inspector" class="inspector-content"></div>
  </div>
</main>

<footer>
  <button class="action internal-only" onclick="resetSession()">Reset session</button>
  <button class="action internal-only" onclick="clearStatuses()">Clear statuses</button>
  <button class="action internal-only" onclick="exportFeed()">Export feed.json</button>
  <button class="action primary internal-only" onclick="exportVistaCsv()">Export Vista CSV</button>
  <button class="action primary client-only" onclick="exportClientSuggestions()">Suggest Changes</button>
</footer>

<script>
const INITIAL_SLOTS = {slots_json};
const INITIAL_POOL_NEW = {pool_new_json};
const INITIAL_POOL_PICKS = {pool_picks_json};
const BRAND = "{brand}";
const SEARCH_PARAMS = new URLSearchParams(window.location.search);
const APP_MODE = SEARCH_PARAMS.get("mode") === "client" ? "client" : "internal";
const IS_CLIENT_MODE = APP_MODE === "client";
const STORAGE_KEY = "feedv3_" + BRAND + "_" + APP_MODE + "_" + INITIAL_SLOTS.length;

let state = {{
  slots: [],          // [{{date, dow, time, post: {{...}} | null}}]
  pool: [],           // unified content pool — everything not in a slot
  activeTab: "all",
  selectedIdx: 0,
}};

try {{
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) {{
    state = JSON.parse(saved);
  }} else {{
    state.slots = JSON.parse(JSON.stringify(INITIAL_SLOTS));
    state.pool = [...INITIAL_POOL_NEW, ...INITIAL_POOL_PICKS];
  }}
}} catch(e) {{
  state.slots = JSON.parse(JSON.stringify(INITIAL_SLOTS));
  state.pool = [...INITIAL_POOL_NEW, ...INITIAL_POOL_PICKS];
}}
if (typeof state.selectedIdx !== "number") state.selectedIdx = 0;
document.body.classList.toggle("mode-client", IS_CLIENT_MODE);
document.body.classList.toggle("mode-internal", !IS_CLIENT_MODE);

function save() {{
  try {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }} catch(e) {{}}
}}

function resolveUrl(post) {{
  if (!post) return "";
  if (post.url.startsWith("http")) return post.url;
  return post.url;
}}

function formatDate(isoDate, dow, time) {{
  const d = new Date(isoDate + "T00:00:00");
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${{dow.toUpperCase()}} ${{mm}}-${{dd}}`;
}}

function renderPool() {{
  const el = document.getElementById("pool");
  // Filter pool by active tab
  let filtered = state.pool;
  if (state.activeTab === "new") filtered = state.pool.filter(p => p.source === "bulk");
  else if (state.activeTab === "picks") filtered = state.pool.filter(p => p.source === "picks");
  // Tab counts
  const cNew = state.pool.filter(p => p.source === "bulk").length;
  const cPicks = state.pool.filter(p => p.source === "picks").length;
  document.getElementById("tAll").textContent = state.pool.length;
  document.getElementById("tNew").textContent = cNew;
  document.getElementById("tPicks").textContent = cPicks;
  el.innerHTML = "";
  filtered.forEach((post) => {{
    // Find real pool index so drop handlers can locate by identity
    const realIdx = state.pool.indexOf(post);
    const c = document.createElement("div");
    c.className = "pool-card";
    c.draggable = true;
    c.dataset.source = "pool";
    c.dataset.idx = realIdx;
    c.innerHTML = `
      <img src="${{resolveUrl(post)}}" loading="lazy">
      <div class="info">
        <div class="caption">${{(post.caption_preview || "").replace(/</g, "&lt;")}}</div>
        <div class="tag">${{post.source || "new"}}</div>
      </div>
    `;
    c.addEventListener("dragstart", (e) => {{
      e.dataTransfer.setData("text/plain", JSON.stringify({{ from: "pool", idx: realIdx }}));
    }});
    el.appendChild(c);
  }});
  document.getElementById("sPool").textContent = state.pool.length;
}}

function renderFeed() {{
  const el = document.getElementById("feed");
  el.innerHTML = "";
  state.slots.forEach((slot, idx) => {{
    const div = document.createElement("div");
    div.className = "slot";
    div.dataset.idx = idx;
    if (idx === state.selectedIdx) div.classList.add("selected");
    if (slot.post) {{
      div.classList.add("status-" + (slot.post.status || "accepted"));
      if (slot.post.carousel) div.classList.add("carousel");
      div.innerHTML = `
        <img src="${{resolveUrl(slot.post)}}" loading="lazy">
        <div class="date-badge">${{formatDate(slot.date, slot.dow, slot.time)}}</div>
        ${{slot.post.source && slot.post.source !== "scheduled" ? '<div class="source-badge">' + slot.post.source.toUpperCase() + '</div>' : ""}}
      `;
      div.draggable = true;
      div.addEventListener("dragstart", (e) => {{
        e.dataTransfer.setData("text/plain", JSON.stringify({{ from: "slot", idx }}));
      }});
      div.addEventListener("click", (e) => {{
        if (!slot.post) return;
        state.selectedIdx = idx;
        if (!IS_CLIENT_MODE) {{
          const next = {{ accepted: "rejected", rejected: "pending", pending: "accepted" }};
          state.slots[idx].post.status = next[state.slots[idx].post.status || "accepted"];
        }}
        save();
        renderFeed();
        renderInspector();
      }});
      div.addEventListener("contextmenu", (e) => {{
        e.preventDefault();
        if (!slot.post) return;
        if (IS_CLIENT_MODE) return;
        state.slots[idx].post.carousel = !state.slots[idx].post.carousel;
        save();
        renderFeed();
        renderInspector();
      }});
    }} else {{
      div.classList.add("empty");
      div.innerHTML = `<div class="date-badge">${{formatDate(slot.date, slot.dow, slot.time)}}</div>`;
      div.addEventListener("click", () => {{
        state.selectedIdx = idx;
        save();
        renderFeed();
        renderInspector();
      }});
    }}
    div.addEventListener("dragover", (e) => {{
      e.preventDefault();
      div.classList.add("drag-over");
    }});
    div.addEventListener("dragleave", () => div.classList.remove("drag-over"));
    div.addEventListener("drop", (e) => {{
      e.preventDefault();
      div.classList.remove("drag-over");
      const data = JSON.parse(e.dataTransfer.getData("text/plain"));
      handleDrop(data, idx);
    }});
    el.appendChild(div);
  }});
  updateStats();
}}

function handleDrop(drag, targetIdx) {{
  state.selectedIdx = targetIdx;
  if (drag.from === "pool") {{
    if (IS_CLIENT_MODE) return;
    const post = state.pool[drag.idx];
    if (!post) return;
    // Remove from pool
    state.pool.splice(drag.idx, 1);
    // Evict target slot's current post BACK to pool (top)
    const evicted = state.slots[targetIdx].post;
    if (evicted) state.pool.unshift(evicted);
    // Place new post in slot
    state.slots[targetIdx].post = post;
    post.status = post.status || "pending";
  }} else if (drag.from === "slot") {{
    if (drag.idx === targetIdx) return;
    // SWAP the two slot posts (dates stay)
    const a = state.slots[drag.idx].post;
    const b = state.slots[targetIdx].post;
    state.slots[drag.idx].post = b;
    state.slots[targetIdx].post = a;
  }}
  save();
  renderFeed();
  renderPool();
  renderInspector();
}}

function ensurePostDefaults(post) {{
  if (!post) return;
  post.dish_name = post.dish_name || post.caption_preview || post.filename || post.id || "";
  post.cta = post.cta || "Order online or reserve your table.";
  post.crop = post.crop || {{ mode: "auto", aspect: "4:5", width: 1080, height: 1350 }};
}}

function setStatus(status) {{
  const slot = state.slots[state.selectedIdx];
  if (!slot || !slot.post) return;
  slot.post.status = status;
  save();
  renderFeed();
  renderInspector();
}}

function updateSelectedField(field, value) {{
  const slot = state.slots[state.selectedIdx];
  if (!slot || !slot.post) return;
  ensurePostDefaults(slot.post);
  slot.post[field] = value;
  save();
}}

function updateClientNote(value) {{
  const slot = state.slots[state.selectedIdx];
  if (!slot || !slot.post) return;
  slot.post.client_note = value;
  save();
}}

function setCropMode(mode) {{
  const slot = state.slots[state.selectedIdx];
  if (!slot || !slot.post) return;
  ensurePostDefaults(slot.post);
  slot.post.crop.mode = mode;
  save();
  renderInspector();
}}

function renderInspector() {{
  const el = document.getElementById("inspector");
  const slot = state.slots[state.selectedIdx];
  if (!slot || !slot.post) {{
    el.innerHTML = `<div class="inspector-empty">Select a filled feed cell to edit caption, CTA, status, and crop export settings.</div>`;
    return;
  }}
  const post = slot.post;
  ensurePostDefaults(post);
  const status = post.status || "accepted";
  const cropMode = (post.crop && post.crop.mode) || "auto";
  const safe = (s) => String(s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
  const clientIntro = IS_CLIENT_MODE ? `
    <div class="suggest-note">Review this week's posts, edit caption suggestions, or drag posts into a better order. Changes are sent as suggestions for Savora approval.</div>
  ` : "";
  const statusControls = IS_CLIENT_MODE ? "" : `
    <div class="field">
      <label>Status</label>
      <div class="segmented">
        <button class="${{status === "accepted" ? "active" : ""}}" onclick="setStatus('accepted')">Accept</button>
        <button class="${{status === "pending" ? "active" : ""}}" onclick="setStatus('pending')">Hold</button>
        <button class="${{status === "rejected" ? "active" : ""}}" onclick="setStatus('rejected')">Reject</button>
      </div>
    </div>
  `;
  const cropControls = IS_CLIENT_MODE ? "" : `
    <div class="field">
      <label>Instagram crop export</label>
      <div class="segmented">
        <button class="${{cropMode === "auto" ? "active" : ""}}" onclick="setCropMode('auto')">Auto 4:5</button>
        <button class="${{cropMode === "manual" ? "active" : ""}}" onclick="setCropMode('manual')">Manual</button>
        <button class="${{cropMode === "none" ? "active" : ""}}" onclick="setCropMode('none')">Raw</button>
      </div>
    </div>
  `;
  const clientNotes = IS_CLIENT_MODE ? `
    <div class="field">
      <label>Note to Savora</label>
      <textarea oninput="updateClientNote(this.value)">${{safe(post.client_note || "")}}</textarea>
    </div>
  ` : "";
  el.innerHTML = `
    ${{clientIntro}}
    <div class="preview-card"><img src="${{resolveUrl(post)}}" loading="lazy"></div>
    <div class="field">
      <label>Schedule</label>
      <input value="${{safe(formatDate(slot.date, slot.dow, slot.time) + " · " + slot.time)}}" disabled>
    </div>
    <div class="field">
      <label>Post / dish name</label>
      <input value="${{safe(post.dish_name)}}" oninput="updateSelectedField('dish_name', this.value)">
    </div>
    <div class="field">
      <label>Caption</label>
      <textarea oninput="updateSelectedField('caption', this.value)">${{safe(post.caption || "")}}</textarea>
    </div>
    <div class="field">
      <label>CTA footer</label>
      <input value="${{safe(post.cta)}}" oninput="updateSelectedField('cta', this.value)">
    </div>
    ${{clientNotes}}
    ${{statusControls}}
    ${{cropControls}}
    <div class="micro-grid">
      <div class="field"><label>Source</label><input value="${{safe(post.source || "")}}" disabled></div>
      <div class="field"><label>Carousel</label><input value="${{post.carousel ? "Yes" : "No"}}" disabled></div>
    </div>
  `;
}}

function updateStats() {{
  let filled = 0, accepted = 0, rejected = 0;
  state.slots.forEach(s => {{
    if (s.post) {{
      filled++;
      const st = s.post.status || "accepted";
      if (st === "accepted") accepted++;
      else if (st === "rejected") rejected++;
    }}
  }});
  document.getElementById("sSlots").textContent = state.slots.length;
  document.getElementById("sFilled").textContent = filled;
  document.getElementById("sAccepted").textContent = accepted;
  document.getElementById("sRejected").textContent = rejected;
}}

function resetSession() {{
  if (!confirm("Reset entire session? All status + swap changes will be lost.")) return;
  state.slots = JSON.parse(JSON.stringify(INITIAL_SLOTS));
  state.pool = [...INITIAL_POOL_NEW, ...INITIAL_POOL_PICKS];
  state.selectedIdx = 0;
  save();
  renderAll();
}}

function clearStatuses() {{
  state.slots.forEach(s => {{
    if (s.post && s.post.source !== "scheduled") s.post.status = "pending";
  }});
  save();
  renderAll();
}}

function csvEscape(value) {{
  const text = String(value || "");
  return `"${{text.replace(/"/g, '""')}}"`;
}}

function vistaDateTime(slot) {{
  const [year, month, day] = slot.date.split("-");
  const [hourRaw, minute] = slot.time.split(":").map(Number);
  const suffix = hourRaw >= 12 ? "pm" : "am";
  const hour = hourRaw % 12 || 12;
  return `${{year}}-${{month}}-${{day}} ${{hour}}:${{String(minute).padStart(2, "0")}} ${{suffix}}`;
}}

function isCloudinaryUrl(url) {{
  return url.includes("res.cloudinary.com/") && url.includes("/image/upload/");
}}

function cloudinaryCropTransform(crop) {{
  const mode = ((crop && crop.mode) || "auto").toLowerCase();
  if (mode === "none") return "";
  const width = crop && crop.width ? Number(crop.width) : 1080;
  const height = crop && crop.height ? Number(crop.height) : 1350;
  if (mode === "manual" && crop && crop.x !== undefined && crop.y !== undefined && crop.w && crop.h) {{
    return `c_crop,x_${{Number(crop.x)}},y_${{Number(crop.y)}},w_${{Number(crop.w)}},h_${{Number(crop.h)}}/c_fill,w_${{width}},h_${{height}}`;
  }}
  const gravity = (crop && crop.gravity) || "auto";
  const aspect = (crop && crop.aspect) || "4:5";
  return `c_fill,g_${{gravity}},ar_${{aspect}},w_${{width}},h_${{height}}`;
}}

function cropUrlForCsv(url, crop) {{
  if (!url || !isCloudinaryUrl(url)) return url;
  const transform = cloudinaryCropTransform(crop);
  if (!transform) return url;
  return url.replace("/image/upload/", `/image/upload/${{transform}}/`);
}}

function captionForCsv(post) {{
  ensurePostDefaults(post);
  const caption = String(post.caption || post.caption_preview || "").trim();
  const cta = String(post.cta || "").trim();
  if (!cta) return caption;
  if (caption.toLowerCase().includes(cta.toLowerCase())) return caption;
  return `${{caption}}\n\n${{cta}}`;
}}

function exportVistaCsv() {{
  const rows = [];
  let localUrlCount = 0;
  state.slots.forEach((slot) => {{
    const post = slot.post;
    if (!post || (post.status || "accepted") !== "accepted") return;
    ensurePostDefaults(post);
    const urls = Array.isArray(post.urls) && post.urls.length ? post.urls : [post.url];
    urls.forEach((rawUrl) => {{
      if (!rawUrl) return;
      if (!String(rawUrl).startsWith("http")) localUrlCount++;
      rows.push([
        captionForCsv(post),
        "image",
        cropUrlForCsv(String(rawUrl), post.crop),
        vistaDateTime(slot),
      ]);
    }});
  }});
  const csv = rows.map(row => row.map(csvEscape).join(",")).join("\n") + "\n";
  const blob = new Blob([csv], {{ type: "text/csv;charset=utf-8" }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "vista_" + BRAND + "_" + Date.now() + ".csv";
  a.click();
  URL.revokeObjectURL(url);
  if (localUrlCount) {{
    alert("CSV exported, but " + localUrlCount + " local image URL(s) still need the Python apply_feed.py path so they can upload to Cloudinary first.");
  }}
}}

function originalSlotForPost(postId) {{
  if (!postId) return null;
  return INITIAL_SLOTS.find(slot => slot.post && slot.post.id === postId) || null;
}}

function exportClientSuggestions() {{
  const suggestions = [];
  state.slots.forEach((slot) => {{
    const post = slot.post;
    if (!post) return;
    ensurePostDefaults(post);
    const original = originalSlotForPost(post.id);
    const scheduleChanged = !!original && (original.date !== slot.date || original.time !== slot.time);
    const originalPost = original && original.post ? original.post : {{}};
    const captionChanged = String(post.caption || "") !== String(originalPost.caption || "");
    const ctaChanged = !!post.cta && String(post.cta || "") !== String(originalPost.cta || "");
    const hasNote = !!String(post.client_note || "").trim();
    if (!scheduleChanged && !captionChanged && !ctaChanged && !hasNote) return;
    suggestions.push({{
      post_id: post.id,
      dish_name: post.dish_name || post.caption_preview || post.filename || "",
      current_date: slot.date,
      current_time: slot.time,
      original_date: original ? original.date : null,
      original_time: original ? original.time : null,
      suggested_caption: post.caption || "",
      suggested_cta: post.cta || "",
      client_note: post.client_note || "",
      schedule_changed: scheduleChanged,
      caption_changed: captionChanged,
      cta_changed: ctaChanged,
    }});
  }});
  const payload = {{
    brand: BRAND,
    mode: "client",
    exported_at: new Date().toISOString(),
    suggestion_count: suggestions.length,
    suggestions,
  }};
  const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: "application/json" }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "suggestions_" + BRAND + "_" + Date.now() + ".json";
  a.click();
  URL.revokeObjectURL(url);
}}

function exportFeed() {{
  const payload = {{
    brand: BRAND,
    exported_at: new Date().toISOString(),
    slot_count: state.slots.length,
    slots: state.slots.map(s => ({{
      date: s.date,
      dow: s.dow,
      time: s.time,
      scheduled_at: s.date + " " + s.time,
      post: s.post ? {{
        source: s.post.source,
        id: s.post.id,
        url: s.post.url,
        urls: s.post.urls || null,
        dish_name: s.post.dish_name || s.post.caption_preview || s.post.filename || s.post.id || "",
        caption: s.post.caption,
        caption_preview: s.post.caption_preview,
        cta: s.post.cta || "Order online or reserve your table.",
        crop: s.post.crop || {{ mode: "auto", aspect: "4:5", width: 1080, height: 1350 }},
        batch: s.post.batch || null,
        filename: s.post.filename || null,
        status: s.post.status || "accepted",
        carousel: !!s.post.carousel,
      }} : null,
    }})),
    pool_remaining: state.pool,
  }};
  const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: "application/json" }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "feed_" + BRAND + "_" + Date.now() + ".json";
  a.click();
  URL.revokeObjectURL(url);
}}

function switchTab(tab) {{
  state.activeTab = tab;
  document.querySelectorAll(".pool-tabs button").forEach(b => {{
    b.classList.toggle("active", b.dataset.tab === tab);
  }});
  renderPool();
}}

function renderAll() {{
  renderFeed();
  renderPool();
  renderInspector();
}}

function applyModeUi() {{
  const modePill = document.getElementById("modePill");
  const modeKicker = document.getElementById("modeKicker");
  if (IS_CLIENT_MODE) {{
    modePill.textContent = "Client review";
    modeKicker.textContent = "Upcoming posts · caption edits · schedule suggestions";
  }} else {{
    modePill.textContent = "Internal";
    modeKicker.textContent = "Today → Aug 31 · Mon/Tue/Thu/Fri slots · Drag to swap";
  }}
}}

document.querySelectorAll(".pool-tabs button").forEach(b => {{
  b.addEventListener("click", () => switchTab(b.dataset.tab));
}});

applyModeUi();
renderAll();
</script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brand", required=True, choices=list(BRAND_CONFIG.keys()))
    parser.add_argument("--output", default=None)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()

    cfg = BRAND_CONFIG[args.brand]
    scheduled = load_scheduled(args.brand)
    bulk = load_unscheduled(args.brand)
    picks = load_picks(args.brand)

    slots, leftover_sched, remaining_new = build_slots(args.brand, scheduled, bulk + picks)

    out_path = pathlib.Path(args.output) if args.output else (
        ROOT / "OUTPUT" / f"feed_composer_{args.brand}.html"
    )

    # Separate remaining bulk vs picks (by id prefix)
    remaining_bulk = [p for p in remaining_new if p.get("source") == "bulk"]
    remaining_picks = [p for p in remaining_new if p.get("source") == "picks"]
    # Prepend leftover undated scheduled to evicted pool for visibility
    # (rendered under "Evicted" tab since user shouldn't drop Vista ones into new dates unless they want to)

    html = HTML.format(
        brand=args.brand,
        brand_name=cfg["name"],
        slot_count=len(slots),
        slots_json=json.dumps(slots),
        pool_new_json=json.dumps(remaining_bulk),
        pool_picks_json=json.dumps(remaining_picks),
        **cfg["theme"],
    )
    out_path.write_text(html, encoding="utf-8")
    print(f"[build] {out_path}")
    print(f"        slots: {len(slots)}  pool-new: {len(remaining_bulk)}  pool-picks: {len(remaining_picks)}")

    if not args.no_open:
        subprocess.Popen(["open", f"http://localhost:8765/{out_path.name}"])


if __name__ == "__main__":
    main()
