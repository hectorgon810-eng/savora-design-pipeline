#!/usr/bin/env python3
"""
Claude Design HTML generator.

Produces 3 self-contained HTML variations per post using the playbook
templates. Each HTML file renders at 1080×1350 (4:5) in a browser, pulls
fonts from Google Fonts, and references the real Cloudinary image URL.

Usage:
    python3 scripts/claude_design_html.py \\
        --brand blue_mezcal \\
        --post-id BM-A1-001 \\
        --template A1 \\
        --image-key B-35 \\
        --subject "HOMBRE Old Fashioned" \\
        --support "Branded ice cube. Bourbon underneath."

Output:
    OUTPUT/claude_design/blue_mezcal/BM-A1-001/variation_{1..3}.html

Open in Safari/Chrome for review. Each file is ~1080×1350 — use browser
zoom to 50% to see full frame.
"""

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CLOUDINARY_URLS_PATH = ROOT / "cloudinary_urls.json"


# ---------- brand CSS tokens ----------

BRANDS = {
    "jackson_house": {
        "name": "Jackson House",
        "address": "17 Wood St, Middletown, DE 19709",
        "cta": "Reserve your table · link in bio",
        "fonts_import": (
            "https://fonts.googleapis.com/css2?"
            "family=Rye&family=IM+Fell+English+SC&family=Playfair+Display:wght@400;600&"
            "family=Cormorant+Garamond:ital,wght@1,400;1,600&family=Inter:wght@400;500&display=swap"
        ),
        "palette": {
            "gold": "#C9A24A",
            "ink": "#0F0F0F",
            "ivory": "#F5EEDE",
            "brass": "#8B6B2F",
        },
    },
    "blue_mezcal": {
        "name": "Blue Mezcal",
        "address": "826 Kohl Ave, Middletown, DE 19709",
        "cta": "Visit us · link in bio",
        "fonts_import": (
            "https://fonts.googleapis.com/css2?"
            "family=Smokum&family=Rye&family=DM+Sans:wght@400;500;700&"
            "family=Permanent+Marker&family=Inter:wght@400;500&display=swap"
        ),
        "palette": {
            "azure": "#2FA9D8",
            "navy": "#184B66",
            "cream": "#F6F1E7",
            "chili": "#C1272D",
        },
    },
    "el_azteca": {
        "name": "El Azteca",
        "address": "Delaware · Rehoboth Beach",
        "cta": "Find your nearest location · link in bio",
        "fonts_import": (
            "https://fonts.googleapis.com/css2?"
            "family=Cinzel:wght@500;700&family=Work+Sans:wght@400;500;700&"
            "family=Ceviche+One&family=Inter:wght@400;500&display=swap"
        ),
        "palette": {
            "red": "#D9262B",
            "gold": "#F5C518",
            "blue": "#1B4D8F",
            "green": "#3F7E39",
            "black": "#0A0A0A",
        },
    },
}


# ---------- template renderers ----------

