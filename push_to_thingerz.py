"""
Push thingerz export JSON to thingerz.com API
Usage: python push_to_thingerz.py <json_file> [api_url] [api_key]

Defaults:
  api_url = https://thingerz.com/api/content
  api_key = thingerz_crawler_2026
  
Or set env vars: THINGERZ_API_URL, THINGERZ_API_KEY
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

def main():
    if len(sys.argv) < 2:
        print("Usage: python push_to_thingerz.py <export.json> [api_url] [api_key]")
        sys.exit(1)

    json_file = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else os.getenv("THINGERZ_API_URL", "https://thingerz.com/api/content")
    api_key = sys.argv[3] if len(sys.argv) > 3 else os.getenv("THINGERZ_API_KEY", "thingerz_crawler_2026")

    print(f"Reading: {json_file}")
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("Error: JSON must be an array of content items")
        sys.exit(1)

    total = len(data)
    print(f"Items to push: {total:,}")
    print(f"API URL: {api_url}")

    batch_size = 500
    sent = 0
    errors = 0

    for i in range(0, total, batch_size):
        batch = data[i : i + batch_size]
        payload = json.dumps({
            "key": api_key,
            "content": batch,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).encode("utf-8")

        req = urllib.request.Request(
            api_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "ThingerzCrawler/2.0",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = resp.read().decode()
                sent += len(batch)
                print(f"  Batch {i//batch_size + 1}/{(total-1)//batch_size + 1}: "
                      f"sent {len(batch)} items → HTTP {resp.status}")
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:200]
            print(f"  Batch {i//batch_size + 1} FAILED: HTTP {e.code} — {body}")
            errors += len(batch)
        except Exception as e:
            print(f"  Batch {i//batch_size + 1} FAILED: {e}")
            errors += len(batch)

    print(f"\nDone: {sent:,} sent, {errors:,} errors")

if __name__ == "__main__":
    main()