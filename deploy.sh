#!/usr/bin/env bash
# Thingerz Deploy Helper — run once after cloning on your own machine
# Sets up GitHub repo + pushes, then gives you the Render connection steps.
set -euo pipefail

echo "=== Thingerz Deploy Helper ==="

# 1. GitHub auth check
if ! gh auth status &>/dev/null; then
  echo "GitHub CLI not authenticated."
  echo "  1. Create a token: https://github.com/settings/tokens (scopes: repo, workflow)"
  echo "  2. Run:  echo YOUR_TOKEN | gh auth login --with-token"
  exit 1
fi

# 2. Repo name
REPO_NAME="${1:-thingerz-crawler}"
REPO_VISIBILITY="${2:-public}"

# 3. Create repo if it doesn't exist
if ! gh repo view "$REPO_NAME" &>/dev/null; then
  echo "Creating GitHub repo: $REPO_NAME ($REPO_VISIBILITY)"
  gh repo create "$REPO_NAME" --"$REPO_VISIBILITY" --source . --remote origin --push
else
  echo "Repo exists — pushing to origin"
  git push -u origin main
fi

echo
echo "=== Next: Deploy on Render ==="
echo "  1. Go to https://render.com → New → Web Service"
echo "  2. Connect your GitHub account and pick the '$REPO_NAME' repo"
echo "  3. Render auto-detects render.yaml (build: pip install -r api/requirements.txt;"
echo "     start: python api/server.py; health: /api/stats)"
echo "  4. The dashboard will be live at https://thingerz-dashboard.onrender.com"
echo
echo "=== Optional: seed the database on Render ==="
echo "  The dashboard reads data/thingerz_crawler.db (gitignored). To seed it:"
echo "  - Add the DB to the Render service via a persistent disk, OR"
echo "  - POST /api/content from the crawler with a valid API key, OR"
echo "  - rsync/scp data/thingerz_crawler.db into the service shell"
echo
echo "=== API keys to configure on Render (env vars) ==="
echo "  THINGERZ_API_URL=https://thingerz.com/api/content"
echo "  THINGERZ_API_KEY=<your valid key>"
echo "  GOOGLE_CSE_API_KEY + GOOGLE_CSE_CX (optional, real results for IG/Threads/XHS/Douyin)"
echo "  SERPAPI_KEY (optional)"
echo
echo "Done."
