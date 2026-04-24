#!/usr/bin/env python3
"""
Build a per-brand themed review page. Three themes matching each brand's world:
  blue_mezcal  → editorial cobalt + bone-cream with Fraunces serif
  jackson_house → charred-black + brass-foil heritage with Playfair SC
  el_azteca    → pastel-saturated maximalist with Alfa Slab chunky caps

Taste-skill discipline applied:
  - CSS custom properties per theme (single template, themed per brand)
  - Hardware-accelerated transforms only (no layout thrash)
  - Spring-like cubic-bezier easing (0.16, 1, 0.3, 1)
  - No emojis. No Inter. No neon glows. No pure #000.
  - Editorial type hierarchy with real hierarchy via weight + italic contrast
  - Max 1 accent color per theme

Controls (all themes):
    1-5     star rating
    0 / ←   reject
    →       5-star shortcut
    space   skip
    Z       undo
    E       export / summary
    R       reset session
    ? / H   toggle help

Usage:
    python3 scripts/build_tinder_review.py --brand blue_mezcal
    python3 scripts/build_tinder_review.py --brand jackson_house --include JH-W-
    python3 scripts/build_tinder_review.py --brand el_azteca --include BULK-
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


BRAND_NAMES = {
    "blue_mezcal": "Blue Mezcal",
    "jackson_house": "Jackson House",
    "azteca": "El Azteca",
    "savora": "Savora",
}


THEMES = {
    "blue_mezcal": {
        "font_hero": "'Fraunces', serif",
        "font_ui":   "'Outfit', sans-serif",
        "google_fonts": "family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400;1,9..144,600&family=Outfit:wght@400;500;600;700",
        "ink":         "#1E3A8A",
        "ink_soft":    "#2E4A9A",
        "ground":      "#F3ECD8",
        "ground_soft": "#E8DBB8",
        "accent":      "#C9A24B",
        "muted":       "#8a7c5c",
        "hairline":    "rgba(30, 58, 138, 0.18)",
        "card_shadow": "0 20px 50px -18px rgba(30, 58, 138, 0.22)",
        "body_bg":     "radial-gradient(ellipse at top, #F7F0DC 0%, #EADEC0 100%)",
        "grain":       "0.03",
    },
    "jackson_house": {
        "font_hero": "'Playfair Display', serif",
        "font_ui":   "'Outfit', sans-serif",
        "google_fonts": "family=Playfair+Display:ital,wght@0,500;0,700;1,500;1,700&family=Outfit:wght@400;500;600;700",
        "ink":         "#F2EADF",
        "ink_soft":    "#C9A24B",
        "ground":      "#0C0B0A",
        "ground_soft": "#1A1612",
        "accent":      "#C9A24B",
        "muted":       "#7a6e55",
        "hairline":    "rgba(201, 162, 75, 0.22)",
        "card_shadow": "0 24px 56px -18px rgba(0, 0, 0, 0.65)",
        "body_bg":     "radial-gradient(ellipse at top, #13100d 0%, #0a0908 100%)",
        "grain":       "0.05",
    },
    "azteca": {
        "font_hero": "'Alfa Slab One', serif",
        "font_ui":   "'Outfit', sans-serif",
        "google_fonts": "family=Alfa+Slab+One&family=Outfit:wght@400;500;600;700",
        "ink":         "#18140f",
        "ink_soft":    "#E63946",
        "ground":      "#F8F2DF",
        "ground_soft": "#F5E8D0",
        "accent":      "#E63946",
        "muted":       "#7a6e55",
        "hairline":    "rgba(230, 57, 70, 0.24)",
        "card_shadow": "0 22px 48px -18px rgba(230, 57, 70, 0.25)",
        "body_bg":     "radial-gradient(ellipse at top left, #FFE4F1 0%, #F8F2DF 55%, #E1F5F4 100%)",
        "grain":       "0.025",
    },
    "savora": {
        "font_hero": "'Fraunces', serif",
        "font_ui":   "'Geist', sans-serif",
        "google_fonts": "family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400;1,9..144,600&family=Geist:wght@400;500;600;700",
        "ink":         "#F2EFEB",
        "ink_soft":    "#D9D4CE",
        "ground":      "#00060B",
        "ground_soft": "#062423",
        "accent":      "#C2612C",
        "muted":       "#7B9693",
        "hairline":    "rgba(43, 140, 131, 0.28)",
        "card_shadow": "0 26px 60px -18px rgba(194, 97, 44, 0.22)",
        "body_bg":     "radial-gradient(ellipse at top, #062423 0%, #010908 55%, #00060B 100%)",
        "grain":       "0.055",
    },
}


def collect_images(brand: str, include: str | None) -> list[dict]:
    base = ROOT / "OUTPUT" / "nano_banana" / brand
    if not base.exists():
        sys.exit(f"No such folder: {base}")
    out = []
    for folder in sorted(base.iterdir()):
        if not folder.is_dir():
            continue
        if include and include not in folder.name:
            continue
        for png in sorted(folder.glob("variation_*.png")):
            # Relative to the HTML location (OUTPUT/) so relative URLs work
            # over an HTTP server rooted at OUTPUT/
            rel_from_html = str(png.relative_to(ROOT / "OUTPUT"))
            out.append({
                "brand": brand,
                "batch": folder.name,
                "filename": png.name,
                "path": rel_from_html,
                "rel": str(png.relative_to(ROOT)),
            })
    return out


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Review · {brand_name}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{google_fonts}&display=swap" rel="stylesheet">
<style>
:root {{
  --font-hero: {font_hero};
  --font-ui: {font_ui};
  --ink: {ink};
  --ink-soft: {ink_soft};
  --ground: {ground};
  --ground-soft: {ground_soft};
  --accent: {accent};
  --muted: {muted};
  --hairline: {hairline};
  --card-shadow: {card_shadow};
  --body-bg: {body_bg};
  --grain: {grain};
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
  --pill: 999px;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-user-select: none; user-select: none; }}
html, body {{ min-height: 100dvh; background: var(--ground); color: var(--ink); font-family: var(--font-ui); overflow: hidden; }}
body {{
  display: flex; flex-direction: column;
  background: var(--body-bg);
  position: relative;
}}

/* Paper grain pointer-free overlay */
body::before {{
  content: "";
  position: fixed; inset: 0;
  background-image: url("data:image/svg+xml;utf8,<svg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 {grain} 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
  pointer-events: none; z-index: 50; opacity: 1; mix-blend-mode: multiply;
}}

/* Header */
header {{
  padding: 18px 28px;
  display: flex; justify-content: space-between; align-items: baseline;
  gap: 24px;
  border-bottom: 1px solid var(--hairline);
  background: color-mix(in oklab, var(--ground) 92%, transparent);
  backdrop-filter: blur(8px);
  z-index: 10; position: relative;
}}
header .wordmark {{
  font-family: var(--font-hero);
  font-weight: 400;
  font-style: italic;
  font-size: 28px;
  color: var(--ink);
  letter-spacing: -0.01em;
  line-height: 1;
}}
header .wordmark em {{ font-style: normal; font-weight: 600; }}
header .kicker {{
  font-family: var(--font-ui);
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  color: var(--muted);
  margin-top: 6px;
}}

header .histogram {{ display: flex; gap: 14px; align-items: center; font-size: 11px; color: var(--muted); letter-spacing: 0.06em; text-transform: uppercase; }}
header .histogram .bucket {{ display: inline-flex; align-items: center; gap: 6px; }}
header .histogram .bucket b {{ color: var(--ink); font-family: var(--font-ui); font-weight: 600; letter-spacing: 0; text-transform: none; font-size: 12px; font-variant-numeric: tabular-nums; }}
header .histogram .reject b {{ color: var(--accent); }}

.progress {{
  height: 2px; background: var(--hairline);
  transform: translate3d(0, 0, 0);
}}
.progress-bar {{
  height: 100%; width: 0%;
  background: var(--accent);
  transition: width 0.5s var(--ease);
  transform-origin: left;
}}

/* Main stage */
main {{
  flex: 1;
  display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
  padding: 36px 24px 160px;
}}

.card {{
  position: relative;
  max-width: min(78vh, 560px);
  transition: transform 0.38s var(--ease), opacity 0.38s var(--ease);
  transform: translate3d(0, 0, 0);
  will-change: transform, opacity;
}}
.card img {{
  display: block;
  max-width: min(78vh, 560px);
  max-height: calc(100dvh - 300px);
  width: auto; height: auto;
  border-radius: 10px;
  box-shadow: var(--card-shadow);
  background: var(--ground-soft);
}}
.card .meta {{
  margin-top: 14px; text-align: center;
  color: var(--muted);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}}
.card .meta .batch {{ color: var(--ink); font-weight: 600; letter-spacing: 0.12em; }}

.card .rating-badge {{
  position: absolute; top: 16px; right: 16px;
  padding: 6px 14px;
  background: var(--ink);
  color: var(--ground);
  font-family: var(--font-hero); font-style: italic;
  font-size: 14px;
  border-radius: var(--pill);
  opacity: 0;
  transform: translate3d(0, -4px, 0) scale(0.95);
  transition: opacity 0.2s var(--ease), transform 0.2s var(--ease);
}}
.card[data-rated="true"] .rating-badge {{ opacity: 1; transform: translate3d(0, 0, 0) scale(1); }}

.card.slide-right {{ transform: translate3d(140vw, 0, 0) rotate(22deg) !important; opacity: 0 !important; }}
.card.slide-left  {{ transform: translate3d(-140vw, 0, 0) rotate(-22deg) !important; opacity: 0 !important; }}
.card.slide-up    {{ transform: translate3d(0, -120vh, 0) !important; opacity: 0 !important; }}

.empty {{
  font-family: var(--font-hero); font-style: italic;
  font-size: 28px; color: var(--ink);
  letter-spacing: -0.01em;
  opacity: 0.7;
  text-align: center;
}}
.empty small {{
  display: block; font-family: var(--font-ui); font-style: normal;
  font-weight: 500; font-size: 11px;
  color: var(--muted);
  letter-spacing: 0.22em; text-transform: uppercase;
  margin-top: 12px;
}}

/* Rating row */
.rating-row {{
  position: fixed; bottom: 88px; left: 50%;
  transform: translate3d(-50%, 0, 0);
  display: flex; gap: 4px;
  padding: 6px;
  background: color-mix(in oklab, var(--ground) 88%, transparent);
  backdrop-filter: blur(10px);
  border: 1px solid var(--hairline);
  border-radius: var(--pill);
  z-index: 20;
}}
.star-btn {{
  background: transparent;
  border: 1px solid transparent;
  color: var(--ink);
  min-width: 72px; height: 48px;
  padding: 0 14px;
  border-radius: 999px;
  cursor: pointer;
  font-family: var(--font-hero);
  font-size: 15px;
  font-weight: 600;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  transition: transform 0.15s var(--ease), background 0.2s var(--ease), color 0.2s var(--ease), border-color 0.2s var(--ease);
  line-height: 1;
}}
.star-btn small {{
  font-family: var(--font-ui); font-style: normal;
  font-size: 8px; font-weight: 600;
  color: var(--muted);
  letter-spacing: 0.18em; text-transform: uppercase;
  margin-top: 4px;
}}
.star-btn:hover {{
  background: var(--ground-soft);
  border-color: var(--hairline);
  transform: translate3d(0, -1px, 0);
}}
.star-btn:active {{ transform: translate3d(0, 1px, 0) scale(0.97); }}

/* Footer actions */
footer {{
  padding: 16px 20px;
  display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;
  border-top: 1px solid var(--hairline);
  background: color-mix(in oklab, var(--ground) 92%, transparent);
  backdrop-filter: blur(10px);
  z-index: 10;
}}
button.action {{
  background: transparent;
  color: var(--ink); opacity: 0.7;
  border: 1px solid var(--hairline);
  padding: 9px 18px;
  font-size: 10px; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase;
  border-radius: 999px;
  cursor: pointer;
  font-family: var(--font-ui);
  transition: opacity 0.2s var(--ease), background 0.2s var(--ease), transform 0.15s var(--ease);
}}
button.action:hover {{
  opacity: 1;
  background: var(--ground-soft);
  transform: translate3d(0, -1px, 0);
}}
button.action:active {{ transform: translate3d(0, 1px, 0) scale(0.98); }}
button.action.export {{
  background: var(--ink); color: var(--ground); opacity: 1;
  border-color: var(--ink);
}}
button.action.export:hover {{
  background: var(--ink-soft); border-color: var(--ink-soft);
}}

/* Shortcuts panel */
.shortcuts {{
  position: fixed; bottom: 150px; right: 20px;
  background: color-mix(in oklab, var(--ground) 94%, transparent);
  backdrop-filter: blur(12px);
  padding: 16px 18px;
  border-radius: 10px;
  border: 1px solid var(--hairline);
  box-shadow: var(--card-shadow);
  font-size: 11px; line-height: 1.8;
  color: var(--muted); letter-spacing: 0.04em;
  max-width: 240px;
  display: none;
  z-index: 30;
}}
.shortcuts.show {{ display: block; }}
.shortcuts b {{ color: var(--ink); text-transform: uppercase; letter-spacing: 0.14em; font-size: 10px; font-weight: 600; }}
.shortcuts kbd {{
  background: var(--ground-soft); color: var(--ink);
  padding: 2px 6px; border-radius: 3px;
  margin: 0 2px; font-family: 'SF Mono', 'Menlo', monospace;
  font-size: 10px; border: 1px solid var(--hairline);
}}

/* Summary modal */
.summary {{
  position: fixed; inset: 0;
  background: color-mix(in oklab, var(--ground) 92%, transparent);
  backdrop-filter: blur(20px);
  display: none;
  flex-direction: column; align-items: center; justify-content: center;
  padding: 40px 24px;
  z-index: 100;
  overflow-y: auto;
}}
.summary.show {{ display: flex; }}
.summary h2 {{
  font-family: var(--font-hero); font-style: italic; font-weight: 400;
  color: var(--ink);
  font-size: 44px;
  letter-spacing: -0.02em;
  margin-bottom: 28px;
}}
.summary h2 em {{ font-style: normal; font-weight: 600; }}

.summary .histogram-big {{
  display: flex; gap: 12px; margin-bottom: 32px; flex-wrap: wrap; justify-content: center;
}}
.summary .histogram-big .bucket {{
  padding: 18px 22px;
  background: color-mix(in oklab, var(--ground) 80%, transparent);
  border: 1px solid var(--hairline);
  border-radius: 8px;
  text-align: center;
  min-width: 96px;
}}
.summary .histogram-big .bucket .label {{
  font-size: 9px; color: var(--muted);
  letter-spacing: 0.22em; text-transform: uppercase;
  font-weight: 600;
}}
.summary .histogram-big .bucket .count {{
  font-family: var(--font-hero);
  font-size: 32px; color: var(--ink);
  font-weight: 600;
  margin-top: 6px;
  font-variant-numeric: tabular-nums;
}}
.summary .histogram-big .reject .count {{ color: var(--accent); }}

.summary .lists {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
  width: min(960px, 92vw);
  margin-bottom: 28px;
}}
.summary .list-col {{
  background: color-mix(in oklab, var(--ground) 86%, transparent);
  border: 1px solid var(--hairline);
  padding: 16px 18px;
  border-radius: 8px;
  max-height: 40vh;
  overflow-y: auto;
}}
.summary .list-col h3 {{
  font-family: var(--font-hero); font-style: italic; font-weight: 400;
  color: var(--ink);
  font-size: 18px; letter-spacing: -0.01em;
  margin-bottom: 12px;
}}
.summary .list-col div {{
  padding: 3px 0;
  font-size: 11px; color: var(--ink);
  font-weight: 500;
  letter-spacing: 0.02em;
  font-family: 'SF Mono', 'Menlo', monospace;
  opacity: 0.85;
}}
.summary .list-col .empty-note {{
  font-family: var(--font-hero); font-style: italic;
  color: var(--muted); font-size: 13px;
}}

.summary .summary-actions {{ display: flex; gap: 10px; }}

@media (max-width: 640px) {{
  header {{ padding: 14px 18px; flex-direction: column; align-items: flex-start; gap: 12px; }}
  header .histogram {{ font-size: 10px; gap: 10px; }}
  main {{ padding: 24px 16px 200px; }}
  .star-btn {{ min-width: 52px; padding: 0 8px; }}
  .rating-row {{ bottom: 120px; }}
  .summary h2 {{ font-size: 30px; }}
}}
</style>
</head>
<body>
<header>
  <div>
    <div class="wordmark"><em>{brand_name}</em> <span style="opacity:0.65">· Review</span></div>
    <div class="kicker">Rate 1–5 · Export at end</div>
  </div>
  <div class="histogram">
    <span class="bucket">5 Star <b id="h5">0</b></span>
    <span class="bucket">4 <b id="h4">0</b></span>
    <span class="bucket">3 <b id="h3">0</b></span>
    <span class="bucket">2 <b id="h2">0</b></span>
    <span class="bucket">1 <b id="h1">0</b></span>
    <span class="bucket reject">Reject <b id="hReject">0</b></span>
    <span class="bucket">Skip <b id="hSkip">0</b></span>
    <span class="bucket">· <b id="hCount">0 / {total}</b></span>
  </div>
</header>

<div class="progress"><div class="progress-bar" id="progressBar"></div></div>

<main id="main"></main>

<div class="rating-row">
  <button class="star-btn" onclick="rate(1)">1<small>Meh</small></button>
  <button class="star-btn" onclick="rate(2)">2<small>Ok</small></button>
  <button class="star-btn" onclick="rate(3)">3<small>Usable</small></button>
  <button class="star-btn" onclick="rate(4)">4<small>Great</small></button>
  <button class="star-btn" onclick="rate(5)">5<small>Best</small></button>
</div>

<div class="shortcuts" id="shortcuts">
  <b>Rating</b><br>
  <kbd>1</kbd>–<kbd>5</kbd> star rating<br>
  <kbd>0</kbd> / <kbd>←</kbd> reject<br>
  <kbd>→</kbd> 5-star<br>
  <kbd>space</kbd> skip<br>
  <br>
  <b>Session</b><br>
  <kbd>Z</kbd> undo last<br>
  <kbd>E</kbd> export<br>
  <kbd>R</kbd> reset<br>
  <kbd>?</kbd> toggle help
</div>

<footer>
  <button class="action" onclick="decide('rejected')">Reject · ←</button>
  <button class="action" onclick="decide('skipped')">Skip · Space</button>
  <button class="action" onclick="undo()">Undo · Z</button>
  <button class="action" onclick="toggleShortcuts()">? Shortcuts</button>
  <button class="action export" onclick="showSummary()">Export · E</button>
</footer>

<div class="summary" id="summary">
  <h2><em>Session</em> summary</h2>
  <div class="histogram-big">
    <div class="bucket"><div class="label">Five Star</div><div class="count" id="s5">0</div></div>
    <div class="bucket"><div class="label">Four</div><div class="count" id="s4">0</div></div>
    <div class="bucket"><div class="label">Three</div><div class="count" id="s3">0</div></div>
    <div class="bucket"><div class="label">Two</div><div class="count" id="s2">0</div></div>
    <div class="bucket"><div class="label">One</div><div class="count" id="s1">0</div></div>
    <div class="bucket reject"><div class="label">Reject</div><div class="count" id="sReject">0</div></div>
    <div class="bucket"><div class="label">Skip</div><div class="count" id="sSkip">0</div></div>
  </div>
  <div class="lists">
    <div class="list-col"><h3>5 star — best fit</h3><div id="list5"></div></div>
    <div class="list-col"><h3>4 star — great</h3><div id="list4"></div></div>
    <div class="list-col"><h3>3 star — usable</h3><div id="list3"></div></div>
  </div>
  <div class="summary-actions">
    <button class="action export" onclick="download()">Download approved.json</button>
    <button class="action" onclick="closeSummary()">Back to review</button>
  </div>
</div>

<script>
// Error surface — if anything explodes, show it on screen
window.addEventListener("error", (e) => {{
  const bar = document.createElement("div");
  bar.style.cssText = "position:fixed;top:0;left:0;right:0;background:#b00020;color:#fff;padding:10px 16px;z-index:9999;font:14px monospace;";
  bar.textContent = "JS ERROR: " + e.message + " @ " + e.filename + ":" + e.lineno;
  document.body.appendChild(bar);
}});
const IMAGES = {images_json};
const BRAND = "{brand}";
// Key includes image count so new batches reset state
// Bump version when batch content changes materially
const STORAGE_KEY = "review_" + BRAND + "_v5_" + IMAGES.length;

let state = {{ index: 0, decisions: [] }};

try {{
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) state = JSON.parse(saved);
}} catch (e) {{}}

function save() {{
  try {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }} catch (e) {{}}
}}

function render() {{
  const main = document.getElementById("main");
  main.innerHTML = "";
  if (state.index >= IMAGES.length) {{
    main.innerHTML = '<div class="empty">All done.<small>Press E to export</small></div>';
    updateStats();
    return;
  }}
  const img = IMAGES[state.index];
  const card = document.createElement("div");
  card.className = "card";
  card.id = "currentCard";
  card.innerHTML = `
    <div style="position:relative">
      <img src="${{img.path}}" alt="${{img.filename}}" loading="eager">
      <div class="rating-badge" id="ratingBadge"></div>
    </div>
    <div class="meta"><span class="batch">${{img.batch}}</span> · ${{img.filename}}</div>
  `;
  main.appendChild(card);
  updateStats();
}}

function updateStats() {{
  const h = {{ s1:0, s2:0, s3:0, s4:0, s5:0, rejected:0, skipped:0 }};
  state.decisions.forEach(d => {{
    if (d.decision === "rated") h["s" + d.rating]++;
    else if (d.decision === "rejected") h.rejected++;
    else if (d.decision === "skipped") h.skipped++;
  }});
  ["h1","h2","h3","h4","h5"].forEach((id, i) => {{ document.getElementById(id).textContent = h["s" + (i+1)]; }});
  document.getElementById("hReject").textContent = h.rejected;
  document.getElementById("hSkip").textContent = h.skipped;
  document.getElementById("hCount").textContent = state.index + " / " + IMAGES.length;
  document.getElementById("progressBar").style.width = (100 * state.index / IMAGES.length) + "%";
}}

function rate(stars) {{
  if (state.index >= IMAGES.length) return;
  const card = document.getElementById("currentCard");
  const badge = document.getElementById("ratingBadge");
  if (badge) badge.textContent = stars + " star" + (stars === 1 ? "" : "s");
  if (card) {{
    card.setAttribute("data-rated", "true");
    card.classList.add(stars >= 4 ? "slide-right" : stars === 3 ? "slide-up" : "slide-left");
  }}
  state.decisions.push({{ idx: state.index, decision: "rated", rating: stars }});
  state.index++;
  save();
  setTimeout(render, 380);
}}

function decide(decision) {{
  if (state.index >= IMAGES.length) return;
  const card = document.getElementById("currentCard");
  if (card) card.classList.add(decision === "rejected" ? "slide-left" : "slide-up");
  state.decisions.push({{ idx: state.index, decision, rating: null }});
  state.index++;
  save();
  setTimeout(render, 380);
}}

function undo() {{
  if (state.decisions.length === 0) return;
  state.decisions.pop();
  state.index--;
  save();
  render();
}}

function reset() {{
  if (!confirm("Reset all decisions for this brand?")) return;
  state = {{ index: 0, decisions: [] }};
  save();
  render();
}}

function toggleShortcuts() {{
  document.getElementById("shortcuts").classList.toggle("show");
}}

function showSummary() {{
  const h = {{ s1:0, s2:0, s3:0, s4:0, s5:0, rejected:0, skipped:0 }};
  const lists = {{ 5: [], 4: [], 3: [] }};
  state.decisions.forEach(d => {{
    if (d.decision === "rated") {{
      h["s" + d.rating]++;
      if (lists[d.rating]) lists[d.rating].push(IMAGES[d.idx]);
    }}
    else if (d.decision === "rejected") h.rejected++;
    else if (d.decision === "skipped") h.skipped++;
  }});
  for (let i = 1; i <= 5; i++) document.getElementById("s" + i).textContent = h["s" + i];
  document.getElementById("sReject").textContent = h.rejected;
  document.getElementById("sSkip").textContent = h.skipped;
  [5, 4, 3].forEach(key => {{
    const el = document.getElementById("list" + key);
    const list = lists[key];
    el.innerHTML = list.length === 0
      ? '<div class="empty-note">Nothing yet</div>'
      : list.map(img => '<div>' + img.batch + ' · ' + img.filename + '</div>').join("");
  }});
  document.getElementById("summary").classList.add("show");
}}

function closeSummary() {{ document.getElementById("summary").classList.remove("show"); }}

function download() {{
  const rated = state.decisions.filter(d => d.decision === "rated");
  const byStar = {{ 5: [], 4: [], 3: [], 2: [], 1: [] }};
  rated.forEach(d => {{ byStar[d.rating].push(Object.assign({{}}, IMAGES[d.idx], {{ rating: d.rating }})); }});
  const payload = {{
    brand: BRAND,
    exported_at: new Date().toISOString(),
    total_reviewed: state.decisions.length,
    total_images: IMAGES.length,
    counts: {{
      "5_star": byStar[5].length, "4_star": byStar[4].length, "3_star": byStar[3].length,
      "2_star": byStar[2].length, "1_star": byStar[1].length,
      rejected: state.decisions.filter(d => d.decision === "rejected").length,
      skipped: state.decisions.filter(d => d.decision === "skipped").length,
    }},
    approved_4plus: [...byStar[5], ...byStar[4]],
    by_rating: byStar,
    all_decisions: state.decisions.map(d => Object.assign({{}}, IMAGES[d.idx], {{ decision: d.decision, rating: d.rating }})),
  }};
  const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: "application/json" }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "approved_" + BRAND + "_" + Date.now() + ".json";
  a.click();
  URL.revokeObjectURL(url);
}}

document.addEventListener("keydown", (e) => {{
  if (document.getElementById("summary").classList.contains("show")) return;
  const k = e.key;
  if (k >= "1" && k <= "5") rate(parseInt(k, 10));
  else if (k === "0" || k === "ArrowLeft") decide("rejected");
  else if (k === "ArrowRight") rate(5);
  else if (k === " ") {{ e.preventDefault(); decide("skipped"); }}
  else if (k.toLowerCase() === "z") undo();
  else if (k.toLowerCase() === "e") showSummary();
  else if (k.toLowerCase() === "r") reset();
  else if (k === "?" || k.toLowerCase() === "h") toggleShortcuts();
}});

let touchStartX = 0;
document.addEventListener("touchstart", (e) => {{ touchStartX = e.touches[0].clientX; }});
document.addEventListener("touchend", (e) => {{
  const dx = e.changedTouches[0].clientX - touchStartX;
  if (dx > 80) rate(5);
  else if (dx < -80) decide("rejected");
}});

render();
</script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brand", required=True, choices=list(THEMES.keys()))
    parser.add_argument("--include", help="Substring filter on batch folder name")
    parser.add_argument("--output", default=None)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()

    images = collect_images(args.brand, args.include)
    if not images:
        sys.exit("No images found")

    theme = THEMES[args.brand]
    out_path = pathlib.Path(args.output) if args.output else (
        ROOT / "OUTPUT" / f"review_{args.brand}.html"
    )

    html = HTML.format(
        brand=args.brand,
        brand_name=BRAND_NAMES[args.brand],
        total=len(images),
        images_json=json.dumps(images),
        **theme,
    )
    out_path.write_text(html, encoding="utf-8")
    print(f"[build] {out_path}  ({len(images)} images)")

    if not args.no_open:
        # Start a local HTTP server rooted at OUTPUT/ so relative image paths resolve.
        # Safari blocks cross-origin file:// image loading; HTTP fixes it.
        output_dir = ROOT / "OUTPUT"
        port = 8765
        print(f"[serve] http://localhost:{port}/{out_path.name}")
        print(f"[serve] Ctrl+C in terminal to stop server")
        # Open browser first
        subprocess.Popen(
            ["open", f"http://localhost:{port}/{out_path.name}"]
        )
        # Foreground the server so the process stays alive
        subprocess.run(
            ["python3", "-m", "http.server", str(port), "--bind", "127.0.0.1"],
            cwd=str(output_dir),
        )


if __name__ == "__main__":
    main()
