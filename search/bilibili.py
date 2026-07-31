"""
Bilibili search — uses bilibili public search API (no auth required).
"""

import json
import time
import urllib.parse
import urllib.request
from typing import Dict, List

from config import MAX_RESULTS_PER_PLATFORM

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/120.0.0.0 Safari/537.36")

BILIBILI_HEADERS = {
    "User-Agent": USER_AGENT,
    "Referer": "https://www.bilibili.com/",
    "Accept-Language": "zh-HK,zh;q=0.9",
}


def search(query: str, max_results: int = MAX_RESULTS_PER_PLATFORM) -> List[Dict]:
    """Search Bilibili for videos matching the query."""
    results = []
    try:
        url = ("https://api.bilibili.com/x/web-interface/search/type"
               f"?search_type=video&keyword={urllib.parse.quote(query)}&page=1")
        req = urllib.request.Request(url, headers=BILIBILI_HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        videos = data.get("data", {}).get("result", [])
        for v in videos[:max_results]:
            bvid = v.get("bvid", "")
            if not bvid:
                continue

            # Parse duration
            duration = v.get("duration", "0:00")
            dur_sec = 0
            try:
                parts = duration.split(":")
                if len(parts) == 2:
                    dur_sec = int(parts[0]) * 60 + int(parts[1])
                elif len(parts) == 3:
                    dur_sec = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            except (ValueError, IndexError):
                pass

            play_count = v.get("play", 0)
            like_count = v.get("like", 0)

            results.append({
                "platform": "bilibili",
                "platform_id": bvid,
                "title": v.get("title", "").replace("<em class=\"keyword\">", "").replace("</em>", ""),
                "description": v.get("description", "")[:500],
                "url": f"https://www.bilibili.com/video/{bvid}",
                "thumbnail_url": v.get("pic", ""),
                "author_name": v.get("author", ""),
                "author_url": f"https://space.bilibili.com/{v.get('mid', '')}" if v.get("mid") else "",
                "published_at": v.get("pubdate", ""),
                "view_count": play_count,
                "like_count": like_count,
                "comment_count": v.get("review", 0),
                "duration_sec": dur_sec,
                "content_type": "video",
                "score": min(1.0, play_count / 100000) if play_count else 0.3,
            })
    except Exception as e:
        # Silent fail — platform may be throttling
        pass

    time.sleep(0.3)  # be polite
    return results