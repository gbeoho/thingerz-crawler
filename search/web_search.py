"""
Unified Web Search — coordinates multiple search backends to find
social media content across platforms with public search restrictions.

Strategy:
  1. DuckDuckGo HTML (no JS required)
  2. Bing (with mobile UA)
  3. Google (with specific headers — may trigger CAPTCHA)
  4. Fallback: query-log only (records search intent for future browser-based fetch)

Each platform search module calls this instead of implementing its own.
"""

import json
import re
import time
import urllib.parse
import urllib.request
from typing import Dict, List, Optional

USER_AGENT_DESKTOP = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36")
USER_AGENT_MOBILE = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/120.0.0.0 Mobile Safari/537.36")


def _parse_duckduckgo_url(clean_url: str) -> Optional[str]:
    """Extract actual URL from DuckDuckGo redirect."""
    if "duckduckgo.com/l/" in clean_url or clean_url.startswith("//duckduckgo"):
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(clean_url).query)
        actual = urllib.parse.unquote(qs.get('uddg', [''])[0])
        return actual if actual else None
    return clean_url


def _search_duckduckgo(query: str, domain_filter: Optional[str] = None,
                       max_results: int = 10) -> List[Dict]:
    """Search via DuckDuckGo HTML (no JS needed). Returns raw results."""
    results = []
    try:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT_MOBILE,
            "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        seen = set()
        for m in re.finditer(r'class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)', html):
            url_str = m.group(1)
            title = m.group(2).strip()
            raw_url = _parse_duckduckgo_url(url_str.split("&")[0])
            if not raw_url:
                continue
            if domain_filter and domain_filter not in raw_url:
                continue
            if raw_url in seen:
                continue
            seen.add(raw_url)
            results.append({
                "raw_url": raw_url,
                "title": re.sub(r'<[^>]+>', '', title).strip(),
            })
            if len(results) >= max_results:
                break
    except Exception:
        pass
    return results


def _search_bing(query: str, domain_filter: Optional[str] = None,
                 max_results: int = 10) -> List[Dict]:
    """Search via Bing."""
    results = []
    try:
        url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&setlang=zh-HK"
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT_MOBILE,
            "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Bing puts URLs in <cite> tags and <a> tags
        seen = set()
        # Pattern 1: <cite> tags
        for m in re.finditer(r'<cite[^>]*>([^<]+)</cite>', html):
            clean_url = m.group(1).strip()
            if domain_filter and domain_filter not in clean_url:
                continue
            if clean_url in seen:
                continue
            seen.add(clean_url)
            results.append({
                "raw_url": clean_url,
                "title": "",
            })
            if len(results) >= max_results:
                break

        # Pattern 2: <a> hrefs
        if len(results) < max_results:
            for m in re.finditer(r'<a[^>]*href="(https?://[^"]*)"[^>]*>', html):
                clean_url = urllib.parse.unquote(m.group(1))
                if domain_filter and domain_filter not in clean_url:
                    continue
                if clean_url in seen:
                    continue
                seen.add(clean_url)
                results.append({
                    "raw_url": clean_url,
                    "title": "",
                })
                if len(results) >= max_results:
                    break
    except Exception:
        pass
    return results


def search_web(query: str, domain_filter: Optional[str] = None,
               max_results: int = 10) -> List[Dict]:
    """
    Multi-backend web search for social media content.
    Tries DuckDuckGo first, falls back to Bing.

    Returns list of dicts with 'raw_url' and 'title'.
    """
    results = _search_duckduckgo(query, domain_filter, max_results)
    if not results:
        results = _search_bing(query, domain_filter, max_results)
    time.sleep(0.5)  # be polite
    return results