#!/bin/bash
echo "🚀 Bot launcher started — auto-restart enabled"

RESTART_DELAY=5
CRASH_COUNT=0
MAX_DELAY=60

kill_all() {
    # Kill any running bot processes
    pkill -9 -f "python bot.py" 2>/dev/null || true
    pkill -9 -f "python3 bot.py" 2>/dev/null || true

    # Force-release port 5000
    fuser -k 5000/tcp 2>/dev/null || true

    # Extra safety: kill via lsof if fuser not available
    lsof -ti:5000 2>/dev/null | xargs -r kill -9 2>/dev/null || true

    sleep 2
}

# Clear everything before first start
kill_all

while true; do
    echo "▶️  Starting bot.py... (restart #$CRASH_COUNT)"

    # Run with memory limit hint via ulimit (advisory, prevents slow OOM spiral)
    python -u bot.py
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ Bot exited cleanly (code 0). Restarting in ${RESTART_DELAY}s..."
        RESTART_DELAY=5
    elif [ $EXIT_CODE -eq 137 ]; then
        CRASH_COUNT=$((CRASH_COUNT + 1))
        # OOM kill — wait longer so OS can free memory
        RESTART_DELAY=$(( RESTART_DELAY < MAX_DELAY ? RESTART_DELAY * 2 : MAX_DELAY ))
        echo "💥 OOM kill (exit 137, crash #$CRASH_COUNT). Waiting ${RESTART_DELAY}s for memory to free..."
    else
        CRASH_COUNT=$((CRASH_COUNT + 1))
        echo "💥 Bot crashed with exit code $EXIT_CODE (crash #$CRASH_COUNT). Restarting in ${RESTART_DELAY}s..."
        RESTART_DELAY=5
    fi

    kill_all
    sleep $RESTART_DELAY
done
