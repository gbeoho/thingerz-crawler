#!/usr/bin/env python3
"""
Thingerz Content Dashboard — Flask API server (single file).
============================================================

Serves a single-page dashboard (index.html) backed by the Thingerz crawler's
SQLite database. Provides a small JSON API for stats, districts, categories
and filtered content items.

Run:
    python3 server.py
Then open http://localhost:8080
"""

import os
import sqlite3
import sys

from flask import Flask, jsonify, request, send_from_directory

# ── Paths ──────────────────────────────────────────────────────────────
# All paths are relative to this file so the app can live anywhere.
API_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(API_DIR)                     # crawler root
DB_PATH = os.path.join(BASE_DIR, "data", "thingerz_crawler.db")

# Make ../config.py importable so we can reuse its SUB_CATEGORIES mapping
# (Chinese names + category groups) for the /api/categories endpoint.
sys.path.insert(0, BASE_DIR)
from config import CATEGORIES, SUB_CATEGORIES  # noqa: E402

app = Flask(__name__)

# The full row we expose for each item in the table (raw_data is huge/raw).
ITEM_COLUMNS = [
    "id", "platform", "platform_id", "sub_category", "district",
    "title", "description", "url", "thumbnail_url", "author_name",
    "author_url", "published_at", "view_count", "like_count",
    "comment_count", "duration_sec", "content_type", "language",
    "score", "fetched_at",
]


# ── Helpers ────────────────────────────────────────────────────────────
def get_db():
    """Open a connection-per-request to the crawler's SQLite DB."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def db_missing():
    """Return True when the crawler database does not exist yet."""
    return not os.path.exists(DB_PATH)


def empty_stats():
    """Shape of /api/stats when the DB is absent or empty."""
    return {
        "total": 0,
        "sub_categories_covered": 0,
        "districts_covered": 0,
        "platforms": 0,
        "per_platform": {},
        "last_run": None,
    }


def safe_int(value, default):
    """Coerce a query-string value to an int, falling back on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ── Pages ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    """Serve the single-page dashboard."""
    return send_from_directory(API_DIR, "index.html")


# ── API ────────────────────────────────────────────────────────────────
@app.route("/api/stats")
def api_stats():
    """Overall numbers for the KPI cards + per-platform counts."""
    if db_missing():
        return jsonify(empty_stats())

    conn = get_db()
    try:
        stats = {
            "total": conn.execute(
                "SELECT COUNT(*) AS c FROM crawled_content"
            ).fetchone()["c"],

            "sub_categories_covered": conn.execute(
                "SELECT COUNT(DISTINCT sub_category) AS c FROM crawled_content"
            ).fetchone()["c"],

            "districts_covered": conn.execute(
                "SELECT COUNT(DISTINCT district) AS c FROM crawled_content"
            ).fetchone()["c"],

            "platforms": conn.execute(
                "SELECT COUNT(DISTINCT platform) AS c FROM crawled_content"
            ).fetchone()["c"],

            "per_platform": {
                row["platform"]: row["c"]
                for row in conn.execute(
                    "SELECT platform, COUNT(*) AS c FROM crawled_content "
                    "GROUP BY platform"
                )
            },

            "last_run": None,
        }

        last_run = conn.execute(
            "SELECT * FROM crawl_run ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if last_run is not None:
            stats["last_run"] = dict(last_run)
    except sqlite3.OperationalError:
        # Table missing / DB not initialised yet — degrade gracefully.
        stats = empty_stats()
    finally:
        conn.close()

    return jsonify(stats)


@app.route("/api/districts")
def api_districts():
    """All districts with item counts, most populated first."""
    if db_missing():
        return jsonify([])

    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT district, COUNT(*) AS count FROM crawled_content "
            "GROUP BY district ORDER BY count DESC"
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
    finally:
        conn.close()

    return jsonify([dict(r) for r in rows])


@app.route("/api/categories")
def api_categories():
    """
    Per sub-category: code, Chinese name, group and item count.
    Chinese name + group come from config.py's SUB_CATEGORIES dict.
    """
    if db_missing():
        return jsonify([])

    conn = get_db()
    try:
        counts = {
            row["sub_category"]: row["count"]
            for row in conn.execute(
                "SELECT sub_category, COUNT(*) AS count FROM crawled_content "
                "GROUP BY sub_category"
            )
        }
    except sqlite3.OperationalError:
        counts = {}
    finally:
        conn.close()

    result = []
    for sub_category, count in counts.items():
        meta = SUB_CATEGORIES.get(sub_category, {})
        result.append({
            "sub_category": sub_category,
            "zh_name": meta.get("zh", sub_category),
            "category": meta.get("category", "unknown"),
            "count": count,
        })
    # Deterministic ordering by sub-category code (s001, s002, …).
    result.sort(key=lambda c: c["sub_category"])
    return jsonify(result)


@app.route("/api/items")
def api_items():
    """
    Filtered items, newest first.

    Query params:
        platform   — platform key (youtube, bilibili, …)
        district   — HK district (Chinese)
        category   — sub-category code (s001…) OR a category group
                     (commercial, education, …)
        q          — free-text search against title/description
        limit      — page size (default 20)
        offset     — pagination offset (default 0)
    """
    platform = request.args.get("platform", "").strip()
    district = request.args.get("district", "").strip()
    category = request.args.get("category", "").strip()
    q = request.args.get("q", "").strip()
    limit = min(safe_int(request.args.get("limit"), 20), 200)
    offset = max(safe_int(request.args.get("offset"), 0), 0)

    where = []
    params = []

    if platform:
        where.append("platform = ?")
        params.append(platform)

    if district:
        where.append("district = ?")
        params.append(district)

    if category:
        if category in CATEGORIES:
            # A category group: expand to every sub-category inside it.
            sub_codes = [
                code for code, meta in SUB_CATEGORIES.items()
                if meta["category"] == category
            ]
            where.append("sub_category IN (%s)" % ",".join("?" * len(sub_codes)))
            params.extend(sub_codes)
        else:
            # A single sub-category code (s001 … s054).
            where.append("sub_category = ?")
            params.append(category)

    if q:
        like = f"%{q.replace('%', '\\%').replace('_', '\\_')}%"
        where.append(
            "(title LIKE ? ESCAPE '\\' OR description LIKE ? ESCAPE '\\')"
        )
        params.extend([like, like])

    clause = (" WHERE " + " AND ".join(where)) if where else ""

    conn = get_db()
    try:
        total = conn.execute(
            "SELECT COUNT(*) AS c FROM crawled_content" + clause,
            params,
        ).fetchone()["c"]

        rows = conn.execute(
            "SELECT " + ", ".join(ITEM_COLUMNS) + " FROM crawled_content"
            + clause
            + " ORDER BY fetched_at DESC LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
        total = 0
    finally:
        conn.close()

    return jsonify({"total": total, "items": [dict(r) for r in rows]})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Render injects PORT
    print(f"Thingerz dashboard → http://0.0.0.0:{port}  (db: {DB_PATH})")
    app.run(host="0.0.0.0", port=port)
