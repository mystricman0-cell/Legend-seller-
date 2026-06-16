#!/bin/bash
echo "🚀 Bot launcher started — auto-restart enabled"

RESTART_DELAY=5
CRASH_COUNT=0
MAX_DELAY=60

kill_all() {
    # Kill bot processes
    pkill -9 -f "python bot.py"  2>/dev/null || true
    pkill -9 -f "python3 bot.py" 2>/dev/null || true

    # Kill anything on port 5000 using Python (works without fuser/lsof)
    python3 -c "
import subprocess, os, time
try:
    r = subprocess.run(['ss','-tlnp','sport = :5000'], capture_output=True, text=True, timeout=5)
    for line in r.stdout.splitlines():
        if ':5000' in line and 'pid=' in line:
            pid = line.split('pid=')[1].split(',')[0]
            os.kill(int(pid), 9)
            print(f'Killed PID {pid} on port 5000')
except Exception: pass
try:
    with open('/proc/net/tcp') as f:
        lines = f.readlines()[1:]
    for line in lines:
        parts = line.split()
        if len(parts) > 9 and int(parts[1].split(':')[1],16)==5000:
            inode = parts[9]
            for pid in os.listdir('/proc'):
                if not pid.isdigit(): continue
                try:
                    for fd in os.listdir(f'/proc/{pid}/fd'):
                        if f'socket:[{inode}]' in os.readlink(f'/proc/{pid}/fd/{fd}'):
                            os.kill(int(pid), 9)
                            print(f'Killed PID {pid} (inode {inode})')
                except Exception: pass
except Exception: pass
" 2>/dev/null || true

    sleep 2
}

# Clear everything before first start
kill_all

while true; do
    echo "▶️  Starting bot.py... (restart #$CRASH_COUNT)"
    python -u bot.py
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ Bot exited cleanly. Restarting in ${RESTART_DELAY}s..."
        RESTART_DELAY=5
    elif [ $EXIT_CODE -eq 137 ]; then
        CRASH_COUNT=$((CRASH_COUNT + 1))
        RESTART_DELAY=$(( RESTART_DELAY < MAX_DELAY ? RESTART_DELAY * 2 : MAX_DELAY ))
        echo "💥 OOM kill (exit 137, crash #$CRASH_COUNT). Waiting ${RESTART_DELAY}s..."
    else
        CRASH_COUNT=$((CRASH_COUNT + 1))
        echo "💥 Crashed exit=$EXIT_CODE (crash #$CRASH_COUNT). Restarting in ${RESTART_DELAY}s..."
        RESTART_DELAY=5
    fi

    kill_all
    sleep $RESTART_DELAY
done
