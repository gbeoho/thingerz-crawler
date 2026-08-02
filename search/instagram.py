"""
Instagram search — multi-strategy approach.

Strategy 1: Google Custom Search (via API key — set GOOGLE_CSE_API_KEY + GOOGLE_CSE_CX)
Strategy 2: SerpAPI (via API key — set SERPAPI_KEY)
Strategy 3: Query recording for later browser-based fetch (always works)
"""

import os
import urllib.parse
from typing import Dict, List

from config import MAX_RESULTS_PER_PLATFORM

DOMAIN = "instagram.com"
PLATFORM = "instagram"
PLATFORM_ZH = "Instagram"


def _format_result(url: str, title: str = "", platform_id: str = "") -> Dict:
    """Normalize a result into the standard format."""
    if not platform_id:
        path = urllib.parse.urlparse(url).path.strip("/")
        platform_id = path.split("/")[-1].split("?")[0] if path else url
    return {
        "platform": PLATFORM,
        "platform_id": platform_id,
        "title": title[:200] if title else f"[{PLATFORM_ZH}] {url}",
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


def _search_via_google_cse(query: str, max_results: int) -> List[Dict]:
    """Search via Google Custom Search JSON API."""
    api_key = os.getenv("GOOGLE_CSE_API_KEY") or os.getenv("CUSTOM_GOOGLE_API")
    cx = os.getenv("GOOGLE_CSE_CX") or os.getenv("CUSTOM_SEARCH_ENGINE_ID")
    if not api_key or not cx:
        return []

    import json
    import urllib.request

    try:
        site_query = f"site:{DOMAIN} {query}"
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
            # Filter to post URLs only
            if "/p/" in link or "/reel/" in link or "/reels/" in link:
                results.append(_format_result(
                    url=link,
                    title=item.get("title", ""),
                    platform_id=link.split("/p/")[-1].split("/")[0] if "/p/" in link
                    else link.split("/reel/")[-1].split("/")[0],
                ))
        return results
    except Exception:
        return []


def _search_via_serpapi(query: str, max_results: int) -> List[Dict]:
    """Search via SerpAPI (supports many engines)."""
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return []

    import json
    import urllib.request

    try:
        params = {
            "api_key": api_key,
            "engine": "google",
            "q": f"site:{DOMAIN} {query}",
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
            if "/p/" in link or "/reel/" in link or "/reels/" in link:
                results.append(_format_result(
                    url=link,
                    title=item.get("title", ""),
                ))
        return results
    except Exception:
        return []


def _generate_search_urls(query: str) -> List[Dict]:
    """
    Fallback: generate the Instagram search URL and record it.
    The actual fetch can be done via browser automation (Playwright)
    or the Instagram API.
    """
    # Instagram search URL format
    encoded = urllib.parse.quote(query)
    results = []
    # Tags
    results.append(_format_result(
        url=f"https://www.instagram.com/explore/tags/{encoded}/",
        title=f"#{query} — Instagram Tag Search",
        platform_id=f"tag_{encoded}",
    ))
    return results


def search(query: str, max_results: int = MAX_RESULTS_PER_PLATFORM) -> List[Dict]:
    """Search Instagram — tries API key methods first, then proxy, then URL generation."""
    # 1. Try Google CSE
    results = _search_via_google_cse(query, max_results)
    if results:
        return results

    # 2. Try SerpAPI
    results = _search_via_serpapi(query, max_results)
    if results:
        return results

    # 3. Fallback: generate search URLs for browser-based fetch
    return _generate_search_urls(query)