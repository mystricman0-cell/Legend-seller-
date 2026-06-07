import os
import time
import subprocess

CHECK_INTERVAL = 30

def has_git_changes():
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True
    )
    return bool(result.stdout.strip())

def run_sync():
    result = subprocess.run(
        ["bash", "git_sync.sh"],
        capture_output=True,
        text=True
    )
    if result.stdout:
        print(result.stdout.strip(), flush=True)
    if result.stderr:
        print("[git_sync stderr]", result.stderr.strip(), flush=True)
    return result.returncode == 0

def main():
    print(f"[file_watcher] Monitoring all git-tracked changes. Check interval: {CHECK_INTERVAL}s", flush=True)

    while True:
        time.sleep(CHECK_INTERVAL)
        if has_git_changes():
            print("[file_watcher] Detected uncommitted changes, syncing to GitHub...", flush=True)
            success = run_sync()
            if success:
                print("[file_watcher] Sync successful.", flush=True)
            else:
                print("[file_watcher] Sync FAILED. Will retry on next interval.", flush=True)

if __name__ == "__main__":
    main()
