"""
thingerz-crawler — Main orchestrator
======================================
Every 6 hours:
  1. For each sub-category (54 total)
  2. For each Hong Kong district (18 total)
  3. For each enabled platform (6 total)
  4. Build a search query = "{sub_category_zh} {district} 香港"
  5. Collect results
  6. Store in SQLite with dedup
  7. Optionally push to thingerz.com API
"""

import json
import os
import random
import re
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    SUB_CATEGORIES, HK_DISTRICTS, DISTRICT_ALIASES,
    PLATFORMS, MAX_RESULTS_PER_PLATFORM,
    INTENT_KEYWORDS, QUALITY_SIGNALS, CONTENT_BLOCKLIST,
    THINGERZ_API_URL, THINGERZ_API_KEY, LOG_DIR,
)
from search import search_platform, _load_searchers
from storage import (
    init_db, get_conn, upsert_content,
    start_run, finish_run, export_json, cleanup_stale_runs,
)


def build_queries(sub_cat_id: str, sub_cat_zh: str, district: str) -> List[str]:
    """
    Build search query variations for a sub-category + district.
    Returns multiple query variants to maximize coverage.
    Randomly picks 2 intent-based keywords per run to cycle through
    all real-world search terms over time.
    """
    # Primary: Chinese query
    queries = [
        f"{sub_cat_zh} {district} 香港",
        f"{sub_cat_zh} {district}",
    ]

    # Intent-based keywords (random 2 per run for cycling)
    intent_kw = INTENT_KEYWORDS.get(sub_cat_id, [])
    if intent_kw:
        selected = random.sample(intent_kw, min(2, len(intent_kw)))
        for kw in selected:
            queries.append(f"{kw} {district} 香港")
            queries.append(f"{district} {kw}")

    # English alias for the district
    aliases = DISTRICT_ALIASES.get(district, [])
    for alias in aliases:
        queries.append(f"{sub_cat_zh} {alias} Hong Kong")
        # Also add intent keywords with English alias
        for kw in selected:
            queries.append(f"{kw} {alias}")

    # Deduplicate
    seen = set()
    unique = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            unique.append(q)
    return unique


def is_content_blocked(item: Dict) -> bool:
    """
    Check if content should be blocked (politics, sex, inappropriate).
    Returns True if the content should be filtered out.
    """
    title = (item.get("title") or "") + " " + (item.get("description") or "")
    for keyword in CONTENT_BLOCKLIST:
        if keyword in title:
            return True
    return False


def compute_quality_score(item: Dict) -> float:
    """
    Score a content item based on how well it demonstrates
    actual service/teaching quality (not just generic content).
    Returns a score from 0.0 to 1.0.
    """
    score = 0.3  # baseline

    title = (item.get("title") or "") + " " + (item.get("description") or "")
    title_lower = title.lower()

    # Boost for quality signals in title/description
    signal_count = 0
    for signal in QUALITY_SIGNALS:
        if signal in title or signal in title_lower:
            signal_count += 1
    score += min(0.4, signal_count * 0.08)  # up to +0.4 for quality signals

    # Boost for view count (popular content is more likely to be quality)
    views = item.get("view_count", 0) or 0
    if views > 0:
        score += min(0.15, views / 50000 * 0.15)

    # Penalize very short videos (< 30s — likely shorts/reels, less teaching value)
    dur = item.get("duration_sec", 0) or 0
    if dur > 0 and dur < 30:
        score -= 0.1
    elif dur > 300:  # 5+ min — more likely to be substantive
        score += 0.05

    # Penalize extremely low engagement (suggests low quality)
    likes = item.get("like_count", 0) or 0
    if views > 100 and likes == 0:
        score -= 0.05

    return max(0.0, min(1.0, score))


def estimate_crawl_time():
    """Rough estimate of how long a full crawl takes (in seconds)."""
    enabled = sum(1 for p in PLATFORMS.values() if p["enabled"])
    total_calls = len(SUB_CATEGORIES) * len(HK_DISTRICTS) * enabled * 2  # 2 query variants
    # Each call takes ~2 sec + rate limit delays
    return total_calls * 3  # seconds


