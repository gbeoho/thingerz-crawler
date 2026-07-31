"""
YouTube search — uses public yewtu/Invidious instances or direct scrape
as fallback.  No API key needed for basic search.
"""

import re
import time
import json
import urllib.parse
import urllib.request
from typing import Dict, List, Optional

from config import MAX_RESULTS_PER_PLATFORM

# Invidious fallback instances (public, no key)
INVIDIOUS_INSTANCES = [
    "https://inv.nadeko.net",
    "https://yt.artemislena.eu",
    "https://invidious.snopyta.org",
    "https://yewtu.be",
]

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/120.0.0.0 Safari/537.36")


def _search_invidious(query: str, max_results: int = 10) -> List[Dict]:
    """Search YouTube via Invidious API."""
    for instance in INVIDIOUS_INSTANCES:
        try:
            url = f"{instance}/api/v1/search?q={urllib.parse.quote(query)}&type=video&page=1&sort=relevance"
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            results = []
            for item in data[:max_results]:
                if item.get("type") != "video":
                    continue
                results.append({
                    "platform": "youtube",
                    "platform_id": item.get("videoId", ""),
                    "title": item.get("title", ""),
                    "description": item.get("description", "")[:500],
                    "url": f"https://www.youtube.com/watch?v={item.get('videoId', '')}",
                    "thumbnail_url": item.get("videoThumbnails", [{}])[-1].get("url", "") if item.get("videoThumbnails") else "",
                    "author_name": item.get("author", ""),
                    "author_url": f"https://www.youtube.com/channel/{item.get('authorId', '')}" if item.get("authorId") else "",
                    "published_at": item.get("publishedText", ""),
                    "view_count": item.get("viewCount", 0),
                    "like_count": item.get("likeCount", 0),
                    "duration_sec": item.get("lengthSeconds", 0),
                    "content_type": "video",
                    "score": min(1.0, (item.get("viewCount", 0) or 0) / 100000) if item.get("viewCount") else 0.5,
                })
            if results:
                return results
        except Exception:
            continue
    return []


def _scrape_youtube_html(query: str, max_results: int = 10) -> List[Dict]:
    """Fallback: scrape YouTube search results HTML."""
    try:
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Extract initial data from ytInitialData
        match = re.search(r'var ytInitialData = ({.*?});</script>', html, re.DOTALL)
        if not match:
            return []

        data = json.loads(match.group(1))
        results = []
        contents = (data.get("contents", {}).get("twoColumnSearchResultsRenderer", {})
                    .get("primaryContents", {}).get("sectionListRenderer", {})
                    .get("contents", []))

        for section in contents:
            items = section.get("itemSectionRenderer", {}).get("contents", [])
            for item in items:
                v = item.get("videoRenderer", {})
                if not v:
                    continue
                vid = v.get("videoId", "")
                if not vid:
                    continue
                title_runs = v.get("title", {}).get("runs", [])
                title = "".join(r.get("text", "") for r in title_runs)

                views_text = v.get("viewCount", {}).get("simpleText", "0")
                views = 0
                m = re.search(r'([\d,]+)', views_text.replace("次观看", ""))
                if m:
                    views = int(m.group(1).replace(",", ""))

                length = v.get("lengthSeconds", {}).get("simpleText", "0")
                try:
                    parts = length.split(":")
                    dur = int(parts[0]) * 60 + int(parts[1]) if len(parts) == 2 else int(parts[0])
                except (ValueError, IndexError):
                    dur = 0

                results.append({
                    "platform": "youtube",
                    "platform_id": vid,
                    "title": title,
                    "description": v.get("detailedMetadataSnippets", [{}])[0]
                                    .get("snippetText", {}).get("runs", [{}])[0]
                                    .get("text", "")[:500] if v.get("detailedMetadataSnippets") else "",
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "thumbnail_url": v.get("thumbnail", {}).get("thumbnails", [{}])[-1].get("url", ""),
                    "author_name": v.get("ownerText", {}).get("runs", [{}])[0].get("text", ""),
                    "author_url": v.get("ownerText", {}).get("runs", [{}])[0].get("navigationEndpoint", {})
                                  .get("browseEndpoint", {}).get("canonicalBaseUrl", ""),
                    "published_at": v.get("publishedTimeText", {}).get("simpleText", ""),
                    "view_count": views,
                    "like_count": 0,
                    "duration_sec": dur,
                    "content_type": "video",
                    "score": min(1.0, views / 100000) if views else 0.5,
                })
                if len(results) >= max_results:
                    break
        return results
    except Exception:
        return []


def search(query: str, max_results: int = MAX_RESULTS_PER_PLATFORM) -> List[Dict]:
    """Search YouTube for content matching the query."""
    results = _search_invidious(query, max_results)
    if not results:
        results = _scrape_youtube_html(query, max_results)
    time.sleep(0.5)  # rate limit courtesy
    return results