BASE_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;overflow:hidden}
.canvas{position:relative;width:1080px;height:1350px;overflow:hidden}
.logo{position:absolute;font-size:14px;letter-spacing:.2em;text-transform:uppercase;opacity:.85}
img.photo{display:block;width:100%;height:100%;object-fit:cover}
"""


def render_jackson_house_a1(variation: int, image_url: str, subject: str, support: str, address: str, cta: str) -> str:
    """Jackson House A1 Menu-Card Hero variations."""
    layouts = {
        1: {
            "photo_frame": "top:120px;left:90px;width:900px;height:900px;border:1px solid #C9A24A",
            "text_block": "top:1080px;left:0;width:100%;text-align:center",
            "align": "center",
        },
        2: {
            "photo_frame": "top:80px;left:60px;width:800px;height:800px;border:1px solid #C9A24A",
            "text_block": "top:920px;left:60px;width:960px;text-align:left",
            "align": "left",
        },
        3: {
            "photo_frame": "top:200px;left:540px;width:480px;height:640px;border:1px solid #C9A24A",
            "text_block": "top:240px;left:60px;width:440px;text-align:left",
            "align": "left",
        },
    }
    L = layouts[variation]
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>JH A1 v{variation}</title>
<link href="{BRANDS['jackson_house']['fonts_import']}" rel="stylesheet">
<style>{BASE_CSS}
.canvas{{background:#F5EEDE}}
.frame{{position:absolute;{L['photo_frame']};padding:14px;box-sizing:border-box}}
.frame::before,.frame::after{{content:"";position:absolute;width:40px;height:40px;border:3px solid #C9A24A}}
.frame::before{{top:-3px;left:-3px;border-right:none;border-bottom:none}}
.frame::after{{bottom:-3px;right:-3px;border-left:none;border-top:none}}
.frame img{{width:100%;height:100%;object-fit:cover}}
.title{{position:absolute;{L['text_block']};color:#0F0F0F;font-family:'Rye',serif;font-size:56px;line-height:1;letter-spacing:.02em}}
.sub{{position:absolute;color:#8B6B2F;font-family:'Cormorant Garamond',serif;font-style:italic;font-size:26px;line-height:1.2}}
.rule{{position:absolute;bottom:160px;left:20%;right:20%;height:1px;background:#C9A24A;opacity:.6}}
.footer{{position:absolute;bottom:90px;left:0;width:100%;text-align:center;font-family:'Playfair Display',serif;font-size:14px;color:#0F0F0F}}
.footer em{{display:block;margin-top:6px;color:#8B6B2F;font-style:italic}}
.logo{{bottom:30px;left:0;width:100%;text-align:center;color:#8B6B2F;font-family:'IM Fell English SC',serif;font-size:20px}}
</style></head><body>
<div class="canvas">
  <div class="frame"><img src="{image_url}" alt=""></div>
  <div class="title" style="{'text-align:'+L['align']};padding:0 60px">{subject}</div>
  <div class="sub" style="top:{1080+72 if variation==1 else (920+72 if variation==2 else 320)}px;{'left:0;width:100%;text-align:center' if variation==1 else 'left:60px;width:960px;text-align:left' if variation==2 else 'left:60px;width:440px;text-align:left'}">{support}</div>
  <div class="rule"></div>
  <div class="footer">{address}<em>{cta}</em></div>
  <div class="logo">JACKSON HOUSE</div>
</div></body></html>"""


