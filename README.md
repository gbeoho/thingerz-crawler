# Thingerz Content Crawler & Dashboard

Social media content aggregation for [thingerz.com](https://thingerz.com) — crawls 6 platforms (YouTube, Bilibili, Instagram, TikTok/Douyin, Threads, 小紅書) across 54 sub-categories × 18 HK districts, deduplicated in SQLite, plus a web dashboard.

## Components

- **`main.py`** — CLI crawler orchestrator
  - `python3 main.py` — full crawl (54 × 18 × 6, ~10h)
  - `python3 main.py --max-combos N` — crawl only N query combos (for cron batches)
  - `python3 main.py --push` — crawl + push to thingerz.com API
  - `python3 main.py --stats` — database stats
  - `python3 main.py --export` — dump all content as JSON
- **`config.py`** — taxonomy (tracks, categories, 54 sub-categories, 18 districts, platforms, intent keywords)
- **`storage.py`** — SQLite storage with dedup by `(platform, platform_id)`
- **`search/`** — per-platform search modules (multi-strategy: API → HTML scrape → URL generation)
- **`api/`** — Flask dashboard (stats + filtered content browsing)

## Database

SQLite at `data/thingerz_crawler.db` (WAL mode). Tables: `crawled_content`, `crawl_run`, `sub_category_stats`.

## API Keys

| Env Var | Purpose |
|---------|---------|
| `GOOGLE_CSE_API_KEY` + `GOOGLE_CSE_CX` | Google Programmable Search (Instagram, Threads, Xiaohongshu, Douyin) |
| `SERPAPI_KEY` | SerpAPI (same platforms) |
| `THINGERZ_API_URL` / `THINGERZ_API_KEY` | Push results to thingerz.com |

## Dashboard

```bash
cd api
pip install -r requirements.txt
python3 server.py   # http://localhost:8080
```

Endpoints: `/api/stats`, `/api/districts`, `/api/categories`, `/api/items?platform=&district=&category=&q=&limit=&offset=`

## Deploy (Render)

`render.yaml` at repo root defines the web service (auto-detected when connecting the repo to Render).

## Cron

Runs every 6h via Hermes cron. After the `--max-combos` fix, recommended schedule is a small batch every 30–60 min instead of one long crawl.

## Testing

```bash
python3 main.py --dry-run   # preview search combos
python3 main.py --stats     # DB health
```
