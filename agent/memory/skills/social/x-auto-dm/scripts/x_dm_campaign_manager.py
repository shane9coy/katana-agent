#!/usr/bin/env python3
"""
x_campaign_manager.py
─────────────────────────────────────────────────────────────────────────────
Production-grade X (Twitter) DM campaign manager.

Features:
  • Real-time reply monitoring via Filtered Stream
  • Follow check: single GET /2/users/:id?user.fields=connection_status call
    → "followed_by" in result = they follow us. Flat $0.005, no pagination.
  • Nudge → ignore-list logic (one nudge per user, then blacklist)
  • Per-campaign JSON analytics (comments, DMs, followers, cost, duration, headline)
  • Central campaigns registry JSON with file locking (safe for 2 parallel campaigns)
  • Graceful shutdown (Ctrl+C) with final stats saved

Setup:
  pip install tweepy python-dotenv filelock requests requests-oauthlib

.env required keys:
  X_SWRLD_BEARER_TOKEN
  X_SWRLD_CONSUMER_KEY
  X_SWRLD_CONSUMER_SECRET
  X_SWRLD_ACCESS_TOKEN
  X_SWRLD_ACCESS_TOKEN_SECRET
"""

import os
import json
import signal
import sys
import time
import uuid
import threading
from datetime import datetime, timezone
from pathlib import Path

import tweepy
from dotenv import load_dotenv
from filelock import FileLock, Timeout

load_dotenv()

# ══════════════════════════════════════════════════════════════════
#  CAMPAIGN CONFIG — edit these before each launch
# ══════════════════════════════════════════════════════════════════

CAMPAIGN = {
    "headline":     "Agent Skills Architecture Guide 🔥",   # scroll-stopper / campaign label
    "post_id":      "2024272175012712946",                  # the X post you're monitoring replies on
    "keywords":     ["skills", "skill", "skil"],            # triggers (matched case-insensitive)
    "our_username": "shaneswrld_",                          # YOUR username (no @)
    "dm_text": (
        "Hey! This will take your agentic engineering skills to the next level🔥\n\n"
        "Here's the Agent Skills Architecture Guide:\n\n"
        "📄 PDF: https://bit.ly/3Ov3Z9G\n"
        "📁 Repo: https://github.com/shane9coy/Agent-Skill-Architecture-Guide"
        "Drop a ⭐ on the repo if it helps!"
    ),
    "nudge_text": (
        "Make sure you're following so I can DM you! "
        "Comment one of: skills / skill / skil again once you follow."
    ),
}

# ══════════════════════════════════════════════════════════════════
#  PATHS & LOCKING
# ══════════════════════════════════════════════════════════════════

STATE_DIR   = Path("state")
STATE_DIR.mkdir(exist_ok=True)

CAMPAIGNS_FILE = STATE_DIR / "campaigns.json"          # central registry
CAMPAIGNS_LOCK = STATE_DIR / "campaigns.json.lock"     # exclusive write lock

# ══════════════════════════════════════════════════════════════════
#  COST CONSTANTS  (from x-api-costs.md)
# ══════════════════════════════════════════════════════════════════

COST = {
    "follow_check": 0.005,   # GET /2/users/:id/followers
    "reply_tweet":  0.005,   # POST /2/tweets
    "send_dm":      0.015,   # POST /2/dm_conversations/with/:id/messages
}

# ══════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════

BEARER_TOKEN         = os.getenv("X_SWRLD_BEARER_TOKEN")
CONSUMER_KEY         = os.getenv("X_SWRLD_CONSUMER_KEY")
CONSUMER_SECRET      = os.getenv("X_SWRLD_CONSUMER_SECRET")
ACCESS_TOKEN         = os.getenv("X_SWRLD_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET  = os.getenv("X_SWRLD_ACCESS_TOKEN_SECRET")

for name, val in [
    ("X_SWRLD_BEARER_TOKEN",        BEARER_TOKEN),
    ("X_SWRLD_CONSUMER_KEY",        CONSUMER_KEY),
    ("X_SWRLD_CONSUMER_SECRET",     CONSUMER_SECRET),
    ("X_SWRLD_ACCESS_TOKEN",        ACCESS_TOKEN),
    ("X_SWRLD_ACCESS_TOKEN_SECRET", ACCESS_TOKEN_SECRET),
]:
    if not val:
        sys.exit(f"❌  Missing env var: {name}")

# OAuth 1.0a client — required for DMs and tweeting (user-context actions)
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True,
)

