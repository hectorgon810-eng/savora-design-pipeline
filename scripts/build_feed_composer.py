#!/usr/bin/env python3
"""
Feed Composer v2 — Slot-based IG feed scheduler + drag-drop composer.

Auto-assigns Tue/Wed dates from TODAY → Aug 31 to every post (existing scheduled
posts keep their original dates; new generated posts + picks get auto-slotted
into the first available Tue/Wed).

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
        "post_time_tue": "17:00",
        "post_time_wed": "17:30",
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
        "post_time_tue": "17:30",
        "post_time_wed": "18:00",
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
        "post_time_tue": "17:00",
        "post_time_wed": "17:30",
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
        try:
            dt = datetime.strptime(p["original_date"].split(" ")[0], "%Y-%m-%d").date()
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
        time_str = cfg["post_time_tue"]
        # Priority 1: Vista-scheduled post matching this exact date
        post = None
        if d in scheduled_by_date and scheduled_by_date[d]:
            post = scheduled_by_date[d].pop(0)
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
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ min-height: 100dvh; background: var(--ground); color: var(--ink); font-family: var(--font-ui); overflow: hidden; }}
body {{ display: flex; flex-direction: column; }}

header {{
  padding: 14px 22px;
  display: flex; justify-content: space-between; align-items: baseline;
  gap: 20px;
  border-bottom: 1px solid var(--hairline);
  background: color-mix(in oklab, var(--ground) 94%, transparent);
  z-index: 10;
}}
header .wordmark {{ font-family: var(--font-hero); font-style: italic; font-size: 24px; color: var(--ink); letter-spacing: -0.01em; }}
header .wordmark em {{ font-style: normal; font-weight: 600; }}
header .kicker {{ font-size: 10px; color: var(--muted); letter-spacing: 0.22em; text-transform: uppercase; margin-top: 4px; }}
header .stats {{ display: flex; gap: 14px; font-size: 11px; color: var(--muted); letter-spacing: 0.06em; text-transform: uppercase; }}
header .stats b {{ color: var(--ink); font-weight: 600; margin-left: 4px; font-variant-numeric: tabular-nums; }}

main {{
  flex: 1;
  display: grid;
  grid-template-columns: 320px 1fr;
  grid-template-rows: minmax(0, 1fr);
  gap: 16px;
  padding: 16px;
  overflow: hidden;
  min-height: 0;
  height: calc(100dvh - 140px); /* explicit bound so feed-wrap definitely scrolls */
}}

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
</style>
</head>
<body>
<header>
  <div>
    <div class="wordmark"><em>{brand_name}</em> · Feed Scheduler</div>
    <div class="kicker">Today → Aug 31 · Tue/Wed slots · Drag to swap</div>
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
  <div class="pane">
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
    <div class="meta">IG 3-col preview · {slot_count} Tue/Wed slots</div>
    <div class="feed-wrap"><div class="feed" id="feed"></div></div>
  </div>
</main>

<footer>
  <button class="action" onclick="resetSession()">Reset session</button>
  <button class="action" onclick="clearStatuses()">Clear statuses</button>
  <button class="action primary" onclick="exportFeed()">Export feed.json</button>
</footer>

<script>
const INITIAL_SLOTS = {slots_json};
const INITIAL_POOL_NEW = {pool_new_json};
const INITIAL_POOL_PICKS = {pool_picks_json};
const BRAND = "{brand}";
const STORAGE_KEY = "feedv3_" + BRAND + "_" + INITIAL_SLOTS.length;

let state = {{
  slots: [],          // [{{date, dow, time, post: {{...}} | null}}]
  pool: [],           // unified content pool — everything not in a slot
  activeTab: "all",
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
        const next = {{ accepted: "rejected", rejected: "pending", pending: "accepted" }};
        state.slots[idx].post.status = next[state.slots[idx].post.status || "accepted"];
        save();
        renderFeed();
      }});
      div.addEventListener("contextmenu", (e) => {{
        e.preventDefault();
        if (!slot.post) return;
        state.slots[idx].post.carousel = !state.slots[idx].post.carousel;
        save();
        renderFeed();
      }});
    }} else {{
      div.classList.add("empty");
      div.innerHTML = `<div class="date-badge">${{formatDate(slot.date, slot.dow, slot.time)}}</div>`;
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
  if (drag.from === "pool") {{
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
  save();
  renderAll();
}}

function clearStatuses() {{
  state.slots.forEach(s => {{
    if (s.post && s.post.source !== "scheduled") s.post.status = "pending";
  }});
  save();
  renderFeed();
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
        caption: s.post.caption,
        caption_preview: s.post.caption_preview,
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
}}

document.querySelectorAll(".pool-tabs button").forEach(b => {{
  b.addEventListener("click", () => switchTab(b.dataset.tab));
}});

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
