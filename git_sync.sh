#!/bin/bash
# Git sync — handles Replit's own git lock file conflicts

if [ -z "$GITHUB_TOKEN" ]; then
    echo "[git_sync] ERROR: GITHUB_TOKEN is not set."
    exit 1
fi

# ── Wait for any Replit-owned git locks to clear (up to 30s) ──────────
LOCK_WAIT=0
while [ -f .git/index.lock ] || [ -f .git/config.lock ]; do
    if [ $LOCK_WAIT -ge 30 ]; then
        echo "[git_sync] Lock files still present after 30s — force removing"
        rm -f .git/index.lock .git/config.lock .git/HEAD.lock \
               .git/refs/heads/main.lock .git/packed-refs.lock 2>/dev/null
        break
    fi
    sleep 1
    LOCK_WAIT=$((LOCK_WAIT + 1))
done
# Final cleanup just in case
rm -f .git/index.lock .git/config.lock .git/HEAD.lock \
       .git/refs/heads/main.lock .git/packed-refs.lock 2>/dev/null

git config --global user.email "bot@legendaryotp.replit"
git config --global user.name "Legendary OTP Bot"
git config --global credential.helper ""
git config --global core.askPass ""

REMOTE_URL=$(git remote get-url origin 2>/dev/null)
CLEAN_URL=$(echo "$REMOTE_URL" | sed 's|https://[^@]*@||' | sed 's|https://||')
AUTH_URL="https://${GITHUB_TOKEN}@${CLEAN_URL}"

restore_remote() {
    git remote set-url origin "$REMOTE_URL" 2>/dev/null || true
}
trap restore_remote EXIT

# Retry remote set-url up to 5 times if it fails due to lock
for i in 1 2 3 4 5; do
    git remote set-url origin "$AUTH_URL" 2>/dev/null && break
    sleep 2
    rm -f .git/config.lock 2>/dev/null
done

git add -A

if git diff --cached --quiet; then
    echo "[git_sync] No changes to commit."
    exit 0
fi

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
git commit -m "Auto-sync: $TIMESTAMP"

if git push origin main 2>&1; then
    echo "[git_sync] ✅ Pushed to GitHub at $TIMESTAMP"
    exit 0
fi

echo "[git_sync] Normal push failed. Doing fresh squash push..."

TMPBRANCH="fresh_$(date +%s)"
git checkout --orphan "$TMPBRANCH"
git add -A
git commit -m "Auto-sync (clean): $TIMESTAMP"
GIT_TERMINAL_PROMPT=0 git push origin "$TMPBRANCH:main" --force
git checkout main 2>/dev/null || git checkout -b main
git branch -D "$TMPBRANCH" 2>/dev/null || true
git reset --hard origin/main 2>/dev/null || true

echo "[git_sync] ✅ Fresh push done at $TIMESTAMP"
