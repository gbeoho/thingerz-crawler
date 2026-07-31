"""
SQLite storage for crawled content — deduped by (platform, platform_id).
"""

import sqlite3
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS crawled_content (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    -- dedup key
    platform      TEXT NOT NULL,       -- youtube, instagram, douyin, threads, xiaohongshu, bilibili
    platform_id   TEXT NOT NULL,       -- native id on the platform (video id, post id, url hash)
    -- context
    sub_category  TEXT NOT NULL,       -- s001..s054
    district      TEXT NOT NULL,       -- 香港18區
    -- content
    title         TEXT,
    description   TEXT,
    url           TEXT NOT NULL,
    thumbnail_url TEXT,
    author_name   TEXT,
    author_url    TEXT,
    published_at  TEXT,                -- ISO-8601
    view_count    INTEGER DEFAULT 0,
    like_count    INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    duration_sec  INTEGER,            -- video length (0 for image posts)
    content_type  TEXT DEFAULT 'video', -- video / image / text
    language      TEXT DEFAULT 'zh',
    raw_data      TEXT,                -- JSON blob for extra fields
    -- meta
    score         REAL DEFAULT 0.0,    -- relevance score (0-1)
    fetched_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    UNIQUE(platform, platform_id)
);

CREATE INDEX IF NOT EXISTS idx_crawled_sub_cat  ON crawled_content(sub_category);
CREATE INDEX IF NOT EXISTS idx_crawled_district  ON crawled_content(district);
CREATE INDEX IF NOT EXISTS idx_crawled_platform  ON crawled_content(platform);
CREATE INDEX IF NOT EXISTS idx_crawled_fetched   ON crawled_content(fetched_at);
CREATE INDEX IF NOT EXISTS idx_crawled_score     ON crawled_content(score DESC);

CREATE TABLE IF NOT EXISTS crawl_run (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at      TEXT NOT NULL,
    ended_at        TEXT,
    sub_categories  INTEGER DEFAULT 0,
    districts       INTEGER DEFAULT 0,
    platforms       INTEGER DEFAULT 0,
    total_fetched   INTEGER DEFAULT 0,
    total_new       INTEGER DEFAULT 0,
    status          TEXT DEFAULT 'running' -- running / completed / failed
);

CREATE TABLE IF NOT EXISTS sub_category_stats (
    sub_category  TEXT PRIMARY KEY,
    district      TEXT NOT NULL,
    total_count   INTEGER DEFAULT 0,
    last_fetched  TEXT
);
"""


def get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def upsert_content(conn: sqlite3.Connection, item: Dict[str, Any]) -> bool:
    """
    Insert or update a single content item.
    Returns True if new, False if updated an existing row.
    """
    raw = {k: v for k, v in item.items()
           if k not in ('title', 'description', 'url', 'thumbnail_url',
                        'author_name', 'author_url', 'view_count', 'like_count',
                        'comment_count', 'duration_sec', 'content_type', 'score')}
    # Check if exists first so we can return True/False correctly
    existing = conn.execute(
        "SELECT 1 FROM crawled_content WHERE platform=? AND platform_id=?",
        (item['platform'], item['platform_id'])
    ).fetchone()

    conn.execute("""
        INSERT INTO crawled_content
            (platform, platform_id, sub_category, district, title, description,
             url, thumbnail_url, author_name, author_url,
             published_at, view_count, like_count, comment_count,
             duration_sec, content_type, score, raw_data)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(platform, platform_id) DO UPDATE SET
            title       = COALESCE(excluded.title, title),
            description = COALESCE(excluded.description, description),
            view_count  = COALESCE(excluded.view_count, view_count),
            like_count  = COALESCE(excluded.like_count, like_count),
            comment_count = COALESCE(excluded.comment_count, comment_count),
            score       = COALESCE(excluded.score, score),
            raw_data    = COALESCE(excluded.raw_data, raw_data),
            fetched_at  = strftime('%Y-%m-%dT%H:%M:%fZ','now')
    """, (
        item['platform'], item['platform_id'], item['sub_category'], item['district'],
        item.get('title', ''), item.get('description', ''),
        item['url'], item.get('thumbnail_url'),
        item.get('author_name'), item.get('author_url'),
        item.get('published_at'), item.get('view_count', 0),
        item.get('like_count', 0), item.get('comment_count', 0),
        item.get('duration_sec'), item.get('content_type', 'video'),
        item.get('score', 0.0), json.dumps(raw, ensure_ascii=False),
    ))
    return existing is None  # True if was new row


def cleanup_stale_runs():
    """Mark any runs still 'running' as 'failed' — from previous killed sessions."""
    conn = get_conn()
    conn.execute(
        "UPDATE crawl_run SET status='failed', ended_at=? WHERE status='running'",
        (datetime.now(timezone.utc).isoformat(),)
    )
    conn.commit()
    conn.close()


def start_run(sub_cats: int, districts: int, platforms: int) -> int:
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO crawl_run (started_at, sub_categories, districts, platforms) VALUES (?,?,?,?)",
        (datetime.now(timezone.utc).isoformat(), sub_cats, districts, platforms)
    )
    run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return run_id


def finish_run(run_id: int, total_fetched: int, total_new: int, status: str = "completed"):
    conn = get_conn()
    conn.execute(
        "UPDATE crawl_run SET ended_at=?, total_fetched=?, total_new=?, status=? WHERE id=?",
        (datetime.now(timezone.utc).isoformat(), total_fetched, total_new, status, run_id)
    )
    conn.commit()
    conn.close()


def get_latest_for_subcategory(sub_category: str, district: str,
                                platform: Optional[str] = None,
                                limit: int = 20) -> List[Dict]:
    """Get latest verified content for a sub-category + district combo."""
    conn = get_conn()
    where = "sub_category=? AND district=?"
    params = [sub_category, district]
    if platform:
        where += " AND platform=?"
        params.append(platform)
    rows = conn.execute(f"""
        SELECT * FROM crawled_content
        WHERE {where}
        ORDER BY score DESC, view_count DESC
        LIMIT ?
    """, (*params, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_district_summary(sub_category: str) -> List[Dict]:
    """Get grouped count per district for a sub-category."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT district, COUNT(*) as cnt, MAX(fetched_at) as last_fetched
        FROM crawled_content
        WHERE sub_category=?
        GROUP BY district
        ORDER BY cnt DESC
    """, (sub_category,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_platform_summary(sub_category: str, district: str) -> List[Dict]:
    """Get grouped count per platform for a sub-category + district."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT platform, COUNT(*) as cnt, MAX(fetched_at) as last_fetched
        FROM crawled_content
        WHERE sub_category=? AND district=?
        GROUP BY platform
        ORDER BY cnt DESC
    """, (sub_category, district)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_content(limit: int = 100, offset: int = 0) -> List[Dict]:
    """Get all content, newest first."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM crawled_content
        ORDER BY fetched_at DESC
        LIMIT ? OFFSET ?
    """, (limit, offset)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def export_json() -> List[Dict]:
    """Full export for thingerz.com API push."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT platform, platform_id, sub_category, district,
               title, description, url, thumbnail_url,
               author_name, author_url, published_at,
               view_count, like_count, comment_count,
               duration_sec, content_type, score, fetched_at
        FROM crawled_content
        WHERE score >= 0.3
        ORDER BY score DESC, fetched_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]