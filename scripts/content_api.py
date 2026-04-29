#!/usr/bin/env python3
"""Local Savora content catalog API.

This indexes generated pipeline images without moving them. The SQLite catalog
stores review state while the existing folders remain the source files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import mimetypes
import os
import pathlib
import shutil
import sqlite3
import sys
import time
import urllib.parse
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from zoneinfo import ZoneInfo

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


ROOT = pathlib.Path(__file__).resolve().parent.parent
if load_dotenv:
    load_dotenv(ROOT / ".env")

DB_PATH = ROOT / "OUTPUT" / "content_state" / "content.sqlite"
SCRIPTS_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import caption_service

BRAND_ALIASES = {
    "blue-mezcal": "blue_mezcal",
    "blue_mezcal": "blue_mezcal",
    "jackson-house": "jackson_house",
    "jackson_house": "jackson_house",
    "azteca": "azteca",
    "el-azteca": "azteca",
    "el_azteca": "azteca",
    "savora": "savora",
    "savora_v1_cream_dish_voice": "savora",
    "aztecarestaurantrehoboth": "aztecarestaurantrehoboth",
}

BRAND_LABELS = {
    "blue_mezcal": "Blue Mezcal",
    "jackson_house": "Jackson House",
    "azteca": "El Azteca",
    "savora": "Savora",
    "aztecarestaurantrehoboth": "Azteca Rehoboth",
}

BRAND_THEMES = {
    "blue_mezcal": {"accent": "#1E3A8A", "paper": "#F3ECD8", "ink": "#10245F"},
    "jackson_house": {"accent": "#C9A24B", "paper": "#0C0B0A", "ink": "#F2EADF"},
    "azteca": {"accent": "#E63946", "paper": "#F8F2DF", "ink": "#18140f"},
    "savora": {"accent": "#D5662E", "paper": "#F4ECD8", "ink": "#0F3B3C"},
    "aztecarestaurantrehoboth": {"accent": "#E63946", "paper": "#F8F2DF", "ink": "#18140f"},
}

BRAND_CSVS = {
    "blue_mezcal": "bluemezcalrestaurant.csv",
    "jackson_house": "jacksonhousede.csv",
    "azteca": "aztecadelaware.csv",
    "aztecarestaurantrehoboth": "aztecarestaurantrehoboth.csv",
}

BRAND_ACCOUNTS = {
    "blue_mezcal": "@bluemezcalrestaurant",
    "jackson_house": "@jacksonhousede",
    "el_azteca": "@aztecadelaware",
    "azteca": "@aztecadelaware",
    "azteca_rehoboth": "@aztecarestaurantrehoboth",
    "aztecarestaurantrehoboth": "@aztecarestaurantrehoboth",
}

FULL_EXPORT_HEADER = [
    "slot_index",
    "date",
    "time",
    "dow",
    "scheduled_at_iso",
    "account_handle",
    "brand",
    "post_group_id",
    "carousel_order",
    "media_type",
    "image_url",
    "image_key",
    "asset_id",
    "post_id",
    "variation",
    "content_role",
    "source",
    "caption",
    "hashtags",
    "alt_text",
    "first_comment",
    "notes",
]

POST_TIMES = {
    "blue_mezcal": {0: "17:00", 1: "17:00", 3: "17:30", 4: "17:30"},
    "jackson_house": {0: "17:30", 1: "17:30", 3: "18:00", 4: "18:00"},
    "azteca": {0: "17:00", 1: "17:00", 3: "17:30", 4: "17:30"},
    "aztecarestaurantrehoboth": {0: "11:00", 4: "16:30"},
    "savora": {0: "10:00", 2: "10:00", 4: "10:00"},
}

GRAPHIC_DAYS = {1, 3}


def normalize_brand(slug: str) -> str:
    return BRAND_ALIASES.get(slug, slug.replace("-", "_"))


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def rel_to_root(path: pathlib.Path, root: pathlib.Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def asset_id_for(rel_path: str) -> str:
    return hashlib.sha1(rel_path.encode("utf-8")).hexdigest()[:20]


def variation_label(filename: str) -> str:
    return pathlib.Path(filename).stem.replace("variation_", "V")


def variation_number(filename: str) -> int | None:
    label = variation_label(filename)
    if label.startswith("V") and label[1:].isdigit():
        return int(label[1:])
    return None


def read_prompt_records(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            out.append(payload)
    return out


def metadata_for_image(image_path: pathlib.Path) -> dict:
    records = read_prompt_records(image_path.parent / "prompts.jsonl")
    if not records:
        return {}
    number = variation_number(image_path.name)
    if number is not None:
        for record in records:
            if record.get("variation") == number:
                return record
    label = variation_label(image_path.name)
    for record in records:
        if str(record.get("variation", "")).lower() == label.lower():
            return record
    return records[0]


def connect(db_path: pathlib.Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS assets (
            id TEXT PRIMARY KEY,
            brand TEXT NOT NULL,
            source_brand_dir TEXT NOT NULL,
            post_id TEXT NOT NULL,
            variation TEXT NOT NULL,
            image_path TEXT NOT NULL UNIQUE,
            prompt_path TEXT,
            metadata_json TEXT NOT NULL DEFAULT '{}',
            backend TEXT,
            stem TEXT,
            format TEXT,
            aspect TEXT,
            angle TEXT,
            image_key TEXT,
            image_url TEXT,
            subject TEXT,
            support TEXT,
            status TEXT NOT NULL DEFAULT 'new',
            rating INTEGER,
            notes TEXT,
            duplicate_group_id TEXT,
            duplicate_winner INTEGER NOT NULL DEFAULT 0,
            pick_path TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_brand ON assets(brand)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_rating ON assets(rating)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_duplicate ON assets(duplicate_group_id)")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS plans (
            brand TEXT PRIMARY KEY,
            version INTEGER NOT NULL DEFAULT 1,
            updated_at TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS plan_slots (
            brand TEXT NOT NULL,
            slot_index INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            dow TEXT NOT NULL,
            slot_kind TEXT,
            source TEXT NOT NULL,
            asset_id TEXT,
            asset_snapshot TEXT NOT NULL DEFAULT '{}',
            caption_draft TEXT,
            PRIMARY KEY (brand, slot_index),
            FOREIGN KEY (brand) REFERENCES plans(brand) ON DELETE CASCADE
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS plan_pool (
            brand TEXT NOT NULL,
            asset_id TEXT NOT NULL,
            position INTEGER NOT NULL,
            asset_snapshot TEXT NOT NULL DEFAULT '{}',
            PRIMARY KEY (brand, asset_id),
            FOREIGN KEY (brand) REFERENCES plans(brand) ON DELETE CASCADE
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS plan_slot_carousel_items (
            brand TEXT NOT NULL,
            slot_index INTEGER NOT NULL,
            item_order INTEGER NOT NULL,
            asset_id TEXT,
            asset_snapshot TEXT NOT NULL DEFAULT '{}',
            role TEXT,
            PRIMARY KEY (brand, slot_index, item_order),
            FOREIGN KEY (brand, slot_index)
                REFERENCES plan_slots(brand, slot_index)
                ON DELETE CASCADE
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS conflict_acknowledgements (
            brand TEXT NOT NULL,
            conflict_key TEXT NOT NULL,
            acknowledged_at TEXT NOT NULL,
            PRIMARY KEY (brand, conflict_key)
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_plan_slots_brand ON plan_slots(brand)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_plan_pool_brand_position ON plan_pool(brand, position)")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_carousel_items_brand_slot "
        "ON plan_slot_carousel_items(brand, slot_index)"
    )
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(plan_slots)").fetchall()}
    if "caption_variants" not in columns:
        conn.execute("ALTER TABLE plan_slots ADD COLUMN caption_variants TEXT NOT NULL DEFAULT '[]'")
    conn.commit()


def row_to_dict(row: sqlite3.Row) -> dict:
    data = dict(row)
    data["label"] = BRAND_LABELS.get(data["brand"], data["brand"].replace("_", " ").title())
    data["theme"] = BRAND_THEMES.get(data["brand"], BRAND_THEMES["savora"])
    return data


def scan_generated_assets(
    *,
    root: pathlib.Path = ROOT,
    conn: sqlite3.Connection | None = None,
    brand: str | None = None,
    include_archives: bool = False,
) -> dict:
    owned_conn = conn is None
    conn = conn or connect(root / "OUTPUT" / "content_state" / "content.sqlite")
    base = root / "OUTPUT" / "nano_banana"
    counts = {"indexed": 0, "seen": 0, "skipped_archives": 0}
    if not base.exists():
        return counts

    wanted_brand = normalize_brand(brand) if brand else None
    stamp = now_iso()
    for image_path in sorted(base.rglob("variation_*.png")):
        rel_parts = image_path.relative_to(base).parts
        if len(rel_parts) < 3:
            continue
        if not include_archives and any(part.startswith("_archive") for part in rel_parts):
            counts["skipped_archives"] += 1
            continue
        source_brand_dir = rel_parts[0]
        canonical_brand = normalize_brand(source_brand_dir)
        if wanted_brand and canonical_brand != wanted_brand:
            continue
        counts["seen"] += 1
        rel_image = rel_to_root(image_path, root)
        prompt_path = image_path.parent / "prompts.jsonl"
        rel_prompt = rel_to_root(prompt_path, root) if prompt_path.exists() else None
        meta = metadata_for_image(image_path)
        post_id = image_path.parent.name
        asset_id = asset_id_for(rel_image)
        existing = conn.execute("SELECT status, rating, notes FROM assets WHERE id = ?", (asset_id,)).fetchone()
        status = existing["status"] if existing else "new"
        rating = existing["rating"] if existing else None
        notes = existing["notes"] if existing else None
        conn.execute(
            """
            INSERT INTO assets (
                id, brand, source_brand_dir, post_id, variation, image_path,
                prompt_path, metadata_json, backend, stem, format, aspect,
                angle, image_key, image_url, subject, support, status, rating,
                notes, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                brand=excluded.brand,
                source_brand_dir=excluded.source_brand_dir,
                post_id=excluded.post_id,
                variation=excluded.variation,
                image_path=excluded.image_path,
                prompt_path=excluded.prompt_path,
                metadata_json=excluded.metadata_json,
                backend=excluded.backend,
                stem=excluded.stem,
                format=excluded.format,
                aspect=excluded.aspect,
                angle=excluded.angle,
                image_key=excluded.image_key,
                image_url=excluded.image_url,
                subject=excluded.subject,
                support=excluded.support,
                updated_at=excluded.updated_at
            """,
            (
                asset_id,
                canonical_brand,
                source_brand_dir,
                post_id,
                variation_label(image_path.name),
                rel_image,
                rel_prompt,
                json.dumps(meta, sort_keys=True),
                meta.get("backend"),
                meta.get("stem"),
                meta.get("format"),
                meta.get("aspect"),
                meta.get("angle"),
                meta.get("image_key"),
                meta.get("image_url"),
                meta.get("subject"),
                meta.get("support"),
                status,
                rating,
                notes,
                stamp,
                stamp,
            ),
        )
        counts["indexed"] += 1
    conn.commit()
    if owned_conn:
        conn.close()
    return counts


def list_brands(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT brand, COUNT(*) AS total,
               SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) AS new_count,
               SUM(CASE WHEN status = 'picked' THEN 1 ELSE 0 END) AS picked_count,
               SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) AS rejected_count,
               SUM(CASE WHEN duplicate_group_id IS NOT NULL THEN 1 ELSE 0 END) AS duplicate_count
        FROM assets
        GROUP BY brand
        ORDER BY brand
        """
    ).fetchall()
    return [
        {
            **dict(row),
            "label": BRAND_LABELS.get(row["brand"], row["brand"].replace("_", " ").title()),
            "theme": BRAND_THEMES.get(row["brand"], BRAND_THEMES["savora"]),
        }
        for row in rows
    ]


def list_assets(
    conn: sqlite3.Connection,
    *,
    brand: str | None = None,
    status: str | None = None,
    q: str | None = None,
    min_rating: int | None = None,
    limit: int = 120,
    offset: int = 0,
) -> list[dict]:
    clauses = []
    params: list[object] = []
    if brand:
        clauses.append("brand = ?")
        params.append(normalize_brand(brand))
    if status and status != "all":
        clauses.append("status = ?")
        params.append(status)
    if min_rating is not None:
        clauses.append("rating >= ?")
        params.append(min_rating)
    if q:
        like = f"%{q}%"
        clauses.append("(post_id LIKE ? OR subject LIKE ? OR support LIKE ? OR image_key LIKE ? OR angle LIKE ?)")
        params.extend([like, like, like, like, like])
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = conn.execute(
        f"""
        SELECT * FROM assets
        {where}
        ORDER BY
          CASE status
            WHEN 'new' THEN 0
            WHEN 'shortlisted' THEN 1
            WHEN 'picked' THEN 2
            WHEN 'duplicate' THEN 3
            WHEN 'rejected' THEN 4
            ELSE 5
          END,
          COALESCE(rating, 0) DESC,
          post_id ASC,
          variation ASC
        LIMIT ? OFFSET ?
        """,
        (*params, limit, offset),
    ).fetchall()
    return [row_to_dict(row) for row in rows]


def update_asset(conn: sqlite3.Connection, asset_id: str, **fields: object) -> dict:
    allowed = {
        "status",
        "rating",
        "notes",
        "duplicate_group_id",
        "duplicate_winner",
        "pick_path",
    }
    updates = {key: value for key, value in fields.items() if key in allowed}
    if not updates:
        row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
        if not row:
            raise KeyError(asset_id)
        return row_to_dict(row)
    updates["updated_at"] = now_iso()
    set_sql = ", ".join(f"{key} = ?" for key in updates)
    params = [*updates.values(), asset_id]
    conn.execute(f"UPDATE assets SET {set_sql} WHERE id = ?", params)
    conn.commit()
    row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
    if not row:
        raise KeyError(asset_id)
    return row_to_dict(row)


def promote_pick(conn: sqlite3.Connection, *, root: pathlib.Path, asset_id: str) -> dict:
    row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
    if not row:
        raise KeyError(asset_id)
    data = row_to_dict(row)
    src = root / data["image_path"]
    if not src.exists():
        raise FileNotFoundError(src)
    rating = int(data["rating"] or 4)
    pick_dir = root / "OUTPUT" / "PICKS" / data["brand"]
    pick_dir.mkdir(parents=True, exist_ok=True)
    safe_post_id = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in data["post_id"])
    dst = pick_dir / f"{rating}s_{safe_post_id}_{data['variation']}.png"
    shutil.copy2(src, dst)
    return update_asset(
        conn,
        asset_id,
        status="picked",
        rating=rating,
        pick_path=rel_to_root(dst, root),
    )


def infer_content_role(asset: dict) -> str:
    text = " ".join(str(asset.get(key) or "") for key in ("subject", "support", "format", "angle")).lower()
    if "quote" in text or "review" in text or "you already know" in text:
        return "carousel_end"
    if "name-masthead" in text or "typographic" in text or "type is the image" in text:
        return "carousel_cover"
    if "event" in text or "happy hour" in text or "brunch" in text:
        return "single"
    return "single"


