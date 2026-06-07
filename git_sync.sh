#!/bin/bash
set -e

if [ -z "$GITHUB_TOKEN" ]; then
    echo "[git_sync] ERROR: GITHUB_TOKEN is not set. Cannot push to GitHub."
    exit 1
fi

REMOTE_URL=$(git remote get-url origin 2>/dev/null)
CLEAN_URL=$(echo "$REMOTE_URL" | sed 's|https://[^@]*@||' | sed 's|https://||')
AUTH_URL="https://${GITHUB_TOKEN}@${CLEAN_URL}"

restore_remote() {
    git remote set-url origin "$REMOTE_URL" 2>/dev/null || true
}
trap restore_remote EXIT

git remote set-url origin "$AUTH_URL"

git add -A

if git diff --cached --quiet; then
    echo "[git_sync] No changes to commit."
    exit 0
fi

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
git commit -m "Auto-sync: $TIMESTAMP"
git push origin main
echo "[git_sync] Pushed to GitHub at $TIMESTAMP"