def render_blue_mezcal_a1(variation: int, image_url: str, subject: str, support: str, address: str, cta: str) -> str:
    """Blue Mezcal A1 Block-Headline Hero variations."""
    blocks = {
        1: {"block_pos": "bottom:280px;left:60px;width:auto;max-width:800px", "logo_pos": "bottom:40px;left:0;width:100%;text-align:center"},
        2: {"block_pos": "top:120px;right:60px;left:auto;width:auto;max-width:680px", "logo_pos": "bottom:40px;right:60px;text-align:right"},
        3: {"block_pos": "top:50%;left:50%;transform:translate(-50%,-50%);width:auto;max-width:700px;text-align:center", "logo_pos": "bottom:40px;left:0;width:100%;text-align:center"},
    }
    L = blocks[variation]
    align = "center" if variation == 3 else "left"
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>BM A1 v{variation}</title>
<link href="{BRANDS['blue_mezcal']['fonts_import']}" rel="stylesheet">
<style>{BASE_CSS}
.canvas{{background:#184B66}}
.bg{{position:absolute;inset:0;filter:saturate(.9) brightness(.85)}}
.bg img{{width:100%;height:100%;object-fit:cover}}
.block{{position:absolute;{L['block_pos']};background:#F6F1E7;padding:36px 44px;text-align:{align}}}
.title{{font-family:'Smokum','Rye',serif;font-size:64px;line-height:1;color:#184B66;letter-spacing:.01em}}
.sub{{margin-top:18px;font-family:'DM Sans',sans-serif;font-weight:500;font-size:22px;color:#184B66;opacity:.85}}
.footer{{position:absolute;bottom:100px;left:0;width:100%;text-align:center;font-family:'DM Sans',sans-serif;font-size:16px;color:#F6F1E7;opacity:.8;letter-spacing:.08em;text-transform:uppercase}}
.logo{{{L['logo_pos']};color:#2FA9D8;font-family:'Smokum',serif;font-size:28px;letter-spacing:.08em}}
</style></head><body>
<div class="canvas">
  <div class="bg"><img src="{image_url}" alt=""></div>
  <div class="block">
    <div class="title">{subject}</div>
    <div class="sub">{support}</div>
  </div>
  <div class="footer">{address} · {cta}</div>
  <div class="logo">BLUE MEZCAL</div>
</div></body></html>"""


def render_el_azteca_a1(variation: int, image_url: str, subject: str, support: str, address: str, cta: str) -> str:
    """El Azteca A1 Sunstone Hero variations."""
    variants = {
        1: {"title_pos": "left:48px;right:48px;top:980px;text-align:left", "title_color": "#D9262B"},
        2: {"title_pos": "left:48px;right:48px;top:960px;text-align:left", "title_color": "#F5C518"},
        3: {"title_pos": "left:0;right:0;top:1020px;text-align:center;padding:0 48px", "title_color": "#D9262B"},
    }
    V = variants[variation]
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>AZ A1 v{variation}</title>
<link href="{BRANDS['el_azteca']['fonts_import']}" rel="stylesheet">
<style>{BASE_CSS}
.canvas{{background:#0A0A0A;overflow:hidden}}
.sunstone{{position:absolute;top:50px;left:50%;transform:translateX(-50%);width:800px;height:800px;border-radius:50%;border:16px solid #F5C518;opacity:.15}}
.photo-wrap{{position:absolute;top:0;left:0;width:100%;height:945px;overflow:hidden}}
.photo-wrap img{{width:100%;height:100%;object-fit:cover}}
.fade{{position:absolute;left:0;right:0;bottom:405px;height:120px;background:linear-gradient(to bottom,transparent,#0A0A0A)}}
.title{{position:absolute;{V['title_pos']};color:{V['title_color']};font-family:'Cinzel',serif;font-weight:700;font-size:60px;line-height:1;text-transform:uppercase;letter-spacing:.02em}}
.sub{{position:absolute;left:48px;right:48px;top:1070px;color:#F5C518;font-family:'Work Sans',sans-serif;font-weight:500;font-size:22px;{'text-align:center' if variation==3 else 'text-align:left'};padding:0 48px}}
.step-fret{{position:absolute;bottom:0;left:0;right:0;height:40px;background:repeating-linear-gradient(90deg,#D9262B 0 40px,transparent 40px 80px)}}
.footer{{position:absolute;bottom:56px;left:48px;right:48px;color:#F5C518;font-family:'Work Sans',sans-serif;font-size:14px;letter-spacing:.12em;text-transform:uppercase;display:flex;justify-content:space-between;align-items:center}}
.logo{{font-family:'Cinzel',serif;font-weight:700;font-size:20px;color:#D9262B;letter-spacing:.15em}}
</style></head><body>
<div class="canvas">
  <div class="sunstone"></div>
  <div class="photo-wrap"><img src="{image_url}" alt=""></div>
  <div class="fade"></div>
  <div class="title">{subject}</div>
  <div class="sub">{support}</div>
  <div class="footer"><span>{address}</span><span class="logo">EL AZTECA</span></div>
  <div class="step-fret"></div>
</div></body></html>"""


RENDERERS = {
    ("jackson_house", "A1"): render_jackson_house_a1,
    ("blue_mezcal", "A1"): render_blue_mezcal_a1,
    ("el_azteca", "A1"): render_el_azteca_a1,
}


# ---------- main ----------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brand", required=True, choices=BRANDS.keys())
    parser.add_argument("--post-id", required=True)
    parser.add_argument("--template", required=True)
    parser.add_argument("--image-key", required=True, help="Cloudinary filename key (e.g. B-35)")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--support", default="")
    args = parser.parse_args()

    if not CLOUDINARY_URLS_PATH.exists():
        sys.exit(f"Missing {CLOUDINARY_URLS_PATH}")
    urls = json.loads(CLOUDINARY_URLS_PATH.read_text())
    if args.image_key not in urls:
        sys.exit(f"Image key {args.image_key!r} not in cloudinary_urls.json")
    image_url = urls[args.image_key]

    renderer = RENDERERS.get((args.brand, args.template))
    if renderer is None:
        sys.exit(
            f"No HTML renderer yet for ({args.brand}, {args.template}). "
            f"Available: {list(RENDERERS.keys())}"
        )

    brand = BRANDS[args.brand]
    out_dir = ROOT / "OUTPUT" / "claude_design" / args.brand / args.post_id
    out_dir.mkdir(parents=True, exist_ok=True)

    for i in (1, 2, 3):
        html = renderer(
            variation=i,
            image_url=image_url,
            subject=args.subject,
            support=args.support,
            address=brand["address"],
            cta=brand["cta"],
        )
        out_path = out_dir / f"variation_{i}.html"
        out_path.write_text(html)
        print(f"  ✓ {out_path.relative_to(ROOT)}")

    print(f"\nDone. Review: open {out_dir}/variation_1.html")


if __name__ == "__main__":
    main()