# Resolved once at startup — used to filter out our own tweets in the stream
OUR_USER_ID: str | None = None   # populated in main() before stream starts

# ══════════════════════════════════════════════════════════════════
#  CAMPAIGN STATE (per-run JSON)
# ══════════════════════════════════════════════════════════════════

class CampaignState:
    """Manages per-campaign state files with thread-safe writes."""

    def __init__(self, campaign_id: str):
        self.id           = campaign_id
        self.path         = STATE_DIR / f"campaign_{campaign_id}.json"
        self.lock         = threading.Lock()
        self._in_flight   = set()          # uids currently being processed
        self._flight_lock = threading.Lock()

        if self.path.exists():
            with open(self.path) as f:
                self._data = json.load(f)
        else:
            self._data = {
                "id":               campaign_id,
                "headline":         CAMPAIGN["headline"],
                "post_id":          CAMPAIGN["post_id"],
                "keywords":         CAMPAIGN["keywords"],
                "started_at":       datetime.now(timezone.utc).isoformat(),
                "stopped_at":       None,
                "total_seconds":    0,
                "comments_seen":    0,
                "keyword_hits":     0,
                "dms_sent":         0,
                "nudges_sent":      0,
                "new_followers":    0,   # increment manually or via separate check
                "estimated_cost":   0.0,
                "processed_tweets": [],  # tweet IDs already handled
                "dm_sent_to":       [],  # user IDs that got a DM
                "nudge_sent_to":    [],  # user IDs that got a nudge (one-time)
                "ignored_users":    [],  # user IDs permanently skipped (nudged + still not following)
                "username_cache":   {},  # uid → @handle lookup cache
            }
            self._save_unlocked()

    # ── internal helpers ──────────────────────────────────────────

    def _save_unlocked(self):
        """Write to disk — caller must hold self.lock."""
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w") as f:
            json.dump(self._data, f, indent=2)
        tmp.replace(self.path)

    def save(self):
        with self.lock:
            self._save_unlocked()

    # ── set-based helpers ─────────────────────────────────────────

    def _in(self, key, value):
        return str(value) in self._data[key]

    def _add(self, key, value):
        s = str(value)
        if s not in self._data[key]:
            self._data[key].append(s)

    # ── public API ────────────────────────────────────────────────

    def already_processed(self, tweet_id): return self._in("processed_tweets", tweet_id)
    def mark_processed(self, tweet_id):
        with self.lock:
            self._add("processed_tweets", tweet_id)

    def already_dmed(self, user_id):       return self._in("dm_sent_to", user_id)
    def mark_dmed(self, user_id):
        with self.lock:
            self._add("dm_sent_to", user_id)
            self._data["dms_sent"] += 1
            self._data["estimated_cost"] += COST["send_dm"]
            self._save_unlocked()

    def already_nudged(self, user_id):    return self._in("nudge_sent_to", user_id)
    def mark_nudged(self, user_id):
        with self.lock:
            self._add("nudge_sent_to", user_id)
            self._data["nudges_sent"] += 1
            self._data["estimated_cost"] += COST["reply_tweet"]
            self._save_unlocked()

    def is_ignored(self, user_id):        return self._in("ignored_users", user_id)
    def mark_ignored(self, user_id):
        with self.lock:
            self._add("ignored_users", user_id)
            self._save_unlocked()

    def increment_comments(self):
        with self.lock:
            self._data["comments_seen"] += 1
            self._save_unlocked()

    def increment_keyword_hits(self):
        with self.lock:
            self._data["keyword_hits"] += 1
            self._save_unlocked()

    def add_follow_check_cost(self):
        with self.lock:
            self._data["estimated_cost"] += COST["follow_check"]
            self._save_unlocked()

    def get_cached_username(self, uid: str) -> str:
        """Return cached @handle or fallback uid string."""
        return self._data.get("username_cache", {}).get(str(uid), f"uid:{uid}")

    def resolve_username(self, uid: str, tw_client) -> str:
        """Return @handle for uid, fetching from API once then caching."""
        cached = self._data.get("username_cache", {}).get(str(uid))
        if cached:
            return cached
        try:
            resp = tw_client.get_user(id=uid, user_fields=["username"])
            if resp.data:
                handle = f"@{resp.data.username}"
                with self.lock:
                    self._data.setdefault("username_cache", {})[str(uid)] = handle
                    self._save_unlocked()
                return handle
        except Exception:
            pass
        return f"uid:{uid}"

    def acquire_user_lock(self, uid: str) -> bool:
        """Returns True if lock acquired (safe to proceed), False if already in flight."""
        with self._flight_lock:
            if uid in self._in_flight:
                return False
            self._in_flight.add(uid)
            return True

    def release_user_lock(self, uid: str):
        with self._flight_lock:
            self._in_flight.discard(uid)

    def finalize(self, started_ts: float):
        with self.lock:
            self._data["stopped_at"]    = datetime.now(timezone.utc).isoformat()
            self._data["total_seconds"] = int(time.time() - started_ts)
            self._save_unlocked()

    def summary(self) -> dict:
        with self.lock:
            return dict(self._data)


