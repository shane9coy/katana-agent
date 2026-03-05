#!/usr/bin/env python3
"""
x_send_dm.py
─────────────────────────────────────────────────────────────────────────────
Send a DM to one or multiple X users by @username.

Features:
  • Resolves @username → user ID automatically
  • Skips users already in the sent log (safe to re-run)
  • Per-batch JSON log saved to state/dm_batch_<id>.json
  • Terminal shows @handle + uid for every action
  • Estimated cost printed at the end

Setup:
  pip install tweepy python-dotenv

.env required keys:
  X_SWRLD_BEARER_TOKEN
  X_SWRLD_CONSUMER_KEY
  X_SWRLD_CONSUMER_SECRET
  X_SWRLD_ACCESS_TOKEN
  X_SWRLD_ACCESS_TOKEN_SECRET
"""

import os
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import tweepy
from dotenv import load_dotenv

load_dotenv()

# ══════════════════════════════════════════════════════════════════
#  CONFIG — edit before each send
# ══════════════════════════════════════════════════════════════════

DM_TEXT = """Hey! This will take your agentic engineering skills to the next level🔥

Here's the Agent Skills Architecture Guide:

📄 PDF: https://bit.ly/3Ov3Z9G
📁 Repo: https://github.com/shane9coy/Agent-Skill-Architecture-Guide

Drop a ⭐ on the repo if it helps!"""

# Add as many @handles as you want (no @ symbol needed)
RECIPIENTS = [
    "vibestoicism",
    # "another_user",
    # "yet_another",
]

# ══════════════════════════════════════════════════════════════════
#  COST CONSTANTS
# ══════════════════════════════════════════════════════════════════

COST_PER_USER_LOOKUP = 0.005   # GET /2/users/by/username/:username
COST_PER_DM          = 0.015   # POST /2/dm_conversations/with/:id/messages

# ══════════════════════════════════════════════════════════════════
#  PATHS
# ══════════════════════════════════════════════════════════════════

STATE_DIR = Path("state")
STATE_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════

BEARER_TOKEN        = os.getenv("X_SWRLD_BEARER_TOKEN")
CONSUMER_KEY        = os.getenv("X_SWRLD_CONSUMER_KEY")
CONSUMER_SECRET     = os.getenv("X_SWRLD_CONSUMER_SECRET")
ACCESS_TOKEN        = os.getenv("X_SWRLD_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("X_SWRLD_ACCESS_TOKEN_SECRET")

for name, val in [
    ("X_SWRLD_BEARER_TOKEN",        BEARER_TOKEN),
    ("X_SWRLD_CONSUMER_KEY",        CONSUMER_KEY),
    ("X_SWRLD_CONSUMER_SECRET",     CONSUMER_SECRET),
    ("X_SWRLD_ACCESS_TOKEN",        ACCESS_TOKEN),
    ("X_SWRLD_ACCESS_TOKEN_SECRET", ACCESS_TOKEN_SECRET),
]:
    if not val:
        sys.exit(f"❌  Missing env var: {name}")

# OAuth 1.0a client — required for sending DMs (user-context action)
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True,
)

# ══════════════════════════════════════════════════════════════════
#  BATCH LOG
# ══════════════════════════════════════════════════════════════════

def init_batch_log(batch_id: str) -> dict:
    return {
        "id":            batch_id,
        "started_at":    datetime.now(timezone.utc).isoformat(),
        "finished_at":   None,
        "recipients":    RECIPIENTS,
        "results":       [],   # {username, uid, status, reason, timestamp}
        "sent":          0,
        "skipped":       0,
        "failed":        0,
        "estimated_cost": 0.0,
    }

def save_log(log: dict, path: Path):
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(log, f, indent=2)
    tmp.replace(path)

def log_result(log: dict, username: str, uid: str | None,
               status: str, reason: str = ""):
    log["results"].append({
        "username":  username,
        "uid":       uid,
        "status":    status,   # sent | skipped | failed
        "reason":    reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    if status == "sent":    log["sent"]    += 1
    if status == "skipped": log["skipped"] += 1
    if status == "failed":  log["failed"]  += 1

# ══════════════════════════════════════════════════════════════════
#  CORE FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def resolve_user(username: str, log: dict) -> tuple[str | None, str | None]:
    """
    Resolve @username → (uid, display_handle).
    Returns (None, None) on failure.
    """
    log["estimated_cost"] += COST_PER_USER_LOOKUP
    try:
        resp = client.get_user(username=username, user_fields=["username"])
        if resp.data:
            uid    = str(resp.data.id)
            handle = f"@{resp.data.username}"
            print(f"  ✅ Resolved {handle} → {uid}")
            return uid, handle
        print(f"  ❌ @{username} not found")
        return None, None
    except Exception as e:
        print(f"  ❌ Failed to resolve @{username}: {e}")
        return None, None


def already_sent(uid: str, log: dict) -> bool:
    """Check if this uid already received a DM in this batch."""
    return any(r["uid"] == uid and r["status"] == "sent" for r in log["results"])


def send_dm(uid: str, handle: str, log: dict) -> bool:
    """Send DM to uid. Returns True on success."""
    if already_sent(uid, log):
        print(f"  ⏭️  {handle} ({uid}) already sent in this batch — skipping")
        log_result(log, handle, uid, "skipped", "already sent in batch")
        return False

    log["estimated_cost"] += COST_PER_DM
    try:
        client.create_direct_message(participant_id=uid, text=DM_TEXT)
        print(f"  ✅ DM sent → {handle} ({uid})")
        log_result(log, handle, uid, "sent")
        return True
    except Exception as e:
        print(f"  ❌ DM failed → {handle} ({uid}): {e}")
        log_result(log, handle, uid, "failed", str(e))
        return False

# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    batch_id  = uuid.uuid4().hex[:8]
    log       = init_batch_log(batch_id)
    log_path  = STATE_DIR / f"dm_batch_{batch_id}.json"
    start_ts  = time.time()

    print("═" * 60)
    print(f"  📨 DM Batch Sender")
    print(f"  Batch ID:    {batch_id}")
    print(f"  Recipients:  {len(RECIPIENTS)}")
    print(f"  Started:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 60)

    if not RECIPIENTS:
        sys.exit("❌  RECIPIENTS list is empty — add usernames to the config.")

    for username in RECIPIENTS:
        print(f"\n→ Processing @{username}…")

        uid, handle = resolve_user(username, log)
        if uid is None:
            log_result(log, username, None, "failed", "could not resolve user ID")
            save_log(log, log_path)
            continue

        send_dm(uid, handle, log)
        save_log(log, log_path)

        # Small delay between sends — avoids rate limit edge cases on bulk lists
        if RECIPIENTS.index(username) < len(RECIPIENTS) - 1:
            time.sleep(1)

    # ── finalise ────────────────────────────────────────────────
    elapsed = time.time() - start_ts
    log["finished_at"] = datetime.now(timezone.utc).isoformat()
    save_log(log, log_path)

    print("\n" + "═" * 60)
    print(f"  📊 BATCH SUMMARY")
    print("═" * 60)
    print(f"  Sent:          {log['sent']}")
    print(f"  Skipped:       {log['skipped']}")
    print(f"  Failed:        {log['failed']}")
    print(f"  Est. cost:     ${log['estimated_cost']:.3f}")
    print(f"  Duration:      {elapsed:.1f}s")
    print(f"  Log saved →    {log_path}")
    print("═" * 60)


if __name__ == "__main__":
    main()