def caption_for_asset(asset: dict) -> str:
    if asset.get("source") == "scheduled":
        return asset.get("caption_draft") or asset.get("caption") or ""
    brand = asset.get("brand")
    subject = (asset.get("subject") or asset.get("post_id") or "This one").replace("_", " ").strip()
    support = (asset.get("support") or "").strip()
    if brand == "blue_mezcal":
        if support:
            return f"{subject}. {support}\n\nBlue Mezcal, Middletown."
        return f"{subject}.\n\nBlue Mezcal, Middletown."
    if brand == "jackson_house":
        if support:
            return f"{subject}. {support}\n\nReservations at the link."
        return f"{subject}.\n\nReservations at the link."
    if brand in {"azteca", "aztecarestaurantrehoboth"}:
        if support:
            return f"{subject}. {support}\n\nCamden, Dover, and Rehoboth."
        return f"{subject}.\n\nCamden, Dover, and Rehoboth."
    if brand == "savora":
        if support:
            return f"{subject}. {support}\n\nShot and built by Savora."
        return f"{subject}.\n\nShot and built by Savora."
    return f"{subject}. {support}".strip()


def generate_slot_dates(brand: str, days: int = 42) -> list[date]:
    today = date.today()
    end = today + timedelta(days=days)
    allowed = set(POST_TIMES.get(brand, POST_TIMES["blue_mezcal"]).keys())
    out = []
    d = today
    while d <= end:
        if d.weekday() in allowed:
            out.append(d)
        d += timedelta(days=1)
    return out


