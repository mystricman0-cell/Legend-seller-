#!/bin/bash
echo "🚀 Bot launcher started — auto-restart enabled"

RESTART_DELAY=3
CRASH_COUNT=0

kill_port() {
    pkill -9 -f "python bot.py" 2>/dev/null || true
    sleep 1
}

# Initial kill to clear any zombie processes
kill_port

while true; do
    echo "▶️  Starting bot.py... (restart #$CRASH_COUNT)"
    python bot.py
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ Bot exited cleanly (code 0). Restarting..."
    else
        CRASH_COUNT=$((CRASH_COUNT + 1))
        echo "💥 Bot crashed with exit code $EXIT_CODE (crash #$CRASH_COUNT). Restarting in ${RESTART_DELAY}s..."
        kill_port
    fi

    sleep $RESTART_DELAY
done