# ══════════════════════════════════════════════════════════════════
#  CENTRAL CAMPAIGNS REGISTRY
# ══════════════════════════════════════════════════════════════════

def register_campaign(campaign_id: str, headline: str, post_id: str):
    """Add or update an entry in the central campaigns.json (file-locked)."""
    lock = FileLock(str(CAMPAIGNS_LOCK), timeout=10)
    try:
        with lock:
            if CAMPAIGNS_FILE.exists():
                with open(CAMPAIGNS_FILE) as f:
                    registry = json.load(f)
            else:
                registry = {"campaigns": []}

            entry = {
                "id":         campaign_id,
                "headline":   headline,
                "post_id":    post_id,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "status":     "running",
                "state_file": str(STATE_DIR / f"campaign_{campaign_id}.json"),
            }
            # Replace if already exists
            registry["campaigns"] = [c for c in registry["campaigns"] if c["id"] != campaign_id]
            registry["campaigns"].append(entry)

            with open(CAMPAIGNS_FILE, "w") as f:
                json.dump(registry, f, indent=2)
    except Timeout:
        print("⚠️  Could not acquire campaigns.json lock — registry not updated this cycle.")


def update_campaign_status(campaign_id: str, status: str, summary: dict):
    """Mark a campaign done/stopped and write final stats to the registry."""
    lock = FileLock(str(CAMPAIGNS_LOCK), timeout=10)
    try:
        with lock:
            if not CAMPAIGNS_FILE.exists():
                return
            with open(CAMPAIGNS_FILE) as f:
                registry = json.load(f)

            for c in registry["campaigns"]:
                if c["id"] == campaign_id:
                    c["status"]        = status
                    c["stopped_at"]    = summary.get("stopped_at")
                    c["total_seconds"] = summary.get("total_seconds", 0)
                    c["dms_sent"]      = summary.get("dms_sent", 0)
                    c["nudges_sent"]   = summary.get("nudges_sent", 0)
                    c["keyword_hits"]  = summary.get("keyword_hits", 0)
                    c["estimated_cost"]= summary.get("estimated_cost", 0.0)
                    break

            with open(CAMPAIGNS_FILE, "w") as f:
                json.dump(registry, f, indent=2)
    except Timeout:
        print("⚠️  Could not acquire campaigns.json lock for final update.")


# ══════════════════════════════════════════════════════════════════
#  FOLLOW CHECK  — raw OAuth 1.0a HTTP call (bypasses tweepy dataclass)
# ══════════════════════════════════════════════════════════════════
#
# WHY raw requests instead of tweepy.Client.get_user():
#   Tweepy deserialises responses into dataclasses that only map known
#   fields. "connection_status" is silently dropped — resp.data.connection_status
#   always returns None even when the API returned it. Hitting the
#   endpoint directly with requests-oauthlib gives us the full raw JSON.
#
# COST: 1 × GET /2/users/:id = $0.005 flat, no pagination ever.

import requests
from requests_oauthlib import OAuth1

_oauth1 = OAuth1(
    client_key=CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key=ACCESS_TOKEN,
    resource_owner_secret=ACCESS_TOKEN_SECRET,
)


