"""
Search module registry — all platforms advertise a unified `search(query, max_results)`.
"""

from typing import Dict, List, Callable

from config import PLATFORMS

SEARCHERS: Dict[str, Callable] = {}

# Lazy-import each platform's search function
def _load_searchers():
    global SEARCHERS
    if SEARCHERS:
        return
    for key in PLATFORMS:
        if not PLATFORMS[key]["enabled"]:
            continue
        try:
            mod = __import__(f"search.{key}", fromlist=["search"])
            SEARCHERS[key] = mod.search
        except ImportError as e:
            # Don't crash on missing modules
            pass


def search_all(query: str, max_results: int = 10) -> Dict[str, List[Dict]]:
    """Run a query across every enabled platform."""
    _load_searchers()
    results = {}
    for platform, searcher in SEARCHERS.items():
        try:
            items = searcher(query, max_results)
            results[platform] = items
        except Exception:
            results[platform] = []
    return results


def search_platform(platform: str, query: str, max_results: int = 10) -> List[Dict]:
    """Run a query on a single platform."""
    _load_searchers()
    searcher = SEARCHERS.get(platform)
    if not searcher:
        return []
    try:
        return searcher(query, max_results)
    except Exception:
        return []