def parse_vista_datetime(value: str) -> datetime | None:
    text = value.strip()
    for fmt in ("%Y-%m-%d %I:%M %p", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def scheduled_posts_from_csv(*, root: pathlib.Path, brand: str, days: int = 42) -> list[dict]:
    csv_name = BRAND_CSVS.get(brand)
    if not csv_name:
        return []
    csv_path = root / "VISTA_SOCIAL_CSVS" / csv_name
    if not csv_path.exists():
        return []
    today = date.today()
    end = today + timedelta(days=days)
    groups: dict[tuple[str, str], list[dict]] = {}
    with csv_path.open(newline="", encoding="utf-8") as fh:
        for row in csv.reader(fh):
            if len(row) < 4:
                continue
            caption = row[0].strip()
            kind = (row[1] or "image").strip().lower()
            url = row[2].strip()
            sched = row[3].strip()
            parsed = parse_vista_datetime(sched)
            if not url or not parsed:
                continue
            if parsed.date() < today or parsed.date() > end:
                continue
            first_line = caption.splitlines()[0].strip().rstrip(". ")
            groups.setdefault((caption.strip().casefold(), parsed.date().isoformat()), []).append({
                "source": "scheduled",
                "brand": brand,
                "status": "scheduled",
                "content_role": "scheduled",
                "subject": first_line or "Scheduled post",
                "caption": caption,
                "caption_draft": caption,
                "image_url": url,
                "media_type": kind,
                "scheduled_date": parsed.date().isoformat(),
                "scheduled_time": parsed.strftime("%H:%M"),
            })
    out = []
    for rows in groups.values():
        seen_urls = set()
        unique_rows = []
        for item in rows:
            if item["image_url"] in seen_urls:
                continue
            seen_urls.add(item["image_url"])
            unique_rows.append(item)
        if not unique_rows:
            continue
        cover = dict(unique_rows[0])
        cover["id"] = f"scheduled_{len(out)}"
        cover["post_id"] = f"scheduled_{len(out)}"
        if len(unique_rows) > 1:
            cover["media_type"] = "carousel"
            cover["content_role"] = "carousel"
            cover["carousel_items"] = []
            for order, item in enumerate(unique_rows[1:], start=2):
                asset = dict(item)
                asset["id"] = f"{cover['id']}_item_{order}"
                asset["post_id"] = f"{cover['post_id']}_item_{order}"
                cover["carousel_items"].append({
                    "item_order": order,
                    "role": infer_content_role(asset),
                    "asset": asset,
                })
        out.append(cover)
    return out


def next_graphic_asset(queue: list[dict]) -> dict | None:
    for index, asset in enumerate(queue):
        if infer_content_role(asset) == "single":
            return queue.pop(index)
    return queue.pop(0) if queue else None


def schedule_suggestions(
    conn: sqlite3.Connection,
    *,
    brand: str,
    days: int = 42,
    root: pathlib.Path = ROOT,
) -> dict:
    brand = normalize_brand(brand)
    assets = list_assets(conn, brand=brand, status=None, limit=500)
    reviewed = [
        asset for asset in assets
        if asset["status"] in {"picked", "shortlisted"}
        and not asset.get("duplicate_group_id")
        and int(asset["rating"] or 0) >= 3
    ]
    fallback_new = [
        asset for asset in assets
        if asset["status"] == "new" and not asset.get("duplicate_group_id")
    ]
    usable = reviewed if reviewed else fallback_new
    usable.sort(key=lambda item: (
        0 if item["status"] == "picked" else 1,
        -(item["rating"] or 0),
        0 if infer_content_role(item) == "single" else 1,
        item["post_id"],
    ))
    queue = []
    for asset in usable:
        enriched = dict(asset)
        enriched["content_role"] = infer_content_role(enriched)
        enriched["caption_draft"] = caption_for_asset(enriched)
        queue.append(enriched)

    slots = []
    scheduled = scheduled_posts_from_csv(root=root, brand=brand, days=days)
    scheduled_by_date: dict[str, list[dict]] = {}
    for post in scheduled:
        scheduled_by_date.setdefault(post["scheduled_date"], []).append(post)

    for d in generate_slot_dates(brand, days=days):
        date_key = d.isoformat()
        for post in scheduled_by_date.pop(date_key, []):
            slots.append({
                "date": date_key,
                "dow": d.strftime("%a"),
                "time": post["scheduled_time"],
                "slot_kind": "scheduled",
                "asset": post,
                "carousel_items": post.get("carousel_items") or [],
            })
        if d.weekday() in GRAPHIC_DAYS:
            asset = next_graphic_asset(queue)
            if asset:
                slots.append({
                    "date": date_key,
                    "dow": d.strftime("%a"),
                    "time": POST_TIMES.get(brand, POST_TIMES["blue_mezcal"]).get(d.weekday(), "17:00"),
                    "slot_kind": "graphic",
                    "asset": asset,
                })
    for date_key, posts in scheduled_by_date.items():
        parsed = datetime.strptime(date_key, "%Y-%m-%d").date()
        for post in posts:
            slots.append({
                "date": date_key,
                "dow": parsed.strftime("%a"),
                "time": post["scheduled_time"],
                "slot_kind": "scheduled",
                "asset": post,
                "carousel_items": post.get("carousel_items") or [],
            })
    slots.sort(key=lambda slot: (slot["date"], slot["time"]))
    return {
        "brand": brand,
        "label": BRAND_LABELS.get(brand, brand),
        "slots": slots,
        "pool": queue,
    }


def plan_asset_snapshot(item: dict | None) -> dict:
    if not item:
        return {}
    asset = item.get("asset") if isinstance(item, dict) and isinstance(item.get("asset"), dict) else item
    return dict(asset or {})


def plan_slot_source(slot: dict, asset: dict | None) -> str:
    if slot.get("source"):
        return str(slot["source"])
    if slot.get("slot_kind") == "scheduled" or (asset and asset.get("source") == "vista_csv"):
        return "scheduled"
    if asset:
        return "generated"
    return "manual"


def normalize_carousel_items(items: list[dict]) -> list[dict]:
    normalized = []
    for position, item in enumerate(items, start=2):
        asset = plan_asset_snapshot(item.get("asset") if isinstance(item, dict) else None)
        if not asset:
            continue
        try:
            order = int(item.get("item_order", position))
        except (TypeError, ValueError):
            order = position
        normalized.append({
            "item_order": order,
            "asset": asset,
            "role": item.get("role") or infer_content_role(asset),
        })
    normalized.sort(key=lambda item: item["item_order"])
    for offset, item in enumerate(normalized, start=2):
        item["item_order"] = offset
    return normalized


def validate_plan_carousels(slots: list[dict]) -> list[dict]:
    failures = []
    for idx, slot in enumerate(slots):
        items = slot.get("carousel_items") or []
        if not items:
            continue
        if not slot.get("asset"):
            failures.append(export_failure(idx, "carousel_orphan", "Carousel slot needs a cover asset."))
        if 1 + len(items) > 10:
            failures.append(export_failure(idx, "carousel_too_many", "Carousel cannot exceed 10 total images."))
        seen = set()
        for item in items:
            try:
                order = int(item.get("item_order"))
            except (TypeError, ValueError):
                failures.append(export_failure(idx, "carousel_bad_order", "Carousel item order must be an integer."))
                continue
            if order < 2 or order > 10:
                failures.append(export_failure(idx, "carousel_bad_order", "Carousel item order must be between 2 and 10."))
            if order in seen:
                failures.append(export_failure(idx, "carousel_duplicate_order", "Carousel item orders must be unique."))
            seen.add(order)
    return failures


def plan_from_db(conn: sqlite3.Connection, *, brand: str) -> dict | None:
    brand = normalize_brand(brand)
    plan = conn.execute(
        "SELECT brand, version, updated_at FROM plans WHERE brand = ?",
        (brand,),
    ).fetchone()
    if not plan:
        return None
    slot_rows = conn.execute(
        """
        SELECT slot_index, date, time, dow, slot_kind, source, asset_snapshot, caption_draft, caption_variants
        FROM plan_slots
        WHERE brand = ?
        ORDER BY slot_index
        """,
        (brand,),
    ).fetchall()
    pool_rows = conn.execute(
        """
        SELECT asset_snapshot
        FROM plan_pool
        WHERE brand = ?
        ORDER BY position
        """,
        (brand,),
    ).fetchall()
    carousel_rows = conn.execute(
        """
        SELECT slot_index, item_order, asset_snapshot, role
        FROM plan_slot_carousel_items
        WHERE brand = ?
        ORDER BY slot_index, item_order
        """,
        (brand,),
    ).fetchall()
    carousel_by_slot: dict[int, list[dict]] = {}
    for row in carousel_rows:
        asset = json.loads(row["asset_snapshot"] or "{}")
        carousel_by_slot.setdefault(row["slot_index"], []).append({
            "item_order": row["item_order"],
            "asset": asset,
            "role": row["role"],
        })
    slots = []
    for row in slot_rows:
        asset = json.loads(row["asset_snapshot"] or "{}")
        if not asset:
            asset = None
        if asset and row["caption_draft"] is not None:
            asset["caption_draft"] = row["caption_draft"]
        carousel_items = carousel_by_slot.get(row["slot_index"], [])
        slot_kind = "carousel" if carousel_items else row["slot_kind"]
        slots.append({
            "slot_index": row["slot_index"],
            "date": row["date"],
            "time": row["time"],
            "dow": row["dow"],
            "slot_kind": slot_kind,
            "source": row["source"],
            "asset": asset,
            "caption_draft": row["caption_draft"],
            "caption_variants": json.loads(row["caption_variants"] or "[]"),
            "carousel_items": carousel_items,
        })
    return {
        "brand": plan["brand"],
        "version": plan["version"],
        "updated_at": plan["updated_at"],
        "slots": slots,
        "pool": [{"asset": json.loads(row["asset_snapshot"] or "{}")} for row in pool_rows],
    }


def save_plan(
    conn: sqlite3.Connection,
    *,
    brand: str,
    version: int,
    slots: list[dict],
    pool: list[dict],
) -> tuple[int, dict]:
    brand = normalize_brand(brand)
    current_row = conn.execute("SELECT version FROM plans WHERE brand = ?", (brand,)).fetchone()
    current = int(current_row["version"]) if current_row else 0
    if current and version != current:
        current_plan = plan_from_db(conn, brand=brand)
        return 409, current_plan or {"brand": brand, "version": current, "slots": [], "pool": []}
    if not current and version not in {0, 1}:
        return 409, {"brand": brand, "version": 0, "slots": [], "pool": []}
    carousel_failures = validate_plan_carousels(slots)
    if carousel_failures:
        return 422, {"error": "validation_failed", "failures": carousel_failures}

    new_version = current + 1 if current else 1
    created_at = now_iso()
    with conn:
        conn.execute(
            """
            INSERT INTO plans(brand, version, updated_at, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(brand) DO UPDATE SET
                version = excluded.version,
                updated_at = excluded.updated_at
            """,
            (brand, new_version, created_at, created_at),
        )
        conn.execute("DELETE FROM plan_slots WHERE brand = ?", (brand,))
        conn.execute("DELETE FROM plan_slot_carousel_items WHERE brand = ?", (brand,))
        conn.execute("DELETE FROM plan_pool WHERE brand = ?", (brand,))
        for idx, slot in enumerate(slots):
            try:
                slot_index = int(slot.get("slot_index", idx))
            except (TypeError, ValueError):
                slot_index = idx
            asset = plan_asset_snapshot(slot.get("asset"))
            caption = asset.get("caption_draft") if asset else None
            if caption is None:
                caption = slot.get("caption_draft")
            if caption is None and asset:
                caption = asset.get("caption")
            caption_variants = json.dumps(slot.get("caption_variants") or [])
            source = plan_slot_source(slot, asset)
            conn.execute(
                """
                INSERT INTO plan_slots(
                    brand, slot_index, date, time, dow, slot_kind, source,
                    asset_id, asset_snapshot, caption_draft, caption_variants
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    brand,
                    slot_index,
                    str(slot["date"]),
                    str(slot["time"]),
                    str(slot.get("dow") or ""),
                    slot.get("slot_kind"),
                    source,
                    asset.get("id") if asset else None,
                    json.dumps(asset),
                    caption,
                    caption_variants,
                ),
            )
            for item in normalize_carousel_items(slot.get("carousel_items") or []):
                item_asset = item["asset"]
                conn.execute(
                    """
                    INSERT INTO plan_slot_carousel_items(
                        brand, slot_index, item_order, asset_id, asset_snapshot, role
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        brand,
                        slot_index,
                        item["item_order"],
                        item_asset.get("id"),
                        json.dumps(item_asset),
                        item.get("role"),
                    ),
                )
        for position, item in enumerate(pool):
            asset = plan_asset_snapshot(item)
            asset_id = asset.get("id") or f"pool-{position}"
            conn.execute(
                """
                INSERT OR REPLACE INTO plan_pool(brand, asset_id, position, asset_snapshot)
                VALUES (?, ?, ?, ?)
                """,
                (brand, str(asset_id), position, json.dumps(asset)),
            )
    saved = plan_from_db(conn, brand=brand)
    return 200, saved or {"brand": brand, "version": new_version, "slots": [], "pool": []}


def regenerate_plan(
    conn: sqlite3.Connection,
    *,
    brand: str,
    root: pathlib.Path = ROOT,
    days: int = 42,
) -> dict:
    brand = normalize_brand(brand)
    suggestions = schedule_suggestions(conn, brand=brand, days=days, root=root)
    with conn:
        conn.execute("DELETE FROM plan_slot_carousel_items WHERE brand = ?", (brand,))
        conn.execute("DELETE FROM plan_pool WHERE brand = ?", (brand,))
        conn.execute("DELETE FROM plan_slots WHERE brand = ?", (brand,))
        conn.execute("DELETE FROM plans WHERE brand = ?", (brand,))
    status, plan = save_plan(
        conn,
        brand=brand,
        version=0,
        slots=suggestions["slots"],
        pool=suggestions["pool"],
    )
    if status != 200:
        raise RuntimeError("could not regenerate plan")
    return plan


def delete_plan(conn: sqlite3.Connection, *, brand: str) -> None:
    brand = normalize_brand(brand)
    with conn:
        conn.execute("DELETE FROM plan_slot_carousel_items WHERE brand = ?", (brand,))
        conn.execute("DELETE FROM plan_pool WHERE brand = ?", (brand,))
        conn.execute("DELETE FROM plan_slots WHERE brand = ?", (brand,))
        conn.execute("DELETE FROM plans WHERE brand = ?", (brand,))


def slot_from_plan(conn: sqlite3.Connection, *, brand: str, slot_index: int) -> dict | None:
    plan = plan_from_db(conn, brand=brand)
    if not plan:
        return None
    for slot in plan["slots"]:
        if int(slot["slot_index"]) == int(slot_index):
            return slot
    return None


def store_caption_variants(
    conn: sqlite3.Connection,
    *,
    brand: str,
    slot_index: int,
    variants: list[dict],
) -> dict:
    brand = normalize_brand(brand)
    with conn:
        conn.execute(
            "UPDATE plan_slots SET caption_variants = ? WHERE brand = ? AND slot_index = ?",
            (json.dumps(variants), brand, slot_index),
        )
    slot = slot_from_plan(conn, brand=brand, slot_index=slot_index)
    if not slot:
        raise KeyError(slot_index)
    return slot


def generate_caption_variants(conn: sqlite3.Connection, *, brand: str, slot_index: int, client=None) -> dict:
    brand = normalize_brand(brand)
    slot = slot_from_plan(conn, brand=brand, slot_index=slot_index)
    if not slot:
        raise KeyError(slot_index)
    cover = slot.get("asset")
    if not cover:
        raise ValueError("Slot has no cover asset.")
    variants = caption_service.generate_captions(
        brand=brand,
        slot=slot,
        cover_asset=cover,
        carousel_items=slot.get("carousel_items") or [],
        client=client,
    )
    slot = store_caption_variants(conn, brand=brand, slot_index=slot_index, variants=variants)
    usage = getattr(caption_service, "LAST_USAGE", {})
    return {
        "slot_index": slot_index,
        "variants": variants,
        "from_cache": bool(usage.get("cache_read_input_tokens", 0)) if isinstance(usage, dict) else False,
        "usage": usage if isinstance(usage, dict) else {},
        "slot": slot,
    }


def select_caption_variant(conn: sqlite3.Connection, *, brand: str, slot_index: int, variant_id: str) -> dict:
    brand = normalize_brand(brand)
    slot = slot_from_plan(conn, brand=brand, slot_index=slot_index)
    if not slot:
        raise KeyError(slot_index)
    variants = slot.get("caption_variants") or []
    selected_text = None
    for variant in variants:
        selected = variant.get("id") == variant_id
        variant["selected"] = selected
        if selected:
            selected_text = variant.get("text") or ""
    if selected_text is None:
        raise KeyError(variant_id)
    with conn:
        row = conn.execute(
            "SELECT asset_snapshot FROM plan_slots WHERE brand = ? AND slot_index = ?",
            (brand, slot_index),
        ).fetchone()
        asset = json.loads(row["asset_snapshot"] or "{}") if row else {}
        if asset:
            asset["caption_draft"] = selected_text
        conn.execute(
            """
            UPDATE plan_slots
            SET caption_draft = ?, caption_variants = ?, asset_snapshot = ?
            WHERE brand = ? AND slot_index = ?
            """,
            (selected_text, json.dumps(variants), json.dumps(asset), brand, slot_index),
        )
    updated = slot_from_plan(conn, brand=brand, slot_index=slot_index)
    if not updated:
        raise KeyError(slot_index)
    return updated


class ExportValidationError(ValueError):
    def __init__(self, manifest: dict):
        super().__init__("validation_failed")
        self.manifest = manifest


class ConflictValidationError(ValueError):
    def __init__(self, conflicts: list[dict]):
        super().__init__("unacknowledged_conflicts")
        self.conflicts = conflicts


def conflict_key_for(brand: str, code: str, slot_indices: list[int], date_text: str | None) -> str:
    parts = [normalize_brand(brand), code, ",".join(str(idx) for idx in sorted(slot_indices)), date_text or ""]
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()


def normalized_caption(text: str) -> str:
    return (text or "").strip().casefold()


def conflict_summary(conflicts: list[dict]) -> dict:
    summary = {"errors": 0, "warnings": 0, "info": 0, "acknowledged": 0}
    for conflict in conflicts:
        if conflict.get("acknowledged"):
            summary["acknowledged"] += 1
        severity = conflict.get("severity")
        if severity == "error":
            summary["errors"] += 1
        elif severity == "warning":
            summary["warnings"] += 1
        elif severity == "info":
            summary["info"] += 1
    return summary


def conflict_payload(
    *,
    brand: str,
    code: str,
    severity: str,
    date_text: str | None,
    slot_indices: list[int] | None = None,
    message: str,
    suggested_action: str = "none",
) -> dict:
    slot_indices = sorted(int(idx) for idx in (slot_indices or []))
    return {
        "key": conflict_key_for(brand, code, slot_indices, date_text),
        "code": code,
        "severity": severity,
        "date": date_text,
        "slot_indices": slot_indices,
        "message": message,
        "suggested_action": suggested_action,
        "acknowledged": False,
        "acknowledged_at": None,
    }


def vista_csv_path(root: pathlib.Path, brand: str) -> pathlib.Path | None:
    csv_name = BRAND_CSVS.get(normalize_brand(brand))
    return root / "VISTA_SOCIAL_CSVS" / csv_name if csv_name else None


def vista_csv_rows_for_conflicts(*, root: pathlib.Path, brand: str) -> tuple[pathlib.Path | None, list[dict]]:
    path = vista_csv_path(root, brand)
    if not path or not path.exists():
        return path, []
    rows = []
    with path.open(newline="", encoding="utf-8") as fh:
        for index, row in enumerate(csv.reader(fh)):
            if len(row) < 4:
                continue
            parsed = parse_vista_datetime(row[3].strip())
            rows.append({
                "index": index,
                "caption": row[0].strip(),
                "kind": (row[1] or "image").strip().lower(),
                "image_url": row[2].strip(),
                "scheduled": row[3].strip(),
                "parsed": parsed,
            })
    return path, rows


def slot_conflict_action(slots: list[dict]) -> str:
    return "move_generated_to_next_open_graphic_day" if any(slot.get("source") == "generated" for slot in slots) else "none"


def detect_conflicts(
    conn: sqlite3.Connection,
    *,
    brand: str,
    root: pathlib.Path = ROOT,
    now: datetime | None = None,
) -> dict:
    brand = normalize_brand(brand)
    checked_at_dt = now or datetime.now(ZoneInfo("America/New_York"))
    if checked_at_dt.tzinfo is None:
        checked_at_dt = checked_at_dt.replace(tzinfo=ZoneInfo("America/New_York"))
    checked_at = checked_at_dt.astimezone(ZoneInfo("America/New_York")).isoformat()
    plan = plan_from_db(conn, brand=brand) or {"brand": brand, "slots": []}
    slots = plan.get("slots", [])
    conflicts: list[dict] = []

    slots_by_date: dict[str, list[dict]] = {}
    slots_by_datetime: dict[tuple[str, str], list[dict]] = {}
    for slot in slots:
        if not slot.get("asset"):
            continue
        slots_by_date.setdefault(str(slot.get("date")), []).append(slot)
        slots_by_datetime.setdefault((str(slot.get("date")), str(slot.get("time"))), []).append(slot)

    for date_text, date_slots in sorted(slots_by_date.items()):
        if len(date_slots) < 2:
            continue
        indices = [int(slot["slot_index"]) for slot in date_slots]
        times = ", ".join(str(slot.get("time")) for slot in date_slots)
        conflicts.append(conflict_payload(
            brand=brand,
            code="same_day_collision",
            severity="error",
            date_text=date_text,
            slot_indices=indices,
            message=f"{len(date_slots)} posts are placed on {date_text} at {times}.",
            suggested_action=slot_conflict_action(date_slots),
        ))

    for (date_text, time_text), time_slots in sorted(slots_by_datetime.items()):
        if len(time_slots) < 2:
            continue
        conflicts.append(conflict_payload(
            brand=brand,
            code="same_time_collision",
            severity="error",
            date_text=date_text,
            slot_indices=[int(slot["slot_index"]) for slot in time_slots],
            message=f"{len(time_slots)} posts share {date_text} at {time_text}.",
            suggested_action=slot_conflict_action(time_slots),
        ))

    csv_path, vista_rows = vista_csv_rows_for_conflicts(root=root, brand=brand)
    if not csv_path or not csv_path.exists():
        conflicts.append(conflict_payload(
            brand=brand,
            code="vista_csv_missing",
            severity="warning",
            date_text=None,
            message=f"No Vista CSV is mapped or present for {BRAND_LABELS.get(brand, brand)}.",
            suggested_action="add_brand_csv",
        ))
    else:
        if datetime.fromtimestamp(csv_path.stat().st_mtime).date() < checked_at_dt.date() - timedelta(days=14):
            conflicts.append(conflict_payload(
                brand=brand,
                code="vista_csv_stale",
                severity="info",
                date_text=None,
                message=f"Vista CSV {csv_path.name} has not been updated in more than 14 days.",
            ))
        past_dates = sorted({
            row["parsed"].date().isoformat()
            for row in vista_rows
            if row["parsed"] and row["parsed"].date() < checked_at_dt.date()
        })
        for date_text in past_dates:
            conflicts.append(conflict_payload(
                brand=brand,
                code="vista_post_in_past",
                severity="info",
                date_text=date_text,
                message=f"Vista CSV includes scheduled posts before today on {date_text}.",
            ))
        groups: dict[tuple[str, str], list[dict]] = {}
        for row in vista_rows:
            if row["parsed"]:
                groups.setdefault((normalized_caption(row["caption"]), row["parsed"].date().isoformat()), []).append(row)
        for (caption_key, date_text), group_rows in sorted(groups.items()):
            if len(group_rows) < 2:
                continue
            split_slots = [
                slot for slot in slots
                if str(slot.get("date")) == date_text
                and slot.get("source") == "scheduled"
                and not slot.get("carousel_items")
                and normalized_caption((slot.get("asset") or {}).get("caption_draft") or (slot.get("asset") or {}).get("caption")) == caption_key
            ]
            if len(split_slots) >= 2:
                conflicts.append(conflict_payload(
                    brand=brand,
                    code="vista_carousel_detected",
                    severity="warning",
                    date_text=date_text,
                    slot_indices=[int(slot["slot_index"]) for slot in split_slots],
                    message=f"Vista has {len(group_rows)} same-caption rows on {date_text}; these should be one carousel.",
                    suggested_action="merge_into_carousel",
                ))

    ack_rows = conn.execute(
        "SELECT conflict_key, acknowledged_at FROM conflict_acknowledgements WHERE brand = ?",
        (brand,),
    ).fetchall()
    acknowledgements = {row["conflict_key"]: row["acknowledged_at"] for row in ack_rows}
    for conflict in conflicts:
        acked_at = acknowledgements.get(conflict["key"])
        if acked_at:
            conflict["acknowledged"] = True
            conflict["acknowledged_at"] = acked_at
    return {
        "brand": brand,
        "checked_at": checked_at,
        "conflicts": conflicts,
        "summary": conflict_summary(conflicts),
    }


def acknowledge_conflict(conn: sqlite3.Connection, *, brand: str, conflict_key: str, root: pathlib.Path = ROOT) -> dict:
    brand = normalize_brand(brand)
    with conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO conflict_acknowledgements(brand, conflict_key, acknowledged_at)
            VALUES (?, ?, ?)
            """,
            (brand, conflict_key, datetime.now(ZoneInfo("America/New_York")).isoformat()),
        )
    return detect_conflicts(conn, brand=brand, root=root)


def revoke_conflict_ack(conn: sqlite3.Connection, *, brand: str, conflict_key: str, root: pathlib.Path = ROOT) -> dict:
    brand = normalize_brand(brand)
    with conn:
        conn.execute(
            "DELETE FROM conflict_acknowledgements WHERE brand = ? AND conflict_key = ?",
            (brand, conflict_key),
        )
    return detect_conflicts(conn, brand=brand, root=root)


def next_open_graphic_date(brand: str, start: date, occupied: set[str]) -> date | None:
    for offset in range(1, 31):
        candidate = start + timedelta(days=offset)
        if candidate.weekday() in GRAPHIC_DAYS and candidate.isoformat() not in occupied:
            return candidate
    return None


def bump_plan_version(conn: sqlite3.Connection, brand: str) -> None:
    conn.execute(
        "UPDATE plans SET version = version + 1, updated_at = ? WHERE brand = ?",
        (now_iso(), brand),
    )


def auto_fix_conflict(
    conn: sqlite3.Connection,
    *,
    brand: str,
    conflict_key: str,
    action: str,
    root: pathlib.Path = ROOT,
) -> tuple[int, dict]:
    brand = normalize_brand(brand)
    current = detect_conflicts(conn, brand=brand, root=root)
    conflict = next((item for item in current["conflicts"] if item["key"] == conflict_key), None)
    if not conflict:
        return 404, {"error": "conflict_not_found"}
    if conflict.get("suggested_action") != action or action in {"none", "add_brand_csv"}:
        return 400, {"error": "unsupported_auto_fix"}
    plan = plan_from_db(conn, brand=brand)
    if not plan:
        return 404, {"error": "no_plan"}
    slots = plan["slots"]
    if action == "move_generated_to_next_open_graphic_day":
        generated = next(
            (slot for slot in slots if int(slot["slot_index"]) in conflict["slot_indices"] and slot.get("source") == "generated"),
            None,
        )
        if not generated:
            return 409, {"error": "no_generated_slot"}
        occupied = {str(slot.get("date")) for slot in slots if int(slot["slot_index"]) != int(generated["slot_index"]) and slot.get("asset")}
        next_date = next_open_graphic_date(brand, date.fromisoformat(generated["date"]), occupied)
        if not next_date:
            return 409, {"error": "no_open_graphic_day", "message": "No open graphic day found in the next 30 days."}
        with conn:
            conn.execute(
                "UPDATE plan_slots SET date = ?, dow = ?, time = ? WHERE brand = ? AND slot_index = ?",
                (
                    next_date.isoformat(),
                    next_date.strftime("%a"),
                    POST_TIMES.get(brand, POST_TIMES["blue_mezcal"]).get(next_date.weekday(), generated["time"]),
                    brand,
                    int(generated["slot_index"]),
                ),
            )
            bump_plan_version(conn, brand)
    elif action == "merge_into_carousel":
        merge_slots = [
            slot for slot in slots
            if int(slot["slot_index"]) in conflict["slot_indices"] and slot.get("source") == "scheduled" and slot.get("asset")
        ]
        if len(merge_slots) < 2:
            return 409, {"error": "not_enough_scheduled_slots"}
        merge_slots.sort(key=lambda slot: int(slot["slot_index"]))
        cover = merge_slots[0]
        existing_items = list(cover.get("carousel_items") or [])
        for item_slot in merge_slots[1:]:
            existing_items.append({
                "item_order": len(existing_items) + 2,
                "role": infer_content_role(item_slot["asset"]),
                "asset": item_slot["asset"],
            })
        cover["carousel_items"] = existing_items
        cover["slot_kind"] = "carousel"
        remove_indices = {int(slot["slot_index"]) for slot in merge_slots[1:]}
        kept_slots = [slot for slot in slots if int(slot["slot_index"]) not in remove_indices]
        kept_slots.sort(key=lambda slot: (slot["date"], slot["time"], int(slot["slot_index"])))
        for idx, slot in enumerate(kept_slots):
            slot["slot_index"] = idx
        status, saved = save_plan(conn, brand=brand, version=int(plan["version"]), slots=kept_slots, pool=plan.get("pool", []))
        if status != 200:
            return status, saved
        plan = saved
    refreshed_plan = plan_from_db(conn, brand=brand) or plan
    return 200, {"plan": refreshed_plan, "conflicts": detect_conflicts(conn, brand=brand, root=root)}


def unacknowledged_error_conflicts(conn: sqlite3.Connection, *, brand: str, root: pathlib.Path) -> list[dict]:
    payload = detect_conflicts(conn, brand=brand, root=root)
    return [
        conflict for conflict in payload["conflicts"]
        if conflict.get("severity") == "error" and not conflict.get("acknowledged")
    ]


def scheduled_datetime(date_text: str, time_text: str, timezone: str = "America/New_York") -> datetime:
    parsed_date = date.fromisoformat(date_text)
    parsed_time = datetime.strptime(time_text, "%H:%M").time()
    return datetime.combine(parsed_date, parsed_time, tzinfo=ZoneInfo(timezone))


def vista_datetime(date_text: str, time_text: str, timezone: str = "America/New_York") -> str:
    dt = scheduled_datetime(date_text, time_text, timezone)
    hour = dt.strftime("%I").lstrip("0") or "0"
    return f"{dt:%Y-%m-%d} {hour}:{dt:%M} {dt:%p}".lower()


def sorted_export_items(slots: list[dict]) -> list[tuple[int, dict, dict]]:
    items = []
    first_group_index: dict[str, int] = {}
    for idx, slot in enumerate(slots):
        asset = slot.get("asset")
        if not asset:
            continue
        group = asset.get("carousel_group_id") or ""
        if group and group not in first_group_index:
            first_group_index[group] = idx
        items.append((idx, slot, asset))

    def sort_key(item: tuple[int, dict, dict]) -> tuple[int, int, int]:
        idx, _, asset = item
        group = asset.get("carousel_group_id") or ""
        if group:
            try:
                order = int(asset.get("carousel_order"))
            except (TypeError, ValueError):
                order = 9999
            return (first_group_index[group], 0, order)
        return (idx, 1, idx)

    return sorted(items, key=sort_key)


def carousel_group_id_for(brand: str, slot_index: int, date_text: str) -> str:
    return f"car-{brand}-{slot_index:03d}-{date_text.replace('-', '')}"


def expanded_export_items(brand: str, slots: list[dict]) -> tuple[list[tuple[int, dict, dict]], list[dict], list[dict]]:
    expanded: list[tuple[int, dict, dict]] = []
    warnings: list[dict] = []
    failures: list[dict] = []
    legacy_slots = []
    for idx, slot in enumerate(slots):
        asset = slot.get("asset")
        if not asset:
            continue
        slot_index = int(slot.get("slot_index", idx))
        items = normalize_carousel_items(slot.get("carousel_items") or [])
        if not items:
            legacy_slots.append(slot)
            continue
        images = [asset] + [item["asset"] for item in items]
        if len(images) > 10:
            failures.append(export_failure(slot_index, "carousel_too_many", "Carousel cannot exceed 10 total images."))
        if len(images) == 2:
            warnings.append(export_warning(slot_index, "carousel_minimal", "Carousel has only 2 images."))
        group = carousel_group_id_for(brand, slot_index, str(slot.get("date", "")))
        caption = slot.get("caption_draft") or asset.get("caption_draft") or asset.get("caption") or ""
        cover = dict(asset)
        cover["carousel_group_id"] = group
        cover["carousel_order"] = 1
        cover["content_role"] = "cover"
        cover["caption_draft"] = caption
        expanded.append((slot_index, slot, cover))
        for item in items:
            item_asset = dict(item["asset"])
            item_asset["carousel_group_id"] = group
            item_asset["carousel_order"] = item["item_order"]
            item_asset["content_role"] = item.get("role") or infer_content_role(item_asset)
            item_asset["caption_draft"] = caption
            expanded.append((slot_index, slot, item_asset))
    expanded.extend(sorted_export_items(legacy_slots))
    return expanded, warnings, failures


def export_failure(slot_index: int, code: str, message: str) -> dict:
    return {"slot_index": slot_index, "code": code, "message": message}


def export_warning(slot_index: int, code: str, message: str) -> dict:
    return {"slot_index": slot_index, "code": code, "message": message}


def export_manifest(
    *,
    brand: str,
    exported_at: str,
    timezone: str,
    rows: list[dict],
    warnings: list[dict],
    failures: list[dict] | None = None,
) -> dict:
    carousel_counts: dict[str, int] = {}
    captions = []
    for row in rows:
        captions.append(row["caption"])
        if row["post_group_id"]:
            carousel_counts[row["post_group_id"]] = carousel_counts.get(row["post_group_id"], 0) + 1
    manifest = {
        "brand": brand,
        "exported_at": exported_at,
        "timezone": timezone,
        "row_count": 0 if failures else len(rows),
        "carousels": [
            {"post_group_id": group, "items": count}
            for group, count in sorted(carousel_counts.items())
        ],
        "warnings": warnings,
        "stats": {
            "rows_total": len(rows),
            "rows_carousel_items": sum(carousel_counts.values()),
            "rows_solo": len(rows) - sum(carousel_counts.values()),
            "captions_with_hashtags": sum(1 for row in rows if row["hashtags"]),
            "shortest_caption_chars": min((len(caption) for caption in captions), default=0),
            "longest_caption_chars": max((len(caption) for caption in captions), default=0),
        },
    }
    if failures:
        manifest["failures"] = failures
    return manifest


def build_export_rows(
    *,
    brand: str,
    slots: list[dict],
    timezone: str = "America/New_York",
    exported_at: str,
) -> tuple[list[dict], dict]:
    brand = normalize_brand(brand)
    account_handle = BRAND_ACCOUNTS.get(brand)
    rows = []
    export_items, warnings, failures = expanded_export_items(brand, slots)
    group_orders: dict[str, list[int]] = {}
    for slot_index, slot, asset in export_items:
        caption = (asset.get("caption_draft") or asset.get("caption") or "").strip()
        image_url = asset.get("image_url") or ""
        post_group_id = asset.get("carousel_group_id") or ""
        carousel_order = asset.get("carousel_order")
        scheduled_at = None
        try:
            scheduled_at = scheduled_datetime(str(slot["date"]), str(slot["time"]), timezone)
        except (KeyError, ValueError):
            failures.append(export_failure(slot_index, "bad_datetime", "Slot date/time must be ISO date and HH:MM."))
        if not account_handle:
            failures.append(export_failure(slot_index, "unknown_brand", f"No account handle configured for brand {brand}."))
        if not caption:
            failures.append(export_failure(slot_index, "empty_caption", "Caption is empty."))
        elif caption == caption_for_asset(asset):
            failures.append(export_failure(slot_index, "placeholder_caption", "Caption is still the synthesized placeholder."))
        if not image_url.startswith("https://"):
            failures.append(export_failure(slot_index, "no_https_url", "Image URL must be an https Cloudinary URL."))
        if caption and len(caption) < 30:
            warnings.append(export_warning(slot_index, "short_caption", "Caption is shorter than 30 characters."))
        if len(caption) > 2200:
            warnings.append(export_warning(slot_index, "long_caption", "Caption is longer than Instagram's 2200 character limit."))
        if not asset.get("hashtags") and not asset.get("first_comment"):
            warnings.append(export_warning(slot_index, "missing_hashtags", "No hashtags or first comment provided."))
        if not asset.get("alt_text"):
            warnings.append(export_warning(slot_index, "missing_alt_text", "No alt text provided."))
        if post_group_id:
            try:
                group_orders.setdefault(post_group_id, []).append(int(carousel_order))
            except (TypeError, ValueError):
                warnings.append(export_warning(slot_index, "carousel_order_missing", "Carousel item is missing a numeric order."))
        rows.append({
            "slot_index": slot_index,
            "date": str(slot.get("date", "")),
            "time": str(slot.get("time", "")),
            "dow": str(slot.get("dow", "")),
            "scheduled_at_iso": scheduled_at.isoformat() if scheduled_at else "",
            "account_handle": account_handle or "",
            "brand": brand,
            "post_group_id": post_group_id,
            "carousel_order": carousel_order if post_group_id else "",
            "media_type": asset.get("media_type") or "image",
            "image_url": image_url,
            "image_key": asset.get("image_key") or "",
            "asset_id": asset.get("id") or "",
            "post_id": asset.get("post_id") or "",
            "variation": asset.get("variation") or "",
            "content_role": asset.get("content_role") or infer_content_role(asset),
            "source": slot.get("source") or asset.get("source") or "",
            "caption": caption,
            "hashtags": asset.get("hashtags") or "",
            "alt_text": asset.get("alt_text") or "",
            "first_comment": asset.get("first_comment") or "",
            "notes": asset.get("notes") or "",
            "vista_datetime": vista_datetime(str(slot.get("date", "")), str(slot.get("time", "")), timezone)
            if scheduled_at else "",
        })
    for group, orders in group_orders.items():
        if not orders:
            continue
        expected = list(range(min(orders), max(orders) + 1))
        if sorted(orders) != expected:
            first_slot = next(row["slot_index"] for row in rows if row["post_group_id"] == group)
            warnings.append(export_warning(first_slot, "carousel_order_gap", f"Carousel group {group} has order gaps."))
    manifest = export_manifest(
        brand=brand,
        exported_at=exported_at,
        timezone=timezone,
        rows=rows,
        warnings=warnings,
        failures=failures or None,
    )
    return rows, manifest


def export_plan_csv(
    *,
    root: pathlib.Path,
    brand: str,
    slots: list[dict],
    timezone: str = "America/New_York",
    now: datetime | None = None,
) -> dict:
    brand = normalize_brand(brand)
    export_now = now or datetime.now(ZoneInfo(timezone))
    if export_now.tzinfo is None:
        export_now = export_now.replace(tzinfo=ZoneInfo(timezone))
    else:
        export_now = export_now.astimezone(ZoneInfo(timezone))
    timestamp = export_now.strftime("%Y%m%d-%H%M%S")
    exported_at = export_now.isoformat()
    rows, manifest = build_export_rows(brand=brand, slots=slots, timezone=timezone, exported_at=exported_at)
    if manifest.get("failures"):
        raise ExportValidationError(manifest)

    export_parent = root / "OUTPUT" / "EXPORTS" / brand
    export_parent.mkdir(parents=True, exist_ok=True)
    export_dir = export_parent / timestamp
    if export_dir.exists():
        suffix = 1
        while (export_parent / f"{timestamp}-{suffix}").exists():
            suffix += 1
        export_dir = export_parent / f"{timestamp}-{suffix}"
        timestamp = export_dir.name
    csv_path = export_dir / f"vista_plan_{brand}_{timestamp}.csv"
    full_csv_path = export_dir / f"vista_plan_{brand}_{timestamp}.full.csv"
    plan_path = export_dir / "plan.json"
    manifest_path = export_dir / "manifest.json"
    tmp_dir = export_parent / f".{timestamp}.tmp"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)
    tmp_csv_path = tmp_dir / csv_path.name
    tmp_full_csv_path = tmp_dir / full_csv_path.name
    tmp_plan_path = tmp_dir / "plan.json"
    tmp_manifest_path = tmp_dir / "manifest.json"
    with tmp_csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerows([
            [row["caption"], row["media_type"], row["image_url"], row["vista_datetime"]]
            for row in rows
        ])
    with tmp_full_csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FULL_EXPORT_HEADER)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in FULL_EXPORT_HEADER})
    tmp_plan_path.write_text(json.dumps({"brand": brand, "slots": slots}, indent=2), encoding="utf-8")
    tmp_manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    tmp_dir.rename(export_dir)
    return {
        "csv_path": rel_to_root(csv_path, root),
        "full_csv_path": rel_to_root(full_csv_path, root),
        "plan_path": rel_to_root(plan_path, root),
        "manifest_path": rel_to_root(manifest_path, root),
        "row_count": len(rows),
        "warnings": manifest["warnings"],
    }


def export_saved_plan_csv(*, conn: sqlite3.Connection, root: pathlib.Path, brand: str) -> dict:
    blocking = unacknowledged_error_conflicts(conn, brand=brand, root=root)
    if blocking:
        raise ConflictValidationError(blocking)
    plan = plan_from_db(conn, brand=brand)
    if not plan:
        raise ValueError(f"No saved plan for brand {normalize_brand(brand)}. Open the planner first.")
    return export_plan_csv(root=root, brand=normalize_brand(brand), slots=plan["slots"])


ADMIN_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Savora Content Pool</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Geist:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
@font-face {
  font-family: 'Gambarino';
  src: url('https://cdn.fontshare.com/wf/BTAI25FGRLTWEY2FPZ45OGYS24L6TDR7/2JJK7RTL3HCF4HJKMZBABCBLDYK6N3XT/2Z7I7ONFH3JZ4AMMZNLOATONAIDFIEPL.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
:root {
  --background:#00060B;
  --background-deep:#010908;
  --background-elevated:#062423;
  --foreground:#D9D4CE;
  --foreground-bright:#F2EFEB;
  --muted:#7B9693;
  --accent:#C2612C;
  --accent-hover:#D4713A;
  --teal:#4FD3D1;
  --brand:#C2612C;
  --surface:rgba(255,255,255,.03);
  --surface-hover:rgba(255,255,255,.06);
  --glass:rgba(255,255,255,.05);
  --glass-hover:rgba(255,255,255,.09);
  --glass-border:rgba(255,255,255,.10);
  --border:rgba(255,255,255,.06);
  --border-hover:rgba(255,255,255,.12);
  --accent-shadow:194,97,44;
}
* { box-sizing:border-box; }
html { color-scheme:dark; }
body {
  margin:0;
  min-height:100vh;
  background:
    radial-gradient(ellipse 58% 46% at 14% 10%, rgba(20,90,85,.30), transparent 66%),
    radial-gradient(ellipse 54% 42% at 86% 88%, rgba(15,70,68,.24), transparent 66%),
    radial-gradient(ellipse 34% 22% at 74% 4%, rgba(194,97,44,.10), transparent 70%),
    linear-gradient(180deg, #00060B 0%, #00090A 48%, #010908 100%),
    var(--background);
  color:var(--foreground);
  font-family:Geist,Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  overflow-x:hidden;
}
body::before {
  content:"";
  position:fixed;
  inset:-20%;
  z-index:-2;
  pointer-events:none;
  background:
    radial-gradient(ellipse 40% 35% at 20% 30%, rgba(25,110,100,.55), transparent 65%),
    radial-gradient(ellipse 35% 30% at 80% 70%, rgba(18,85,80,.45), transparent 65%),
    radial-gradient(ellipse 30% 25% at 60% 15%, rgba(30,120,110,.35), transparent 65%);
  filter:blur(70px);
  animation:aurora-drift 36s ease-in-out infinite alternate;
}
body::after {
  content:"";
  position:fixed;
  inset:0;
  z-index:-1;
  pointer-events:none;
  opacity:.06;
  mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.6 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
}
@keyframes aurora-drift {
  0% { transform:translate3d(-4%,-2%,0) scale(1.05); }
  50% { transform:translate3d(3%,2%,0) scale(1.15); }
  100% { transform:translate3d(-2%,3%,0) scale(1.08); }
}
@keyframes gloss-sweep {
  0%, 30% { transform:translateX(-54%) rotate(0.001deg); opacity:.08; }
  58% { opacity:.34; }
  78%, 100% { transform:translateX(54%) rotate(0.001deg); opacity:.08; }
}
@media (prefers-reduced-motion:reduce) { body::before, .gloss::after, aside::after, .toolbar::after, .card::after, .pool-list::after, .calendar-panel::after { animation:none; } }
header {
  position:sticky;
  top:0;
  z-index:5;
  display:flex;
  justify-content:space-between;
  gap:18px;
  align-items:end;
  padding:22px clamp(18px,3vw,44px);
  border-bottom:1px solid var(--border);
  background:
    linear-gradient(180deg, rgba(255,255,255,.055), transparent 64%),
    rgba(0,6,11,.78);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.08), 0 18px 70px rgba(0,0,0,.22);
  backdrop-filter:blur(22px) saturate(1.15);
}
h1 {
  margin:0;
  color:var(--foreground-bright);
  font-family:Gambarino,Fraunces,Georgia,serif;
  font-size:clamp(42px,6vw,92px);
  font-weight:400;
  line-height:.92;
  letter-spacing:-.045em;
  word-spacing:-.05em;
}
.sub { margin-top:10px; color:var(--muted); max-width:760px; line-height:1.55; font-size:15px; }
.accent-word {
  color:var(--accent);
  font-style:italic;
  text-shadow:0 0 34px rgba(var(--accent-shadow),.18);
}
.actions { display:flex; flex-wrap:wrap; gap:8px; justify-content:flex-end; }
button, select, input {
  min-height:40px;
  border:1px solid var(--glass-border);
  border-radius:999px;
  background:var(--glass);
  color:var(--foreground);
  font:inherit;
  font-size:13px;
  font-weight:700;
  outline:none;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.08);
  backdrop-filter:blur(18px);
}
select, input { padding:0 13px; }
button { cursor:pointer; padding:0 13px; transition:transform .2s ease, border-color .2s ease, background .2s ease, box-shadow .2s ease; }
button:hover { border-color:var(--border-hover); background:var(--glass-hover); transform:scale(.985); }
button.primary,
button.hot {
  border-color:rgba(255,255,255,.15);
  background:
    linear-gradient(180deg, rgba(255,255,255,.18) 0%, rgba(255,255,255,0) 45%, rgba(0,0,0,.18) 100%),
    linear-gradient(135deg, #E28A4A 0%, var(--accent) 55%, #7A3A13 100%);
  background-blend-mode:overlay,normal;
  color:var(--foreground-bright);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.25), 0 0 24px rgba(var(--accent-shadow),.25);
}
button.brand {
  border-color:color-mix(in oklab,var(--brand) 55%,rgba(255,255,255,.16));
  background:linear-gradient(135deg, color-mix(in oklab,var(--brand) 78%,#fff 10%), var(--brand));
  color:#fff;
  box-shadow:0 0 24px color-mix(in oklab,var(--brand) 28%,transparent);
}
main { display:grid; grid-template-columns:280px minmax(0,1fr); gap:18px; padding:18px clamp(14px,2vw,28px) 34px; }
aside {
  position:sticky;
  top:126px;
  align-self:start;
  border:1px solid var(--glass-border);
  border-radius:1.5rem;
  background:var(--glass);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.08), 0 24px 80px rgba(0,0,0,.18);
  backdrop-filter:blur(22px);
  overflow:hidden;
  isolation:isolate;
}
.brand-row {
  display:flex;
  justify-content:space-between;
  gap:10px;
  width:100%;
  min-height:54px;
  padding:13px 15px;
  border:0;
  border-bottom:1px solid var(--border);
  border-radius:0;
  background:transparent;
  color:var(--foreground);
  text-align:left;
  box-shadow:none;
}
.brand-row.active {
  background:linear-gradient(90deg, color-mix(in oklab,var(--brand) 22%,transparent), rgba(255,255,255,.04));
  color:var(--foreground-bright);
  box-shadow:inset 3px 0 0 var(--brand);
}
.brand-row small { color:var(--muted); font-weight:800; font-variant-numeric:tabular-nums; }
.toolbar {
  display:flex;
  flex-wrap:wrap;
  gap:10px;
  margin-bottom:16px;
  padding:12px;
  border:1px solid var(--glass-border);
  border-radius:1.5rem;
  background:rgba(255,255,255,.035);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.08), 0 18px 60px rgba(0,0,0,.14);
  backdrop-filter:blur(22px);
  position:relative;
  isolation:isolate;
  overflow:hidden;
}
.toolbar input { flex:1 1 280px; min-width:220px; }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(238px,1fr)); gap:16px; }
.card {
  display:grid;
  gap:0;
  border:1px solid var(--glass-border);
  border-radius:1.5rem;
  background:var(--glass);
  overflow:hidden;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.08), 0 18px 70px rgba(0,0,0,.12);
  backdrop-filter:blur(22px);
  transition:transform .25s ease, border-color .25s ease, background .25s ease, box-shadow .25s ease;
  position:relative;
  isolation:isolate;
}
.card::after,
.toolbar::after,
.pool-list::after,
.calendar-panel::after,
aside::after {
  content:"";
  position:absolute;
  inset:-70%;
  pointer-events:none;
  z-index:1;
  background:linear-gradient(112deg, transparent 40%, rgba(255,255,255,.16) 48%, transparent 57%);
  mix-blend-mode:screen;
  opacity:.28;
  animation:gloss-sweep 9s cubic-bezier(.2,.8,.2,1) infinite;
}
.toolbar > *, .card > *, .pool-list > *, .calendar-panel > *, aside > * { position:relative; z-index:2; }
.card:hover {
  transform:translateY(-2px);
  border-color:var(--border-hover);
  background:var(--glass-hover);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.1), 0 16px 48px -16px rgba(194,97,44,.20);
}
.thumb { aspect-ratio:4/5; width:100%; object-fit:cover; background:var(--background-elevated); display:block; }
.body { display:grid; gap:10px; padding:14px; }
h2 { margin:0; color:var(--foreground-bright); font-family:Gambarino,Fraunces,Georgia,serif; font-size:23px; font-weight:400; line-height:1.02; letter-spacing:-.035em; overflow-wrap:anywhere; }
.meta { color:var(--muted); font-size:12px; line-height:1.4; overflow-wrap:anywhere; }
.chips { display:flex; flex-wrap:wrap; gap:5px; }
.chip { display:inline-flex; min-height:24px; align-items:center; padding:3px 8px; border:1px solid var(--glass-border); border-radius:999px; background:rgba(255,255,255,.03); color:var(--muted); font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:.12em; }
.status-picked { outline:2px solid color-mix(in oklab,var(--brand) 52%,transparent); }
.status-rejected { opacity:.58; }
.status-duplicate { outline:2px solid rgba(194,97,44,.42); }
.stars { display:grid; grid-template-columns:repeat(5,1fr); gap:5px; }
.stars button { min-height:32px; padding:0; border-radius:999px; color:var(--muted); }
.card-actions { display:grid; grid-template-columns:1fr 1fr; gap:6px; }
.card-actions button { min-height:36px; font-size:12px; }
.empty { padding:40px; border:1px dashed var(--glass-border); border-radius:1.5rem; background:var(--glass); color:var(--muted); text-align:center; }
.view-tabs { display:flex; gap:8px; margin-bottom:12px; }
.view-tabs button.active {
  border-color:rgba(255,255,255,.16);
  background:
    linear-gradient(180deg, rgba(255,255,255,.18), rgba(255,255,255,0) 46%),
    linear-gradient(135deg, #E28A4A 0%, var(--accent) 62%, #7A3A13 100%);
  color:var(--foreground-bright);
  box-shadow:0 0 26px rgba(var(--accent-shadow),.22), inset 0 1px 0 rgba(255,255,255,.22);
}
.planner { display:none; grid-template-columns:280px minmax(0,1fr); gap:16px; }
.planner.active { display:grid; }
.pool-list, .calendar-panel {
  min-height:520px;
  border:1px solid var(--glass-border);
  border-radius:1.5rem;
  background:var(--glass);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.08), 0 24px 80px rgba(0,0,0,.16);
  backdrop-filter:blur(22px);
  overflow:hidden;
  position:relative;
  isolation:isolate;
}
.panel-head { display:flex; align-items:center; justify-content:space-between; gap:10px; padding:13px 14px; border-bottom:1px solid var(--border); }
.panel-head h3 { margin:0; color:var(--foreground-bright); font-size:12px; font-weight:800; letter-spacing:.18em; text-transform:uppercase; }
.pool-items { display:grid; gap:8px; max-height:70vh; overflow:auto; padding:10px; }
.mini-asset { display:grid; grid-template-columns:52px 1fr; gap:9px; align-items:center; padding:7px; border:1px solid var(--border); border-radius:1rem; background:rgba(255,255,255,.035); cursor:grab; }
.mini-asset img { width:52px; aspect-ratio:4/5; object-fit:cover; border-radius:.65rem; background:var(--background-elevated); }
.mini-asset strong { display:block; color:var(--foreground-bright); font-size:12px; line-height:1.2; }
.mini-asset span { display:block; margin-top:3px; color:var(--muted); font-size:10px; line-height:1.25; text-transform:uppercase; letter-spacing:.12em; }
.calendar-grid { display:grid; grid-template-columns:repeat(3,minmax(160px,1fr)); gap:5px; padding:10px; }
.slot { min-height:250px; border:1px solid var(--border); border-radius:1rem; background:rgba(255,255,255,.025); overflow:hidden; }
.slot.drag-over { border-color:var(--brand); box-shadow:0 0 0 1px var(--brand),0 0 28px color-mix(in oklab,var(--brand) 34%,transparent); }
.slot-date { display:flex; justify-content:space-between; gap:8px; padding:8px 9px; color:var(--muted); font-size:10px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
.slot img { width:100%; aspect-ratio:4/5; object-fit:cover; display:block; }
.slot-body { display:grid; gap:6px; padding:9px; }
.slot-title { color:var(--foreground-bright); font-size:12px; font-weight:800; line-height:1.25; }
.carousel-chip { border-color:color-mix(in oklab,var(--brand) 68%,rgba(255,255,255,.18)); color:var(--foreground-bright); }
.carousel-strip { border:1px solid var(--border); border-radius:.85rem; background:rgba(255,255,255,.03); padding:8px; }
.carousel-head { display:flex; justify-content:space-between; align-items:center; gap:8px; color:var(--muted); font-size:10px; font-weight:900; letter-spacing:.12em; text-transform:uppercase; }
.carousel-head button { min-height:28px; padding:0 9px; font-size:10px; }
.carousel-items { display:flex; gap:7px; margin-top:8px; overflow-x:auto; padding-bottom:3px; }
.carousel-item { flex:0 0 72px; border:1px solid var(--border); border-radius:.75rem; background:rgba(0,0,0,.16); padding:5px; display:grid; gap:4px; cursor:grab; }
.carousel-item img { width:100%; aspect-ratio:4/5; object-fit:cover; border-radius:.5rem; }
.carousel-item select { width:100%; min-height:25px; padding:0 4px; border-radius:.55rem; font-size:9px; }
.carousel-item button { min-height:24px; padding:0; border-radius:.55rem; }
.carousel-drop { flex:0 0 72px; min-height:112px; display:grid; place-items:center; border:1px dashed var(--border-hover); border-radius:.75rem; color:var(--muted); font-size:10px; text-transform:uppercase; letter-spacing:.1em; }
.caption { width:100%; min-height:74px; resize:vertical; border:1px solid var(--border); border-radius:.85rem; background:rgba(0,0,0,.18); color:var(--foreground); padding:8px; font:inherit; font-size:11px; line-height:1.4; outline:none; }
.caption-tools { display:flex; gap:6px; }
.caption-tools button { min-height:30px; font-size:10px; }
.conflict-banner { display:flex; align-items:center; justify-content:space-between; gap:10px; margin:0 0 12px; padding:10px 12px; border:1px solid rgba(255,255,255,.12); border-radius:1rem; background:rgba(255,255,255,.05); color:var(--foreground-bright); box-shadow:inset 0 1px 0 rgba(255,255,255,.08); }
.conflict-banner.clean { color:var(--muted); }
.conflict-banner strong { font-size:12px; letter-spacing:.08em; text-transform:uppercase; }
.conflict-dot { display:inline-flex; min-width:22px; height:22px; align-items:center; justify-content:center; border-radius:999px; font-size:10px; font-weight:900; color:#fff; }
.conflict-dot.error { background:#B83232; box-shadow:0 0 18px rgba(184,50,50,.35); }
.conflict-dot.warning { background:#C9942E; box-shadow:0 0 18px rgba(201,148,46,.35); }
.slot-conflict-badges { position:absolute; top:38px; right:8px; z-index:3; display:flex; gap:4px; }
.slot { position:relative; }
.caption-modal { position:fixed; inset:0; z-index:20; display:grid; place-items:center; padding:20px; background:rgba(0,0,0,.62); backdrop-filter:blur(18px); }
.caption-modal[hidden] { display:none; }
.caption-dialog { width:min(760px,100%); max-height:86vh; overflow:auto; border:1px solid var(--glass-border); border-radius:1.5rem; background:#061313; box-shadow:0 40px 120px rgba(0,0,0,.5); padding:18px; }
.caption-dialog-head { display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:12px; }
.caption-dialog-head h3 { margin:0; color:var(--foreground-bright); font-family:Gambarino,Fraunces,Georgia,serif; font-size:28px; font-weight:400; }
.variant-list { display:grid; gap:10px; }
.variant-card { border:1px solid var(--border); border-radius:1rem; background:rgba(255,255,255,.04); padding:12px; display:grid; gap:10px; }
.variant-card p { margin:0; color:var(--foreground-bright); line-height:1.45; }
.conflict-card { border:1px solid var(--border); border-radius:1rem; background:rgba(255,255,255,.04); padding:12px; display:grid; gap:10px; opacity:1; }
.conflict-card.acknowledged { opacity:.55; }
.conflict-card p { margin:0; color:var(--foreground-bright); line-height:1.45; }
.conflict-actions { display:flex; flex-wrap:wrap; gap:6px; }
.variant-meta { display:flex; flex-wrap:wrap; gap:6px; align-items:center; color:var(--muted); font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:.12em; }
.toast { position:fixed; right:18px; bottom:18px; z-index:25; max-width:360px; border:1px solid var(--glass-border); border-radius:1rem; background:#061313; color:var(--foreground-bright); padding:12px 14px; box-shadow:0 22px 70px rgba(0,0,0,.42); }
.toast[hidden] { display:none; }
.slot.empty-slot { display:grid; place-items:center; color:var(--muted); font-size:11px; text-align:center; padding:12px; }
@media (max-width:820px) { header { align-items:start; flex-direction:column; } main { grid-template-columns:1fr; } aside { position:static; } }
@media (max-width:1100px) { .planner { grid-template-columns:1fr; } .calendar-grid { grid-template-columns:repeat(2,minmax(150px,1fr)); } }
@media (max-width:680px) { .calendar-grid { grid-template-columns:1fr; } }
</style>
</head>
<body>
<header>
  <div>
    <h1>Savora <span class="accent-word">operator</span></h1>
    <div class="sub">Internal command surface for content picks, duplicates, auto grid drafts, captions, and final CSV exports. Nothing posts automatically.</div>
  </div>
  <div class="actions">
    <button class="primary" onclick="indexNow()">Sync Library</button>
    <button onclick="loadAll()">Refresh</button>
  </div>
</header>
<main>
  <aside id="brands"></aside>
  <section>
    <div class="view-tabs">
      <button id="poolTab" class="active" onclick="setView('pool')">Review Pool</button>
      <button id="plannerTab" onclick="setView('planner')">Auto Grid Draft</button>
      <button class="primary" onclick="exportPlan()">Export Planned CSV</button>
    </div>
    <div id="poolView">
    <div class="toolbar">
      <select id="status" onchange="loadAssets()">
        <option value="all">All statuses</option>
        <option value="new">New</option>
        <option value="shortlisted">Shortlisted</option>
        <option value="picked">Picked</option>
        <option value="duplicate">Duplicate</option>
        <option value="rejected">Rejected</option>
      </select>
      <select id="minRating" onchange="loadAssets()">
        <option value="">Any rating</option>
        <option value="5">5 stars</option>
        <option value="4">4+ stars</option>
        <option value="3">3+ stars</option>
      </select>
      <input id="q" placeholder="Search subject, image key, angle" oninput="loadAssets()">
    </div>
    <div id="grid" class="grid"></div>
    </div>
    <div id="plannerView" class="planner">
      <div class="pool-list" ondragover="allowDrop(event)" ondrop="dropOnPool(event)">
        <div class="panel-head"><h3>Unused pool</h3><button onclick="loadPlanner(true)">Suggest</button></div>
        <div id="plannerPool" class="pool-items"></div>
      </div>
      <div class="calendar-panel">
        <div class="panel-head"><h3>Instagram grid draft</h3><div class="actions"><button onclick="addCustomSlot()">Add day</button><button onclick="clearPlanner()">Clear plan</button></div></div>
        <div id="conflictBanner"></div>
        <div id="calendarGrid" class="calendar-grid"></div>
      </div>
    </div>
  </section>
</main>
<div class="caption-modal" id="captionModal" hidden>
  <div class="caption-dialog">
    <div class="caption-dialog-head">
      <h3>Caption variants</h3>
      <button onclick="closeCaptionModal()">Close</button>
    </div>
    <div id="variantList" class="variant-list"></div>
  </div>
</div>
<div class="caption-modal" id="conflictModal" hidden>
  <div class="caption-dialog">
    <div class="caption-dialog-head">
      <h3>Planner conflicts</h3>
      <button onclick="closeConflictModal()">Close</button>
    </div>
    <div id="conflictList" class="variant-list"></div>
  </div>
</div>
<div class="toast" id="toast" hidden></div>
<script>
let activeBrand = "";
let debounce = 0;
let currentView = "pool";
let plannerSlots = [];
let plannerPool = [];
let planVersion = 0;
let saveTimer = null;
let saveInFlight = false;
let conflictData = { conflicts: [], summary: {} };
let conflictTimer = null;
function esc(s) {
  if (s === null || s === undefined) return "";
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
async function api(path, opts={}) {
  const res = await fetch(path, opts);
  const data = await res.json();
  if (!res.ok) {
    const err = new Error(data.error || res.statusText);
    err.status = res.status;
    err.payload = data;
    throw err;
  }
  return data;
}
function media(path) { return "/media/" + encodeURIComponent(path); }
function assetImage(asset) {
  if (!asset) return "";
  return asset.image_url || media(asset.pick_path || asset.image_path);
}
function defaultCarouselRole(asset) {
  const text = [asset.subject, asset.support, asset.format, asset.angle, asset.content_role].join(" ").toLowerCase();
  if (text.includes("quote") || text.includes("review") || text.includes("you already know")) return "quote";
  if (text.includes("name") || text.includes("typographic") || text.includes("cover")) return "story";
  if (text.includes("end")) return "end_card";
  return "dish";
}
function setView(view) {
  currentView = view;
  document.getElementById("poolTab").classList.toggle("active", view === "pool");
  document.getElementById("plannerTab").classList.toggle("active", view === "planner");
  document.getElementById("poolView").style.display = view === "pool" ? "block" : "none";
  document.getElementById("plannerView").classList.toggle("active", view === "planner");
  if (view === "planner" && !plannerSlots.length) loadPlanner();
}
function normalizePlan(data) {
  plannerSlots = Array.isArray(data.slots) ? data.slots : [];
  plannerPool = Array.isArray(data.pool) ? data.pool.map(item => item && item.asset ? item.asset : item) : [];
  planVersion = data.version || 0;
}
function schedulePlanSave() {
  if (!activeBrand || !plannerSlots.length) return;
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(savePlanNow, 500);
  scheduleConflictRefresh();
}
async function savePlanNow() {
  if (!activeBrand || !plannerSlots.length) return;
  if (saveInFlight) { schedulePlanSave(); return; }
  if (saveTimer) { clearTimeout(saveTimer); saveTimer = null; }
  saveInFlight = true;
  try {
    const res = await api("/api/plan", {
      method:"PUT",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ brand: activeBrand, version: planVersion, slots: plannerSlots, pool: plannerPool })
    });
    planVersion = res.version;
    scheduleConflictRefresh();
  } catch (e) {
    if (e.status === 409) {
      alert("Plan was edited in another tab. Reloading.");
      await loadPlanner(false);
    } else {
      console.error("plan save failed", e);
    }
  } finally {
    saveInFlight = false;
  }
}
async function switchBrand(button) {
  if (saveTimer) await savePlanNow();
  activeBrand = button.dataset.brand;
  document.documentElement.style.setProperty("--brand", button.dataset.accent);
  plannerSlots = [];
  plannerPool = [];
  planVersion = 0;
  conflictData = { conflicts: [], summary: {} };
  await loadAll();
}
async function loadBrands() {
  const data = await api("/api/brands");
  const el = document.getElementById("brands");
  if (!activeBrand && data.brands.length) activeBrand = data.brands[0].brand;
  el.innerHTML = data.brands.map(b => `
    <button class="brand-row ${b.brand === activeBrand ? "active" : ""}" style="--brand:${esc(b.theme.accent)}" data-brand="${esc(b.brand)}" data-accent="${esc(b.theme.accent)}" onclick="switchBrand(this)">
      <span>${esc(b.label)}</span><small>${esc(b.total)}</small>
    </button>
  `).join("");
  const current = data.brands.find(b => b.brand === activeBrand);
  if (current) document.documentElement.style.setProperty("--brand", current.theme.accent);
}
async function loadAssets() {
  clearTimeout(debounce);
  debounce = setTimeout(async () => {
    const status = document.getElementById("status").value;
    const minRating = document.getElementById("minRating").value;
    const q = encodeURIComponent(document.getElementById("q").value.trim());
    const qs = new URLSearchParams({ brand: activeBrand, status, q });
    if (minRating) qs.set("min_rating", minRating);
    const data = await api("/api/content-pool?" + qs.toString());
    renderAssets(data.assets);
  }, 120);
}
function renderAssets(assets) {
  const el = document.getElementById("grid");
  if (!assets.length) { el.innerHTML = `<div class="empty">No assets match this view.</div>`; return; }
  el.innerHTML = assets.map(a => `
    <article class="card status-${esc(a.status)}">
      <img class="thumb" src="${esc(media(a.image_path))}" loading="lazy">
      <div class="body">
        <h2>${esc(a.subject || a.post_id)}</h2>
        <div class="meta">${esc(a.post_id)} · ${esc(a.variation)} · ${esc(a.image_key || "no image key")}</div>
        <div class="chips">
          <span class="chip">${esc(a.status)}</span>
          ${a.rating ? `<span class="chip">${esc(a.rating)} stars</span>` : ""}
          ${a.duplicate_group_id ? `<span class="chip">dup ${esc(a.duplicate_group_id)}</span>` : ""}
        </div>
        <div class="stars">${[1,2,3,4,5].map(n => `<button data-asset-id="${esc(a.id)}" onclick="rate(this.dataset.assetId,${n})">${n}</button>`).join("")}</div>
        <div class="card-actions">
          <button class="brand" data-asset-id="${esc(a.id)}" onclick="pick(this.dataset.assetId)">Pick</button>
          <button data-asset-id="${esc(a.id)}" data-post-id="${esc(a.post_id)}" onclick="duplicate(this.dataset.assetId,this.dataset.postId)">Duplicate</button>
          <button data-asset-id="${esc(a.id)}" onclick="shortlist(this.dataset.assetId)">Shortlist</button>
          <button class="hot" data-asset-id="${esc(a.id)}" onclick="reject(this.dataset.assetId)">Reject</button>
        </div>
      </div>
    </article>
  `).join("");
}
function renderMiniAsset(asset) {
  if (!asset) return "";
  return `
      <div class="mini-asset" draggable="true" data-asset-id="${esc(asset.id)}" ondragstart="dragAsset(event,this.dataset.assetId)">
      <img src="${esc(assetImage(asset))}" loading="lazy">
      <div><strong>${esc(asset.subject || asset.post_id)}</strong><span>${esc(asset.content_role || asset.status)} · ${esc(asset.rating || 0)} stars</span></div>
    </div>
  `;
}
async function loadPlanner(force=false) {
  if (force) {
    const data = await api("/api/plan/regenerate?brand=" + encodeURIComponent(activeBrand), { method:"POST" });
    normalizePlan(data);
    renderPlanner();
    refreshConflicts();
    return;
  }
  try {
    const data = await api("/api/plan?brand=" + encodeURIComponent(activeBrand));
    normalizePlan(data);
  } catch (e) {
    if (e.status === 404) {
      const data = await api("/api/plan/regenerate?brand=" + encodeURIComponent(activeBrand), { method:"POST" });
      normalizePlan(data);
    } else {
      throw e;
    }
  }
  renderPlanner();
  refreshConflicts();
}
function slotConflictBadges(slot) {
  const slotIndex = Number(slot.slot_index);
  const active = (conflictData.conflicts || []).filter(conflict => !conflict.acknowledged && (conflict.slot_indices || []).map(Number).includes(slotIndex));
  if (!active.length) return "";
  const hasError = active.some(conflict => conflict.severity === "error");
  const hasWarning = active.some(conflict => conflict.severity === "warning");
  return `<div class="slot-conflict-badges">${hasError ? `<span class="conflict-dot error">!</span>` : ""}${hasWarning ? `<span class="conflict-dot warning">!</span>` : ""}</div>`;
}
function renderPlanner() {
  document.getElementById("plannerPool").innerHTML = plannerPool.length
    ? plannerPool.map(renderMiniAsset).join("")
    : `<div class="empty">No unused assets in this plan.</div>`;
  document.getElementById("calendarGrid").innerHTML = plannerSlots.map((slot, idx) => {
    const asset = slot.asset;
    if (!asset) {
      return `<div class="slot empty-slot" ondragover="allowDrop(event)" ondrop="dropOnSlot(event,${idx})"><div>${esc(slot.dow)} ${esc(slot.date)}<br>${esc(slot.time)}<br>Drop a post here</div></div>`;
    }
    return `
      <div class="slot" draggable="true" ondragstart="dragSlot(event,${idx})" ondragover="allowDrop(event)" ondragleave="this.classList.remove('drag-over')" ondrop="dropOnSlot(event,${idx})">
        <div class="slot-date"><span>${esc(slot.dow)} ${esc(slot.date.slice(5))}</span><span>${esc(slot.time)}</span></div>
        ${slotConflictBadges(slot)}
        <img src="${esc(assetImage(asset))}" loading="lazy">
        <div class="slot-body">
          <div class="slot-title">${esc(asset.subject || asset.post_id)}</div>
          <div class="chips"><span class="chip ${slot.carousel_items && slot.carousel_items.length ? "carousel-chip" : ""}">${esc(slot.carousel_items && slot.carousel_items.length ? "carousel" : (slot.slot_kind || asset.content_role || "single"))}</span>${asset.rating ? `<span class="chip">${esc(asset.rating)} stars</span>` : ""}</div>
          ${renderCarouselStrip(slot, idx)}
          <textarea class="caption" oninput="plannerSlots[${idx}].asset.caption_draft=this.value; plannerSlots[${idx}].caption_draft=this.value; schedulePlanSave();">${esc(asset.caption_draft || "")}</textarea>
          <div class="caption-tools">
            <button class="brand" onclick="generateCaption(${idx})">✨ Generate</button>
            <button onclick="openCaptionModal(${idx})" ${slot.caption_variants && slot.caption_variants.length ? "" : "disabled"}>Pick variant ▾</button>
          </div>
        </div>
      </div>
    `;
  }).join("");
}
function renderCarouselStrip(slot, slotIdx) {
  const items = slot.carousel_items || [];
  return `
    <div class="carousel-strip" ondragover="allowDrop(event)" ondrop="dropOnCarousel(event,${slotIdx})">
      <div class="carousel-head"><span>Carousel (${items.length + 1} items)</span><button onclick="quickAddCarousel(${slotIdx})">+ Add to carousel</button></div>
      <div class="carousel-items">
        ${items.map((item, itemIdx) => `
          <div class="carousel-item" draggable="true" ondragstart="dragCarouselItem(event,${slotIdx},${itemIdx})" ondragover="allowDrop(event)" ondrop="dropOnCarouselItem(event,${slotIdx},${itemIdx})">
            <img src="${esc(assetImage(item.asset))}" loading="lazy">
            <select onchange="setCarouselRole(${slotIdx},${itemIdx},this.value)">
              ${["dish","quote","story","end_card"].map(role => `<option value="${role}" ${role === item.role ? "selected" : ""}>${role}</option>`).join("")}
            </select>
            <button onclick="removeCarouselItem(${slotIdx},${itemIdx})">×</button>
          </div>
        `).join("")}
        <div class="carousel-drop">drop here</div>
      </div>
    </div>
  `;
}
function scheduleConflictRefresh() {
  if (!activeBrand || currentView !== "planner") return;
  if (conflictTimer) clearTimeout(conflictTimer);
  conflictTimer = setTimeout(refreshConflicts, 800);
}
async function refreshConflicts() {
  if (!activeBrand || currentView !== "planner") return;
  try {
    conflictData = await api("/api/conflicts?brand=" + encodeURIComponent(activeBrand));
    renderConflictBanner();
    renderPlanner();
  } catch (e) {
    console.error("conflict refresh failed", e);
  }
}
function renderConflictBanner() {
  const el = document.getElementById("conflictBanner");
  if (!el) return;
  const conflicts = conflictData.conflicts || [];
  const active = conflicts.filter(conflict => !conflict.acknowledged);
  if (!conflicts.length) {
    el.innerHTML = `<div class="conflict-banner clean"><strong>No conflicts</strong><span>Saved grid is clear.</span></div>`;
    return;
  }
  const errors = active.filter(conflict => conflict.severity === "error").length;
  const warnings = active.filter(conflict => conflict.severity === "warning").length;
  const label = errors ? `${errors} conflict${errors === 1 ? "" : "s"} need attention` : warnings ? `${warnings} warning${warnings === 1 ? "" : "s"} to review` : "All conflicts acknowledged";
  el.innerHTML = `<div class="conflict-banner ${active.length ? "" : "clean"}"><strong>${esc(label)}</strong><button onclick="openConflictModal()">Review</button></div>`;
}
function closeConflictModal() {
  document.getElementById("conflictModal").hidden = true;
}
function conflictSlots(conflict) {
  const indices = new Set((conflict.slot_indices || []).map(Number));
  return plannerSlots
    .filter(slot => indices.has(Number(slot.slot_index)))
    .map(slot => {
      const asset = slot.asset || {};
      return `<span class="chip">${esc(slot.date)} ${esc(slot.time)} · ${esc(asset.subject || asset.post_id || "slot")}</span>`;
    }).join("");
}
function openConflictModal() {
  const conflicts = conflictData.conflicts || [];
  document.getElementById("conflictList").innerHTML = conflicts.length ? conflicts.map(conflict => `
    <article class="conflict-card ${conflict.acknowledged ? "acknowledged" : ""}">
      <div class="variant-meta">
        <span class="conflict-dot ${esc(conflict.severity)}">!</span>
        <span>${esc(conflict.severity)}</span>
        <span>${esc(conflict.code)}</span>
        ${conflict.acknowledged ? `<span class="chip">acknowledged</span>` : ""}
      </div>
      <p>${esc(conflict.message)}</p>
      <div class="chips">${conflictSlots(conflict)}</div>
      <div class="conflict-actions">
        ${conflict.suggested_action && !["none","add_brand_csv"].includes(conflict.suggested_action) ? `<button class="brand" onclick="autoFixConflict('${esc(conflict.key)}','${esc(conflict.suggested_action)}')">Auto-fix</button>` : ""}
        ${conflict.acknowledged ? `<button onclick="revokeConflict('${esc(conflict.key)}')">Revoke ack</button>` : `<button onclick="ackConflict('${esc(conflict.key)}')">Acknowledge</button>`}
      </div>
    </article>
  `).join("") : `<div class="empty">No conflicts.</div>`;
  document.getElementById("conflictModal").hidden = false;
}
async function ackConflict(key) {
  conflictData = await api("/api/conflicts/acknowledge", {
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body: JSON.stringify({ brand: activeBrand, conflict_key: key })
  });
  renderConflictBanner();
  openConflictModal();
  renderPlanner();
}
async function revokeConflict(key) {
  conflictData = await api("/api/conflicts/revoke", {
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body: JSON.stringify({ brand: activeBrand, conflict_key: key })
  });
  renderConflictBanner();
  openConflictModal();
  renderPlanner();
}
async function autoFixConflict(key, action) {
  const result = await api("/api/conflicts/auto-fix", {
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body: JSON.stringify({ brand: activeBrand, conflict_key: key, action })
  });
  normalizePlan(result.plan);
  conflictData = result.conflicts;
  renderConflictBanner();
  openConflictModal();
  renderPlanner();
}
function allowDrop(event) {
  event.preventDefault();
  event.currentTarget.classList.add("drag-over");
}
function dragAsset(event, assetId) {
  event.dataTransfer.setData("text/plain", JSON.stringify({ type:"pool", assetId }));
}
function dragSlot(event, slotIdx) {
  event.dataTransfer.setData("text/plain", JSON.stringify({ type:"slot", slotIdx }));
}
function dragCarouselItem(event, slotIdx, itemIdx) {
  event.stopPropagation();
  event.dataTransfer.setData("text/plain", JSON.stringify({ type:"carousel", slotIdx, itemIdx }));
}
function renumberCarousel(slot) {
  (slot.carousel_items || []).forEach((item, idx) => item.item_order = idx + 2);
  if (slot.carousel_items && slot.carousel_items.length) slot.slot_kind = "carousel";
}
function appendCarouselItem(slotIdx, asset, role=null) {
  const slot = plannerSlots[slotIdx];
  if (!slot || !slot.asset) return false;
  slot.carousel_items = slot.carousel_items || [];
  if (slot.carousel_items.length >= 9) {
    alert("Carousel max is 10 images total.");
    return false;
  }
  slot.carousel_items.push({ item_order: slot.carousel_items.length + 2, asset, role: role || defaultCarouselRole(asset) });
  renumberCarousel(slot);
  return true;
}
function dropOnSlot(event, targetIdx) {
  event.preventDefault();
  event.currentTarget.classList.remove("drag-over");
  const drag = JSON.parse(event.dataTransfer.getData("text/plain") || "{}");
  const targetAsset = plannerSlots[targetIdx].asset;
  if (drag.type === "pool") {
    const sourceIdx = plannerPool.findIndex(asset => asset.id === drag.assetId);
    if (sourceIdx < 0) return;
    const [asset] = plannerPool.splice(sourceIdx, 1);
    if (targetAsset) plannerPool.unshift(targetAsset);
    plannerSlots[targetIdx].asset = asset;
  }
  if (drag.type === "slot") {
    const sourceIdx = Number(drag.slotIdx);
    const sourceAsset = plannerSlots[sourceIdx] && plannerSlots[sourceIdx].asset;
    if (sourceIdx === targetIdx || !sourceAsset) return;
    plannerSlots[sourceIdx].asset = targetAsset || null;
    plannerSlots[targetIdx].asset = sourceAsset;
  }
  schedulePlanSave();
  renderPlanner();
}
function dropOnCarousel(event, targetIdx) {
  event.preventDefault();
  event.stopPropagation();
  event.currentTarget.classList.remove("drag-over");
  const drag = JSON.parse(event.dataTransfer.getData("text/plain") || "{}");
  if (drag.type === "pool") {
    const sourceIdx = plannerPool.findIndex(asset => asset.id === drag.assetId);
    if (sourceIdx < 0) return;
    const [asset] = plannerPool.splice(sourceIdx, 1);
    if (!appendCarouselItem(targetIdx, asset)) plannerPool.unshift(asset);
  }
  if (drag.type === "slot") {
    const sourceIdx = Number(drag.slotIdx);
    const sourceAsset = plannerSlots[sourceIdx] && plannerSlots[sourceIdx].asset;
    if (sourceIdx === targetIdx || !sourceAsset) return;
    plannerSlots[sourceIdx].asset = null;
    if (!appendCarouselItem(targetIdx, sourceAsset, "dish")) plannerSlots[sourceIdx].asset = sourceAsset;
  }
  if (drag.type === "carousel") {
    const sourceSlot = plannerSlots[Number(drag.slotIdx)];
    const sourceItems = sourceSlot && sourceSlot.carousel_items;
    if (!sourceItems) return;
    const [item] = sourceItems.splice(Number(drag.itemIdx), 1);
    renumberCarousel(sourceSlot);
    if (!appendCarouselItem(targetIdx, item.asset, item.role)) sourceItems.splice(Number(drag.itemIdx), 0, item);
  }
  schedulePlanSave();
  renderPlanner();
}
function dropOnCarouselItem(event, targetSlotIdx, targetItemIdx) {
  event.preventDefault();
  event.stopPropagation();
  const drag = JSON.parse(event.dataTransfer.getData("text/plain") || "{}");
  if (drag.type !== "carousel" || Number(drag.slotIdx) !== targetSlotIdx) {
    dropOnCarousel(event, targetSlotIdx);
    return;
  }
  const items = plannerSlots[targetSlotIdx].carousel_items || [];
  const [item] = items.splice(Number(drag.itemIdx), 1);
  items.splice(targetItemIdx, 0, item);
  renumberCarousel(plannerSlots[targetSlotIdx]);
  schedulePlanSave();
  renderPlanner();
}
function dropOnPool(event) {
  event.preventDefault();
  const drag = JSON.parse(event.dataTransfer.getData("text/plain") || "{}");
  if (drag.type !== "carousel") return;
  const slot = plannerSlots[Number(drag.slotIdx)];
  if (!slot || !slot.carousel_items) return;
  const [item] = slot.carousel_items.splice(Number(drag.itemIdx), 1);
  if (item) plannerPool.unshift(item.asset);
  renumberCarousel(slot);
  schedulePlanSave();
  renderPlanner();
}
function setCarouselRole(slotIdx, itemIdx, role) {
  const item = plannerSlots[slotIdx] && plannerSlots[slotIdx].carousel_items && plannerSlots[slotIdx].carousel_items[itemIdx];
  if (!item) return;
  item.role = role;
  schedulePlanSave();
}
function removeCarouselItem(slotIdx, itemIdx) {
  const slot = plannerSlots[slotIdx];
  if (!slot || !slot.carousel_items) return;
  const [item] = slot.carousel_items.splice(itemIdx, 1);
  if (item) plannerPool.unshift(item.asset);
  renumberCarousel(slot);
  schedulePlanSave();
  renderPlanner();
}
function quickAddCarousel(slotIdx) {
  const asset = plannerPool.shift();
  if (!asset) return;
  if (!appendCarouselItem(slotIdx, asset)) plannerPool.unshift(asset);
  schedulePlanSave();
  renderPlanner();
}
function clearPlanner() {
  plannerSlots.forEach(slot => {
    if (slot.asset && slot.asset.source !== "scheduled") plannerPool.unshift(slot.asset);
    slot.asset = null;
  });
  schedulePlanSave();
  renderPlanner();
}
function addCustomSlot() {
  const date = prompt("Date for extra post, YYYY-MM-DD");
  if (!date || !/^\\d{4}-\\d{2}-\\d{2}$/.test(date)) return;
  const time = prompt("Time, 24-hour HH:MM", "17:00") || "17:00";
  const d = new Date(date + "T12:00:00");
  plannerSlots.push({
    date,
    dow: d.toLocaleDateString("en-US", { weekday:"short" }),
    time,
    slot_kind:"extra",
    asset:null
  });
  plannerSlots.sort((a, b) => (a.date + a.time).localeCompare(b.date + b.time));
  schedulePlanSave();
  renderPlanner();
}
function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.hidden = false;
  setTimeout(() => toast.hidden = true, 4500);
}
function closeCaptionModal() {
  document.getElementById("captionModal").hidden = true;
}
function openCaptionModal(slotIdx) {
  const slot = plannerSlots[slotIdx];
  const variants = slot && slot.caption_variants ? slot.caption_variants : [];
  if (!variants.length) return;
  document.getElementById("variantList").innerHTML = variants.map(variant => `
    <article class="variant-card">
      <p>${esc(variant.text)}</p>
      <div class="variant-meta">
        <span>${esc(variant.char_count || String(variant.text || "").length)} chars</span>
        ${(variant.warnings || []).map(w => `<span class="chip">${esc(w)}</span>`).join("")}
        ${variant.selected ? `<span class="chip">selected</span>` : ""}
      </div>
      <button class="brand" onclick="selectCaptionVariant(${slotIdx},'${esc(variant.id)}')">Use this</button>
    </article>
  `).join("");
  document.getElementById("captionModal").hidden = false;
}
async function generateCaption(slotIdx) {
  const slot = plannerSlots[slotIdx];
  if (!slot) return;
  try {
    const result = await api("/api/caption", {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ brand: activeBrand, slot_index: slot.slot_index ?? slotIdx })
    });
    slot.caption_variants = result.variants || [];
    openCaptionModal(slotIdx);
    renderPlanner();
  } catch (e) {
    if (e.status === 503) showToast("Set ANTHROPIC_API_KEY then restart.");
    else if (e.status === 422) showToast(e.payload && (e.payload.message || e.payload.error) || "Caption setup needs attention.");
    else showToast("Generation failed, try again.");
  }
}
async function selectCaptionVariant(slotIdx, variantId) {
  const slot = plannerSlots[slotIdx];
  if (!slot) return;
  const result = await api("/api/caption/select", {
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body: JSON.stringify({ brand: activeBrand, slot_index: slot.slot_index ?? slotIdx, variant_id: variantId })
  });
  plannerSlots[slotIdx] = result.slot;
  closeCaptionModal();
  schedulePlanSave();
  renderPlanner();
}
async function exportPlan() {
  if (!plannerSlots.length) await loadPlanner();
  if (saveTimer) await savePlanNow();
  try {
    const result = await api("/api/export-plan", {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ brand: activeBrand })
    });
    const warningText = result.warnings && result.warnings.length ? "\\nWarnings: " + result.warnings.length : "";
    alert("CSV written: " + result.csv_path + "\\nRows: " + result.row_count + warningText);
  } catch (e) {
    if (e.status === 422) {
      if (e.payload && e.payload.error === "unacknowledged_conflicts") {
        conflictData = { conflicts: e.payload.conflicts || [], summary: {} };
        renderConflictBanner();
        openConflictModal();
        alert("Export blocked: review or acknowledge planner conflicts first.");
        return;
      }
      const failures = (e.payload.failures || []).map(f => `slot ${f.slot_index}: ${f.message}`).join("\\n");
      alert("Export blocked:\\n" + failures);
      return;
    }
    throw e;
  }
}
async function indexNow() {
  await api("/api/index", { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify({}) });
  await loadAll();
}
async function mutate(path, payload) {
  await api(path, { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify(payload) });
  await loadBrands(); await loadAssets();
}
function rate(asset_id, rating) { mutate("/api/rate", { asset_id, rating }); }
function reject(asset_id) { mutate("/api/reject", { asset_id }); }
function shortlist(asset_id) { mutate("/api/status", { asset_id, status:"shortlisted" }); }
function pick(asset_id) { mutate("/api/promote-pick", { asset_id }); }
function duplicate(asset_id, post_id) {
  const group = prompt("Duplicate group id", post_id);
  if (group) mutate("/api/mark-duplicate", { asset_id, duplicate_group_id: group });
}
async function loadAll() { await loadBrands(); await loadAssets(); if (currentView === "planner") await loadPlanner(); }
loadAll().catch(err => { document.getElementById("grid").innerHTML = `<div class="empty">${esc(err.message)}</div>`; });
</script>
</body>
</html>
"""


# --- Generation jobs (in-process, simple state) -------------------------------

import subprocess as _subprocess  # noqa: E402  (deferred to avoid import cost)
import threading as _threading    # noqa: E402
import uuid as _uuid              # noqa: E402

_GEN_JOBS: dict = {}
_GEN_JOBS_LOCK = _threading.Lock()


def _count_generated_files(brand: str, root: pathlib.Path, since_ts: float) -> int:
    """Count newly written variation_*.png under nano_banana/<brand>/ created after since_ts."""
    base = root / "OUTPUT" / "nano_banana" / brand
    if not base.exists():
        return 0
    n = 0
    for png in base.rglob("variation_*.png"):
        try:
            if png.stat().st_mtime >= since_ts:
                n += 1
        except OSError:
            continue
    return n


# Map composer-friendly intent values → bulk_build VALID_INTENTS.
COMPOSER_INTENT_MAP = {
    "batch_seasonal": "new_seasonal_drop",
    "batch_menu":     "new_dish_typography",
    "batch_event":    "new_event_promo",
    "batch_quote":    "new_quote_card",
    "batch_utility":  "new_utility_post",
    "batch_test":     "experiment",
}


def start_generation_job(
    *, root: pathlib.Path, brand: str, count: int, intent: str, theme: str,
    formats: list | None = None,
) -> dict:
    """Spawn bulk_build.py as subprocess. Track via in-process dict.
    Theme + format selection passed via env (bulk_build also accepts them as
    CLI flags --theme and --formats)."""
    job_id = _uuid.uuid4().hex[:12]
    started_at = time.time()
    canonical_intent = COMPOSER_INTENT_MAP.get(intent, intent)
    cmd = [
        sys.executable,
        str(root / "scripts" / "bulk_build.py"),
        "--brand", brand,
        "--count", str(count),
        "--intent", canonical_intent,
    ]
    if theme:
        cmd += ["--theme", theme]
    if formats:
        cmd += ["--formats", ",".join(formats)]
    env = os.environ.copy()
    if theme:
        env["SAVORA_GENERATION_THEME"] = theme
    if formats:
        env["SAVORA_GENERATION_FORMATS"] = ",".join(formats)
    log_path = root / "OUTPUT" / "generation_logs"
    log_path.mkdir(parents=True, exist_ok=True)
    log_file = log_path / f"job_{job_id}.log"
    with open(log_file, "wb") as logf:
        proc = _subprocess.Popen(
            cmd,
            cwd=str(root),
            stdout=logf,
            stderr=_subprocess.STDOUT,
            env=env,
            start_new_session=True,
        )
    job = {
        "job_id": job_id,
        "brand": brand,
        "count": count,
        "intent": intent,
        "theme": theme,
        "pid": proc.pid,
        "started_at": started_at,
        "status": "running",
        "log_file": str(log_file),
    }
    with _GEN_JOBS_LOCK:
        _GEN_JOBS[job_id] = {**job, "_proc": proc}
    return {k: v for k, v in job.items() if not k.startswith("_")}


def get_job_status(job_id: str) -> dict:
    with _GEN_JOBS_LOCK:
        rec = _GEN_JOBS.get(job_id)
    if not rec:
        return {"job_id": job_id, "status": "unknown", "completed": 0, "total": 0}
    proc = rec.get("_proc")
    completed = _count_generated_files(rec["brand"], ROOT, rec["started_at"])
    total = rec["count"]
    if proc is not None:
        rc = proc.poll()
        if rc is None:
            status = "running"
        elif rc == 0:
            status = "done"
        else:
            status = f"failed (rc={rc})"
        if rc is not None:
            with _GEN_JOBS_LOCK:
                rec["status"] = status
                rec["_proc"] = None
    else:
        status = rec.get("status", "done")
    return {
        "job_id": job_id,
        "brand": rec["brand"],
        "status": status,
        "completed": min(completed, total),
        "total": total,
        "started_at": rec["started_at"],
        "log_file": rec.get("log_file"),
    }


# --- Feed grid (Vista CSV merge + picks pool) ---------------------------------

_FEED_BUILDER = None


def _load_feed_builder():
    """Lazy-import scripts/build_feed_composer.py so we reuse load_* + build_slots
    without duplicating logic. Cache the module after first load."""
    global _FEED_BUILDER
    if _FEED_BUILDER is not None:
        return _FEED_BUILDER
    import importlib.util
    path = ROOT / "scripts" / "build_feed_composer.py"
    spec = importlib.util.spec_from_file_location("build_feed_composer", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _FEED_BUILDER = mod
    return mod


def build_feed_grid(brand: str, *, root: pathlib.Path) -> dict:
    """Build the feed grid for a single brand: scheduled Vista slots + pool of
    unscheduled new posts and picks. Mirrors what build_feed_composer.py does
    when it generates the standalone HTML — only without the HTML wrapper."""
    fb = _load_feed_builder()
    aliases = {"el_azteca": "azteca"}
    brand_key = aliases.get(brand, brand)
    if brand_key not in fb.BRAND_CONFIG:
        return {"brand": brand_key, "error": "unknown_brand", "slots": [], "pool": []}
    scheduled = fb.load_scheduled(brand_key)
    new_posts = fb.load_unscheduled(brand_key)
    picks = fb.load_picks(brand_key)
    slots, leftover, queued = fb.build_slots(brand_key, scheduled, new_posts)
    pool = list(queued) + list(picks) + list(leftover)

    def normalize_url(post: dict) -> dict:
        url = post.get("url", "") or ""
        if url and not url.startswith(("http://", "https://")):
            post = {**post, "url": f"/media/{url}"}
        return post

    slots = [
        {**s, "post": normalize_url(s["post"]) if s.get("post") else None}
        for s in slots
    ]
    pool = [normalize_url(p) for p in pool]
    return {
        "brand": brand_key,
        "slot_count": len(slots),
        "pool_count": len(pool),
        "slots": slots,
        "pool": pool,
    }


# --- HTTP handler -------------------------------------------------------------


class ContentHandler(BaseHTTPRequestHandler):
    root = ROOT
    db_path = DB_PATH

    def _json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if not length:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _conn(self) -> sqlite3.Connection:
        return connect(self.db_path)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        try:
            if parsed.path == "/":
                body = ADMIN_HTML.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if parsed.path == "/composer":
                composer_path = self.root / "OUTPUT" / "composer.html"
                if not composer_path.exists():
                    self.send_error(404, "composer.html not found")
                    return
                body = composer_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if parsed.path == "/api/generate/status":
                qs = urllib.parse.parse_qs(parsed.query)
                job_id = (qs.get("job_id") or [""])[0]
                self._json(get_job_status(job_id))
                return
            if parsed.path == "/api/feed-grid":
                qs = urllib.parse.parse_qs(parsed.query)
                brand = (qs.get("brand") or ["blue_mezcal"])[0]
                self._json(build_feed_grid(brand, root=self.root))
                return
            if parsed.path.startswith("/media/"):
                rel = urllib.parse.unquote(parsed.path.removeprefix("/media/"))
                path = (self.root / rel).resolve()
                if not path.is_relative_to(self.root.resolve()) or not path.exists():
                    self.send_error(404)
                    return
                mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
                body = path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if parsed.path == "/api/brands":
                with self._conn() as conn:
                    self._json({"brands": list_brands(conn)})
                return
            if parsed.path == "/api/content-pool":
                qs = urllib.parse.parse_qs(parsed.query)
                with self._conn() as conn:
                    self._json({
                        "assets": list_assets(
                            conn,
                            brand=(qs.get("brand") or [None])[0],
                            status=(qs.get("status") or [None])[0],
                            q=(qs.get("q") or [None])[0],
                            min_rating=(
                                int(qs["min_rating"][0]) if qs.get("min_rating") and qs["min_rating"][0] else None
                            ),
                        )
                    })
                return
            if parsed.path == "/api/schedule-suggestions":
                qs = urllib.parse.parse_qs(parsed.query)
                brand = (qs.get("brand") or ["blue_mezcal"])[0]
                days = int((qs.get("days") or ["42"])[0])
                with self._conn() as conn:
                    self._json(schedule_suggestions(conn, brand=brand, days=days, root=self.root))
                return
            if parsed.path == "/api/plan":
                qs = urllib.parse.parse_qs(parsed.query)
                brand = (qs.get("brand") or [""])[0]
                with self._conn() as conn:
                    plan = plan_from_db(conn, brand=brand)
                if not plan:
                    self._json({"error": f"No saved plan for brand {normalize_brand(brand)}"}, status=404)
                    return
                self._json(plan)
                return
            if parsed.path == "/api/conflicts":
                qs = urllib.parse.parse_qs(parsed.query)
                brand = (qs.get("brand") or [""])[0]
                with self._conn() as conn:
                    self._json(detect_conflicts(conn, brand=brand, root=self.root))
                return
            self.send_error(404)
        except Exception as exc:  # noqa: BLE001
            self._json({"error": str(exc)}, status=500)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        try:
            payload = self._read_json()
            with self._conn() as conn:
                if parsed.path == "/api/index":
                    result = scan_generated_assets(conn=conn, root=self.root, brand=payload.get("brand"))
                    self._json(result)
                    return
                if parsed.path == "/api/rate":
                    rating = int(payload["rating"])
                    if rating < 1 or rating > 5:
                        raise ValueError("rating must be 1-5")
                    self._json({"asset": update_asset(
                        conn,
                        payload["asset_id"],
                        rating=rating,
                        status="shortlisted" if rating >= 4 else "new",
                        notes=payload.get("notes"),
                    )})
                    return
                if parsed.path == "/api/reject":
                    self._json({"asset": update_asset(conn, payload["asset_id"], status="rejected", notes=payload.get("notes"))})
                    return
                if parsed.path == "/api/status":
                    self._json({"asset": update_asset(conn, payload["asset_id"], status=payload["status"])})
                    return
                if parsed.path == "/api/mark-duplicate":
                    self._json({"asset": update_asset(
                        conn,
                        payload["asset_id"],
                        status="duplicate",
                        duplicate_group_id=payload["duplicate_group_id"],
                        duplicate_winner=1 if payload.get("winner") else 0,
                        notes=payload.get("notes"),
                    )})
                    return
                if parsed.path == "/api/promote-pick":
                    self._json({"asset": promote_pick(conn, root=self.root, asset_id=payload["asset_id"])})
                    return
                if parsed.path == "/api/generate":
                    brand = payload.get("brand", "blue_mezcal")
                    count = max(1, min(int(payload.get("count", 4)), 64))
                    intent = payload.get("intent", "batch_test")
                    theme = (payload.get("theme") or "").strip()
                    formats = payload.get("formats") or []
                    job = start_generation_job(
                        root=self.root, brand=brand, count=count, intent=intent,
                        theme=theme, formats=formats,
                    )
                    self._json(job)
                    return
                if parsed.path == "/api/plan/regenerate":
                    qs = urllib.parse.parse_qs(parsed.query)
                    brand = (qs.get("brand") or [payload.get("brand") or "blue_mezcal"])[0]
                    self._json(regenerate_plan(conn, brand=brand, root=self.root))
                    return
                if parsed.path == "/api/caption":
                    try:
                        self._json(generate_caption_variants(
                            conn,
                            brand=payload["brand"],
                            slot_index=int(payload["slot_index"]),
                        ))
                    except caption_service.NoApiKey:
                        self._json({"error": "no_api_key", "message": "Set ANTHROPIC_API_KEY in env."}, status=503)
                    except caption_service.VoiceProfileMissing as exc:
                        self._json({"error": "voice_profile_missing", "message": str(exc)}, status=422)
                    except ValueError as exc:
                        self._json({"error": "invalid_slot", "message": str(exc)}, status=422)
                    except caption_service.CaptionGenerationError as exc:
                        self._json({"error": "caption_generation_failed", "raw": exc.raw}, status=502)
                    except Exception as exc:  # noqa: BLE001
                        self._json({"error": "caption_generation_failed", "raw": str(exc)}, status=502)
                    return
                if parsed.path == "/api/caption/select":
                    try:
                        self._json({"slot": select_caption_variant(
                            conn,
                            brand=payload["brand"],
                            slot_index=int(payload["slot_index"]),
                            variant_id=payload["variant_id"],
                        )})
                    except KeyError as exc:
                        self._json({"error": "not_found", "message": str(exc)}, status=404)
                    return
                if parsed.path == "/api/conflicts/acknowledge":
                    self._json(acknowledge_conflict(
                        conn,
                        brand=payload["brand"],
                        conflict_key=payload["conflict_key"],
                        root=self.root,
                    ))
                    return
                if parsed.path == "/api/conflicts/revoke":
                    self._json(revoke_conflict_ack(
                        conn,
                        brand=payload["brand"],
                        conflict_key=payload["conflict_key"],
                        root=self.root,
                    ))
                    return
                if parsed.path == "/api/conflicts/auto-fix":
                    status, result = auto_fix_conflict(
                        conn,
                        brand=payload["brand"],
                        conflict_key=payload["conflict_key"],
                        action=payload["action"],
                        root=self.root,
                    )
                    self._json(result, status=status)
                    return
                if parsed.path == "/api/export-plan":
                    brand = normalize_brand(payload["brand"])
                    if "slots" in payload:
                        self._json({"error": "Export reads from the saved plan. Send only {brand}."}, status=400)
                        return
                    try:
                        self._json(export_saved_plan_csv(conn=conn, root=self.root, brand=brand))
                    except ConflictValidationError as exc:
                        self._json({
                            "error": "unacknowledged_conflicts",
                            "conflicts": exc.conflicts,
                        }, status=422)
                    except ExportValidationError as exc:
                        self._json({
                            "error": "validation_failed",
                            "failures": exc.manifest.get("failures", []),
                            "warnings": exc.manifest.get("warnings", []),
                            "manifest": exc.manifest,
                        }, status=422)
                    except ValueError as exc:
                        self._json({"error": "no_plan", "message": str(exc)}, status=400)
                    return
            self.send_error(404)
        except Exception as exc:  # noqa: BLE001
            self._json({"error": str(exc)}, status=500)

    def do_PUT(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        try:
            payload = self._read_json()
            with self._conn() as conn:
                if parsed.path == "/api/plan":
                    status, plan = save_plan(
                        conn,
                        brand=payload["brand"],
                        version=int(payload.get("version", 0)),
                        slots=payload.get("slots", []),
                        pool=payload.get("pool", []),
                    )
                    self._json(plan, status=status)
                    return
            self.send_error(404)
        except Exception as exc:  # noqa: BLE001
            self._json({"error": str(exc)}, status=500)

    def do_DELETE(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        try:
            if parsed.path == "/api/plan":
                qs = urllib.parse.parse_qs(parsed.query)
                brand = (qs.get("brand") or [""])[0]
                with self._conn() as conn:
                    delete_plan(conn, brand=brand)
                self._json({"ok": True, "brand": normalize_brand(brand)})
                return
            self.send_error(404)
        except Exception as exc:  # noqa: BLE001
            self._json({"error": str(exc)}, status=500)

    def log_message(self, fmt: str, *args: object) -> None:
        sys.stderr.write("[content-api] " + fmt % args + "\n")


def run_server(host: str, port: int, *, root: pathlib.Path = ROOT, db_path: pathlib.Path = DB_PATH) -> None:
    handler = type("SavoraContentHandler", (ContentHandler,), {"root": root, "db_path": db_path})
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Savora content admin: http://{host}:{port}/")
    print(f"Catalog DB: {db_path}")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--index", action="store_true", help="Index generated assets before serving")
    parser.add_argument("--index-only", action="store_true", help="Index generated assets and exit")
    parser.add_argument("--brand", default=None, help="Optional brand slug for --index")
    args = parser.parse_args()

    if args.index or args.index_only:
        with connect() as conn:
            print(scan_generated_assets(conn=conn, brand=args.brand))
    if args.index_only:
        return
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