def is_following_us(target_uid: str, state: CampaignState) -> bool:
    """
    Returns True if target_uid follows the authenticated account.
    Calls GET /2/users/:id?user.fields=connection_status,username
    signed with OAuth 1.0a so X returns the authenticated relationship context.
    "followed_by" in connection_status → they follow us.
    """
    state.add_follow_check_cost()
    url    = f"https://api.x.com/2/users/{target_uid}"
    params = {"user.fields": "connection_status,username"}

    try:
        r    = requests.get(url, params=params, auth=_oauth1, timeout=10)
        body = r.json()

        # Print full raw response so we can debug if something unexpected comes back
        print(f"  🌐 Raw follow-check response: {json.dumps(body)}")

        if "data" not in body:
            print(f"  ⚠️  No 'data' key in response — {body.get('errors', body)}")
            return False

        user_data  = body["data"]
        username   = user_data.get("username", target_uid)
        connection = user_data.get("connection_status", [])

        print(f"  🔗 @{username} ({target_uid}) connection_status: {connection}")

        if not connection:
            print(f"  ⚠️  connection_status is empty — field may need Elevated access or OAuth scope")

        return "followed_by" in connection

    except Exception as e:
        print(f"  ⚠️  Follow check error for {target_uid}: {e}")
        return False


# ══════════════════════════════════════════════════════════════════
#  ACTIONS
# ══════════════════════════════════════════════════════════════════

def send_dm(uid: str, handle: str, state: CampaignState):
    if state.already_dmed(uid):
        print(f"  → already DM'd {handle} ({uid}), skipping")
        return
    try:
        client.create_direct_message(participant_id=uid, text=CAMPAIGN["dm_text"])
        state.mark_dmed(uid)
        print(f"  ✅ DM sent → {handle} ({uid})")
    except Exception as e:
        print(f"  ❌ DM failed for {handle} ({uid}): {e}")


def send_nudge(reply_tweet_id: str, uid: str, handle: str, state: CampaignState):
    nudge = CAMPAIGN["nudge_text"].format(our_username=CAMPAIGN["our_username"])
    try:
        client.create_tweet(text=nudge, in_reply_to_tweet_id=reply_tweet_id)
        state.mark_nudged(uid)
        print(f"  💬 Nudge sent → {handle} ({uid}) under tweet {reply_tweet_id}")
    except Exception as e:
        print(f"  ❌ Nudge failed for {handle} ({uid}): {e}")


# ══════════════════════════════════════════════════════════════════
#  STREAM LISTENER
# ══════════════════════════════════════════════════════════════════

class CampaignStream(tweepy.StreamingClient):

    def __init__(self, bearer_token: str, state: CampaignState, **kwargs):
        super().__init__(bearer_token, **kwargs)
        self.state = state

    def on_tweet(self, tweet):
        tid  = str(tweet.id)
        uid  = str(tweet.author_id) if tweet.author_id else None
        text = tweet.text or ""

        self.state.increment_comments()

        # ── dedupe: already processed this exact tweet? ─────────────
        if self.state.already_processed(tid):
            return
        self.state.mark_processed(tid)

        # ── uid required ────────────────────────────────────────────
        if uid is None:
            print("   ⚠️  No author_id in tweet — skipping")
            return

        # ── PIPELINE STEP 0: never process our own tweets ───────────
        if OUR_USER_ID and uid == OUR_USER_ID:
            return  # silent — happens every time we send a nudge
        if self.state.is_ignored(uid):
            handle = self.state.get_cached_username(uid)
            print(f"   🚫 {handle} ({uid}) on ignore list — skipping (no API call)")
            return

        # ── PIPELINE STEP 2: already DM'd (no API) ──────────────────
        if self.state.already_dmed(uid):
            handle = self.state.get_cached_username(uid)
            print(f"   → already DM'd {handle} ({uid}) — skipping")
            return

        # ── PIPELINE STEP 3: keyword gate (no API) ──────────────────
        text_lower = text.lower()
        if not any(kw in text_lower for kw in CAMPAIGN["keywords"]):
            return

        # Resolve username (1 cheap API call, cached after first hit)
        handle = self.state.resolve_username(uid, client)

        self.state.increment_keyword_hits()
        print(f"\n🔑 Keyword hit | tweet={tid} | {handle} ({uid})")
        print(f"   \"{text[:80]}\"")

        # ── PIPELINE STEP 4: per-user mutex (prevents double fire) ──
        if not self.state.acquire_user_lock(uid):
            print(f"   ⏳ {handle} ({uid}) already being processed — dropping duplicate event")
            return

        try:
            # ── PIPELINE STEP 5: follow check (1 API call) ──────────
            print(f"   → checking if {handle} follows us…")
            following = is_following_us(uid, self.state)

            if following:
                print(f"   → {handle} follows us ✅ — sending DM")
                send_dm(uid, handle, self.state)
            else:
                print(f"   → {handle} does NOT follow us")
                if self.state.already_nudged(uid):
                    print(f"   → {handle} already nudged once — adding to ignore list")
                    self.state.mark_ignored(uid)
                else:
                    print(f"   → {handle} first-time non-follower — sending nudge")
                    send_nudge(tid, uid, handle, self.state)
        finally:
            self.state.release_user_lock(uid)

    def on_errors(self, errors):
        print(f"⚠️  Stream errors: {errors}")
        return True   # keep alive

    def on_connection_error(self):
        print("🔁 Connection dropped — reconnecting…")
        return True

    def on_disconnect(self):
        print("🔌 Stream disconnected")