def run_crawl(dry_run: bool = False, max_combos: int = 0, progress_callback=None) -> Dict:
    """Execute a full crawl cycle."""
    _load_searchers()
    init_db()
    cleanup_stale_runs()  # Mark previous killed runs as failed

    sub_cats = list(SUB_CATEGORIES.items())
    districts = HK_DISTRICTS
    enabled_platforms = [p for p, cfg in PLATFORMS.items() if cfg["enabled"]]

    run_id = start_run(len(sub_cats), len(districts), len(enabled_platforms))
    total_fetched = 0
    total_new = 0
    total_skipped = 0
    errors = []

    total_combos = len(sub_cats) * len(districts) * 2  # 2 query variants
    combo_idx = 0

    for sub_cat_id, sub_cat_info in sub_cats:
        sub_cat_zh = sub_cat_info["zh"]
        for district in districts:
            queries = build_queries(sub_cat_id, sub_cat_zh, district)

            for query in queries:
                combo_idx += 1

                # Stop early if max_combos is set
                if max_combos > 0 and combo_idx > max_combos:
                    finish_run(run_id, total_fetched, total_new, "partial")
                    return {
                        "run_id": run_id,
                        "sub_categories": len(sub_cats),
                        "districts": len(districts),
                        "platforms": len(enabled_platforms),
                        "total_fetched": total_fetched,
                        "total_new": total_new,
                        "total_errors": len(errors),
                        "errors": errors[:10],
                        "status": "partial",
                        "note": f"Stopped early at combo {combo_idx} (max_combos={max_combos})",
                    }

                if dry_run:
                    print(f"[DRY RUN] Would search: sub_cat={sub_cat_id} ({sub_cat_zh}), "
                          f"district={district}, query='{query}'")
                    continue

                for platform in enabled_platforms:
                    try:
                        results = search_platform(platform, query, MAX_RESULTS_PER_PLATFORM)
                        if not results:
                            continue

                        # Tag results with sub_category + district
                        for item in results:
                            # Block inappropriate content
                            if is_content_blocked(item):
                                continue
                            item["sub_category"] = sub_cat_id
                            item["district"] = district
                            # Compute quality score based on content signals
                            item["score"] = compute_quality_score(item)

                        # Store
                        conn = get_conn()
                        for item in results:
                            is_new = upsert_content(conn, item)
                            if is_new:
                                total_new += 1
                            total_fetched += 1
                        conn.commit()
                        conn.close()

                    except Exception as e:
                        errors.append(f"{platform}:{query[:30]}: {str(e)[:60]}")
                        continue

                # Progress indicator
                if progress_callback:
                    progress_callback(combo_idx, total_combos, total_fetched, total_new)
                else:
                    pct = combo_idx / total_combos * 100
                    sys.stdout.write(
                        f"\r  {combo_idx}/{total_combos} ({pct:.0f}%) | "
                        f"fetched={total_fetched} new={total_new} err={len(errors)}    "
                    )
                    sys.stdout.flush()

                # Rate limit: 0.5s between platform queries for a single combo
                time.sleep(0.3)

    # Finish
    if not dry_run:
        finish_run(run_id, total_fetched, total_new, "completed" if not errors else "partial")
    else:
        finish_run(run_id, 0, 0, "dry_run")

    if not dry_run:
        print()

    return {
        "run_id": run_id,
        "sub_categories": len(sub_cats),
        "districts": len(districts),
        "platforms": len(enabled_platforms),
        "total_fetched": total_fetched,
        "total_new": total_new,
        "total_errors": len(errors),
        "errors": errors[:10],  # first 10 only
        "status": "dry_run" if dry_run else ("completed" if not errors else "partial"),
    }


def push_to_thingerz() -> Dict:
    """Push latest content to thingerz.com API (if configured)."""
    if not THINGERZ_API_URL or not THINGERZ_API_KEY:
        print("[push] Skipped: THINGERZ_API_URL or THINGERZ_API_KEY not set")
        print("[push] To enable: export THINGERZ_API_URL=https://thingerz.com/api/content")
        print("[push]            export THINGERZ_API_KEY=your_key_here")
        return {"status": "skipped", "reason": "env_not_set"}

    data = export_json()
    if not data:
        print("[push] No content to push")
        return {"status": "skipped", "reason": "no_content"}

    # Batch in chunks of 500 to avoid payload size limits
    batch_size = 500
    total_sent = 0
    total_errors = 0

    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        try:
            import urllib.request
            payload = json.dumps({
                "key": THINGERZ_API_KEY,
                "content": batch,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }).encode("utf-8")

            req = urllib.request.Request(
                THINGERZ_API_URL,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": THINGERZ_API_KEY,
                    "User-Agent": "ThingerzCrawler/2.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = resp.read().decode()
                total_sent += len(batch)
                print(f"[push] Batch {i//batch_size + 1}: sent {len(batch)} items → {resp.status}")
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"[push] HTTP {e.code}: {body[:200]}")
            total_errors += len(batch)
        except Exception as e:
            print(f"[push] Failed: {e}")
            total_errors += len(batch)

    print(f"[push] Done: {total_sent} sent, {total_errors} errors")
    return {
        "status": "completed" if total_errors == 0 else "partial",
        "sent": total_sent,
        "errors": total_errors,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Thingerz Social Media Content Crawler")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done, don't store")
    parser.add_argument("--max-combos", type=int, default=0, help="Stop after N query combos (default: all)")
    parser.add_argument("--push", action="store_true", help="Push results to thingerz.com API after crawl")
    parser.add_argument("--export", action="store_true", help="Export all content as JSON")
    parser.add_argument("--init-db", action="store_true", help="Initialize database only")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    args = parser.parse_args()

    if args.init_db:
        init_db()
        print(f"[init] Database initialized at data/thingerz_crawler.db")
        return

    if args.export:
        init_db()
        data = export_json()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if args.stats:
        init_db()
        conn = get_conn()
        rows = conn.execute("SELECT COUNT(*) as cnt FROM crawled_content").fetchone()
        print(f"Total content items: {rows['cnt']}")
        rows = conn.execute("SELECT COUNT(DISTINCT sub_category) FROM crawled_content").fetchone()
        print(f"Sub-categories covered: {rows[0]}")
        rows = conn.execute("SELECT COUNT(DISTINCT district) FROM crawled_content").fetchone()
        print(f"Districts covered: {rows[0]}")
        rows = conn.execute("SELECT platform, COUNT(*) as cnt FROM crawled_content GROUP BY platform ORDER BY cnt DESC").fetchall()
        print("\nPer platform:")
        for r in rows:
            print(f"  {r['platform']}: {r['cnt']}")
        conn.close()
        return

    # Estimate time
    est = estimate_crawl_time()
    print(f"=== Thingerz Crawler ===")
    print(f"Sub-categories: {len(SUB_CATEGORIES)}")
    print(f"Districts:      {len(HK_DISTRICTS)}")
    print(f"Platforms:      {sum(1 for p in PLATFORMS.values() if p['enabled'])}")
    print(f"Estimated time: ~{est//60} min")
    print(f"Dry run: {args.dry_run}")
    print()

    result = run_crawl(dry_run=args.dry_run, max_combos=args.max_combos)

    print()
    print("=== Results ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.push and not args.dry_run:
        print()
        push_to_thingerz()


if __name__ == "__main__":
    main()