"""
抖音/TikTok search — multi-strategy approach.

Strategy 1: SerpAPI (set SERPAPI_KEY) — supports TikTok search
Strategy 2: Google CSE (set GOOGLE_CSE_API_KEY + GOOGLE_CSE_CX)
Strategy 3: Query recording for later browser-based fetch
"""

import os
import urllib.parse
from typing import Dict, List

from config import MAX_RESULTS_PER_PLATFORM


def _format_result(url: str, title: str = "", platform_id: str = "") -> Dict:
    if not platform_id:
        path = urllib.parse.urlparse(url).path.strip("/")
        platform_id = path.split("/")[-1].split("?")[0] if path else url
    return {
        "platform": "douyin",
        "platform_id": platform_id,
        "title": title[:200] if title else f"[抖音/TikTok] {url}",
        "description": "",
        "url": url,
        "thumbnail_url": "",
        "author_name": "",
        "author_url": "",
        "published_at": "",
        "view_count": 0,
        "like_count": 0,
        "comment_count": 0,
        "duration_sec": 0,
        "content_type": "video",
        "score": 0.4,
        "fetch_method": "proxy",
    }


def _search_via_serpapi(query: str, max_results: int) -> List[Dict]:
    """Search TikTok via SerpAPI."""
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return []

    import json
    import urllib.request

    try:
        params = {
            "api_key": api_key,
            "engine": "google",
            "q": f"site:tiktok.com {query}",
            "hl": "zh-HK",
            "num": min(max_results, 10),
        }
        url = "https://serpapi.com/search?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        results = []
        for item in data.get("organic_results", [])[:max_results]:
            link = item.get("link", "")
            if "tiktok.com" in link or "douyin.com" in link:
                results.append(_format_result(
                    url=link,
                    title=item.get("title", ""),
                ))
        return results
    except Exception:
        return []


def _search_via_google_cse(query: str, max_results: int) -> List[Dict]:
    """Search via Google Custom Search."""
    api_key = os.getenv("GOOGLE_CSE_API_KEY") or os.getenv("CUSTOM_GOOGLE_API")
    cx = os.getenv("GOOGLE_CSE_CX") or os.getenv("CUSTOM_SEARCH_ENGINE_ID")
    if not api_key or not cx:
        return []

    import json
    import urllib.request

    try:
        site_query = f"(site:tiktok.com OR site:douyin.com) {query}"
        url = (f"https://www.googleapis.com/customsearch/v1"
               f"?key={api_key}&cx={cx}"
               f"&q={urllib.parse.quote(site_query)}"
               f"&lr=lang_zh-HK&num={min(max_results, 10)}")
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        results = []
        for item in data.get("items", [])[:max_results]:
            link = item.get("link", "")
            if "tiktok.com" in link or "douyin.com" in link:
                results.append(_format_result(
                    url=link,
                    title=item.get("title", ""),
                ))
        return results
    except Exception:
        return []


def _generate_search_urls(query: str) -> List[Dict]:
    """Fallback: generate search URLs for later browser-based fetch."""
    encoded = urllib.parse.quote(query)
    return [
        _format_result(
            url=f"https://www.tiktok.com/search?q={encoded}",
            title=f"{query} — TikTok Search",
            platform_id=f"search_{encoded}",
        ),
    ]


def search(query: str, max_results: int = MAX_RESULTS_PER_PLATFORM) -> List[Dict]:
    """Search Douyin/TikTok."""
    results = _search_via_serpapi(query, max_results)
    if results:
        return results
    results = _search_via_google_cse(query, max_results)
    if results:
        return results
    return _generate_search_urls(query)