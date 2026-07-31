# Thingerz Dashboard — Build Task

Build a web dashboard for the Thingerz content crawler. The crawler lives at /opt/data/thingerz-crawler and stores data in SQLite at /opt/data/thingerz-crawler/data/thingerz_crawler.db

## Database Schema (table: crawled_content)

Columns: id, platform (youtube/bilibili/instagram/douyin/threads/xiaohongshu), platform_id, sub_category (s001-s054), district (18 HK districts in Chinese), title, description, url, thumbnail_url, author_name, author_url, published_at, view_count, like_count, comment_count, duration_sec, content_type, language, raw_data, score (REAL 0-1), fetched_at

Indexes exist on: sub_category, district, platform, fetched_at, score.

## Task

Create a self-contained web dashboard in /opt/data/thingerz-crawler/api/ with these files:

1. **server.py** — Python Flask app (single file) that:
   - Serves the SQLite DB from ../data/thingerz_crawler.db (relative to the api dir)
   - `GET /` → serves index.html
   - `GET /api/stats` → { total, sub_categories_covered (distinct count), districts_covered, platforms, per_platform: {platform: count}, last_run: most recent crawl_run row }
   - `GET /api/districts` → [{district, count}] ordered by count desc
   - `GET /api/categories` → [{sub_category, zh_name, category, count}] — join against config.py's SUB_CATEGORIES dict (import it from ../config.py by adding the parent dir to sys.path) to get the Chinese name and category group
   - `GET /api/items?platform=&district=&category=&limit=20&offset=0&q=` → filtered items ordered by fetched_at desc, with optional text search q against title/description. Return also total count of matching items.
   - Use connection-per-request (sqlite3.connect with row_factory), close after each request
   - Port 8080, host 0.0.0.0
   - Handle the case where DB file doesn't exist yet (return empty stats instead of crashing)

2. **index.html** — Single-page dashboard, ALL CSS and JS inline (no external local files; Chart.js from CDN is fine):
   - Dark modern theme (like Vercel/Linear style, #0a0a0f background, subtle borders, nice accent color like #6c5ce7 or #7c5cff)
   - Header: "Thingerz Content Dashboard" + last-run timestamp badge
   - 4 KPI stat cards at top: Total Items, Sub-categories, Districts, Platforms
   - Chart.js bar chart: items per platform (6 bars, distinct colors)
   - Chart.js horizontal bar chart: top 15 districts
   - Chart.js bar chart: items per category group (from categories endpoint, group by the 'category' field)
   - Filters row: platform dropdown, district dropdown, sub-category dropdown (populated from /api/categories), text search input, limit selector
   - Items table: thumbnail (img, 48px, rounded), title (clickable link to url, target _blank), author, platform badge, district, sub-category, views, likes, score (colored), fetched_at
   - Pagination: prev/next buttons + "showing X–Y of Z"
   - Loading states and graceful empty states
   - Chinese font support (font-family fallback: -apple-system, "PingFang HK", "Microsoft JhengHei", sans-serif)
   - All fetch() calls to the API above, refresh charts when filters change

3. **requirements.txt** — just `flask`

## Constraints
- Use ONLY Flask + stdlib (sqlite3, json). No pandas, no ORM.
- Single-file server.py, single-file index.html.
- Readable, commented code.
- Do NOT modify anything outside /opt/data/thingerz-crawler/api/
- Do NOT touch the database file itself.

## Verification
After creating the files, run: cd /opt/data/thingerz-crawler/api && python3 server.py in the background, then curl http://localhost:8080/api/stats and curl http://localhost:8080/api/items?limit=3 to verify the endpoints return JSON. Then kill the server.

Report back: list of files created, endpoint verification results (the actual JSON responses), and any issues.
