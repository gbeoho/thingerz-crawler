"""
小紅書 (Xiaohongshu / RED) search — multi-strategy approach.

Strategy 1: Google CSE (set GOOGLE_CSE_API_KEY + GOOGLE_CSE_CX)
Strategy 2: SerpAPI (set SERPAPI_KEY)
Strategy 3: Query recording for later browser-based fetch
"""

import os
import urllib.parse
from typing import Dict, List

from config import MAX_RESULTS_PER_PLATFORM

DOMAINS = ["xiaohongshu.com", "xhslink.com"]
PLATFORM = "xiaohongshu"


def _format_result(url: str, title: str = "", platform_id: str = "") -> Dict:
    if not platform_id:
        path = urllib.parse.urlparse(url).path.strip("/")
        platform_id = path.split("/")[-1].split("?")[0] if path else url
    return {
        "platform": PLATFORM,
        "platform_id": platform_id,
        "title": title[:200] if title else f"[小紅書] {url}",
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
        "content_type": "image",
        "score": 0.4,
        "fetch_method": "proxy",
    }


def _make_site_query(query: str) -> str:
    return " OR ".join(f"site:{d}" for d in DOMAINS) + f" {query}"


def _search_via_google_cse(query: str, max_results: int) -> List[Dict]:
    api_key = os.getenv("GOOGLE_CSE_API_KEY")
    cx = os.getenv("GOOGLE_CSE_CX")
    if not api_key or not cx:
        return []

    import json
    import urllib.request

    try:
        url = (f"https://www.googleapis.com/customsearch/v1"
               f"?key={api_key}&cx={cx}"
               f"&q={urllib.parse.quote(_make_site_query(query))}"
               f"&lr=lang_zh-HK&num={min(max_results, 10)}")
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        results = []
        for item in data.get("items", [])[:max_results]:
            link = item.get("link", "")
            if any(d in link for d in DOMAINS):
                results.append(_format_result(
                    url=link,
                    title=item.get("title", ""),
                ))
        return results
    except Exception:
        return []


def _search_via_serpapi(query: str, max_results: int) -> List[Dict]:
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return []

    import json
    import urllib.request

    try:
        params = {
            "api_key": api_key,
            "engine": "google",
            "q": _make_site_query(query),
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
            if any(d in link for d in DOMAINS):
                results.append(_format_result(
                    url=link,
                    title=item.get("title", ""),
                ))
        return results
    except Exception:
        return []


def _generate_search_urls(query: str) -> List[Dict]:
    """Fallback: generate 小紅書 search URLs."""
    encoded = urllib.parse.quote(query)
    return [
        _format_result(
            url=f"https://www.xiaohongshu.com/search_result?keyword={encoded}",
            title=f"{query} — 小紅書 Search",
            platform_id=f"search_{encoded}",
        ),
    ]


def search(query: str, max_results: int = MAX_RESULTS_PER_PLATFORM) -> List[Dict]:
    results = _search_via_google_cse(query, max_results)
    if results:
        return results
    results = _search_via_serpapi(query, max_results)
    if results:
        return results
    return _generate_search_urls(query)