# ══════════════════════════════════════════════════════════════════
#  STREAM RULE MANAGEMENT
# ══════════════════════════════════════════════════════════════════

def setup_stream_rules(stream: CampaignStream, post_id: str):
    """Delete stale rules, add fresh rule for this post."""
    existing = stream.get_rules()
    if existing.data:
        ids = [r.id for r in existing.data]
        stream.delete_rules(ids)
        print(f"🗑️  Cleared {len(ids)} old stream rule(s)")

    rule_value = (
        f"conversation_id:{post_id} is:reply"
        f" -from:{CAMPAIGN['our_username']}"   # ignore our own nudge replies
        f" -to:{CAMPAIGN['our_username']}"     # ignore replies directed at us (mention-only)
    )
    stream.add_rules(tweepy.StreamRule(rule_value))
    print(f"📡 Stream rule set: {rule_value}")


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    campaign_id = uuid.uuid4().hex[:8]
    state       = CampaignState(campaign_id)
    start_ts    = time.time()

    print("═" * 60)
    print(f"  🚀 Campaign: {CAMPAIGN['headline']}")
    print(f"  ID:          {campaign_id}")
    print(f"  Account:     @{CAMPAIGN['our_username']}")
    print(f"  Post:        {CAMPAIGN['post_id']}")
    print(f"  Keywords:    {CAMPAIGN['keywords']}")
    print(f"  Started:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 60)

    # Register in central file
    register_campaign(campaign_id, CAMPAIGN["headline"], CAMPAIGN["post_id"])

    # Resolve our own user ID — used to filter our nudge replies from the stream
    global OUR_USER_ID
    resp = client.get_user(username=CAMPAIGN["our_username"])
    OUR_USER_ID = str(resp.data.id)
    print(f"👤 Authenticated as @{CAMPAIGN['our_username']} ({OUR_USER_ID})")

    # Build stream
    stream = CampaignStream(
        bearer_token=BEARER_TOKEN,
        state=state,
        wait_on_rate_limit=True,
    )
    setup_stream_rules(stream, CAMPAIGN["post_id"])

    # ── graceful shutdown ────────────────────────────────────────
    def shutdown(sig, frame):
        print("\n\n🛑 Shutdown requested…")
        stream.disconnect()
        _finalize(state, start_ts, campaign_id, status="stopped")
        sys.exit(0)

    signal.signal(signal.SIGINT,  shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # ── go ──────────────────────────────────────────────────────
    print("\n▶️  Listening for replies… (Ctrl+C to stop)\n")
    try:
        stream.filter(
            tweet_fields=["author_id", "text", "conversation_id"],
            threaded=False,
        )
    except Exception as e:
        print(f"❌ Stream crashed: {e}")
    finally:
        _finalize(state, start_ts, campaign_id, status="completed")


def _finalize(state: CampaignState, start_ts: float, campaign_id: str, status: str):
    state.finalize(start_ts)
    summary = state.summary()

    elapsed = summary["total_seconds"]
    h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60

    print("\n" + "═" * 60)
    print(f"  📊 CAMPAIGN SUMMARY — {summary['headline']}")
    print("═" * 60)
    print(f"  Duration:       {h:02d}h {m:02d}m {s:02d}s")
    print(f"  Comments seen:  {summary['comments_seen']}")
    print(f"  Keyword hits:   {summary['keyword_hits']}")
    print(f"  DMs sent:       {summary['dms_sent']}")
    print(f"  Nudges sent:    {summary['nudges_sent']}")
    print(f"  Ignored users:  {len(summary['ignored_users'])}")
    print(f"  Est. cost:      ${summary['estimated_cost']:.3f}")
    print(f"  State saved →   state/campaign_{campaign_id}.json")
    print("═" * 60)

    update_campaign_status(campaign_id, status, summary)
    print(f"  Registry →      state/campaigns.json  [status: {status}]")
    print()


if __name__ == "__main__":
    main()