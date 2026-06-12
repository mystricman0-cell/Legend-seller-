---
name: Port configuration for this Replit bot
description: Port 8080 permanently blocked; correct setup uses port 5000 with console workflow.
---

## Rule
Always run the Flask webhook server on port **5000** in this Replit environment.

**Why:** Port 8080 is permanently occupied by something in the Replit container (confirmed via `/proc/net/tcp` and Python bind tests). Port 5000 is always free and bindable.

## How to apply
- `WEBHOOK_PORT = int(os.getenv("PORT", 5000))` in bot.py
- `.replit` [[ports]] → `localPort = 5000, externalPort = 80` (updated via configureWorkflow)
- Workflow configured with `outputType: "console"` (NOT "webview") — webview sends SIGTERM if port doesn't open fast enough; bot startup takes ~3-5 seconds.
- `socketserver.TCPServer.allow_reuse_address = True` set in bot.py before Flask.run() for SO_REUSEADDR.
- `run.sh`: no long sleep delays; `pkill -9 -f "python bot.py"` on restart to clear zombies.

## What NOT to do
- Do NOT set `waitForPort: 5000` with `outputType: "webview"` — Replit sends SIGTERM before bot can start (exit code 143).
- Do NOT use `fuser` — not available in NixOS container.
- Do NOT try port 8080 — permanently blocked, always fails with "[Errno 98] Address already in use".
