#!/bin/bash
echo "🚀 Bot launcher started — auto-restart enabled"

RESTART_DELAY=5
CRASH_COUNT=0

kill_port() {
    pkill -f "python bot.py" 2>/dev/null || true
    fuser -k 8080/tcp 2>/dev/null || true
    kill $(lsof -t -i:8080 2>/dev/null) 2>/dev/null || true
}

while true; do
    # Kill any leftover processes holding port 8080
    kill_port
    sleep 4   # Give OS time to fully release the socket

    echo "▶️  Starting bot.py... (restart #$CRASH_COUNT)"
    python bot.py
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ Bot exited cleanly (code 0). Restarting..."
    else
        CRASH_COUNT=$((CRASH_COUNT + 1))
        echo "💥 Bot crashed with exit code $EXIT_CODE (crash #$CRASH_COUNT). Restarting in ${RESTART_DELAY}s..."
    fi

    sleep $RESTART_DELAY
done
