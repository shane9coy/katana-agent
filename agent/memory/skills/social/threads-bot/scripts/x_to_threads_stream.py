#!/usr/bin/env python3
"""
x_stream_to_threads.py — Real-time X → Threads stream listener.

Opens a single persistent HTTP connection to X API v2 Filtered Stream.
X pushes your matching tweets through the pipe in real-time. No polling.
No repeated API calls. Zero idle cost.

Stream rule:
    from:YOUR_USERNAME -is:reply

What gets pushed through:
    ✓ Original posts
    ✓ Retweets
    ✓ Quote tweets
    ✗ Replies (blocked server-side by -is:reply)

At 3-4 posts/day, this costs essentially nothing — you're only charged
per tweet delivered, not for the open connection sitting idle.

Usage:
    python x_stream_to_threads.py
"""

import json
import logging
import os
import re
import signal
import sys
import tempfile
import time
import threading
from pathlib import Path

import requests
import tweepy
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("x-stream")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SYNCED_FILE = Path(__file__).parent / "synced_tweets.json"
RUNNING = True

# Fields we request on every streamed tweet
TWEET_FIELDS = [
    "created_at", "attachments", "entities", "referenced_tweets",
    "in_reply_to_user_id", "text", "author_id", "note_tweet",
]
EXPANSIONS = [
    "attachments.media_keys", "referenced_tweets.id",
    "referenced_tweets.id.author_id",
]
MEDIA_FIELDS = ["url", "preview_image_url", "type", "variants"]


def _signal_handler(sig, frame):
    global RUNNING
    logger.info("Signal %s received — shutting down...", sig)
    RUNNING = False


signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


# ===================================================================
#  Sync state — dedup tracker (persisted to disk)
# ===================================================================
class SyncState:
    def __init__(self, filepath: Path = SYNCED_FILE):
        self._filepath = filepath
        self._lock = threading.Lock()
        self._ids: set = self._load()

    def _load(self) -> set:
        if self._filepath.exists():
            try:
                return set(json.loads(self._filepath.read_text()))
            except (json.JSONDecodeError, TypeError):
                logger.warning("Corrupt synced file — starting fresh.")
        return set()

    def _save(self):
        self._filepath.write_text(json.dumps(sorted(self._ids), indent=2))

    def already_synced(self, tweet_id: str) -> bool:
        with self._lock:
            return tweet_id in self._ids

    def mark_synced(self, tweet_id: str):
        with self._lock:
            self._ids.add(tweet_id)
            self._save()

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._ids)


# ===================================================================
#  Tweet classification
# ===================================================================
class TweetType:
    ORIGINAL = "original"
    RETWEET = "retweet"
    QUOTE = "quote"
    REPLY = "reply"


def classify_tweet(data: dict) -> str:
    """Classify tweet type from its data."""
    if data.get("in_reply_to_user_id"):
        return TweetType.REPLY

    refs = data.get("referenced_tweets") or []
    ref_types = {r.get("type") for r in refs}

    if "replied_to" in ref_types:
        return TweetType.REPLY
    if "retweeted" in ref_types:
        return TweetType.RETWEET
    if "quoted" in ref_types:
        return TweetType.QUOTE

    return TweetType.ORIGINAL


def should_crosspost(data: dict) -> bool:
    """Original, retweet, quote → yes. Reply → no."""
    return classify_tweet(data) != TweetType.REPLY


# ===================================================================
#  Format tweet text for Threads
# ===================================================================
def format_for_threads(data: dict, includes: dict) -> str:
    """
    Build the Threads caption:
      Original  → tweet text as-is
      Retweet   → RT @author: <original text>
      Quote     → <your text>\n\n📎 @author: "<quoted text>"
    """
    tweet_type = classify_tweet(data)
    text = data.get("text", "")

    if tweet_type == TweetType.RETWEET:
        rt_text = _ref_text(data, includes, "retweeted")
        rt_author = _ref_author(data, includes, "retweeted")
        if rt_text:
            prefix = f"RT @{rt_author}: " if rt_author else "RT: "
            return prefix + _clean(rt_text)
        return _clean(text)

    if tweet_type == TweetType.QUOTE:
        commentary = _clean(text)
        q_text = _ref_text(data, includes, "quoted")
        q_author = _ref_author(data, includes, "quoted")
        if q_text:
            attr = f"@{q_author}" if q_author else "quoted"
            return f"{commentary}\n\n📎 {attr}: \"{_clean(q_text)}\""
        return commentary

    # Original — use note_tweet for long-form if available
    note = (data.get("note_tweet") or {}).get("text")
    if note:
        return _clean(note)
    return _clean(text)


def _ref_text(data: dict, includes: dict, ref_type: str) -> str | None:
    """Get the text of a referenced tweet from includes."""
    ref_id = _ref_id(data, ref_type)
    if not ref_id:
        return None
    for t in includes.get("tweets", []):
        if str(_get(t, "id")) == str(ref_id):
            return _get(t, "text")
    return None


def _ref_author(data: dict, includes: dict, ref_type: str) -> str | None:
    """Get the username of a referenced tweet's author from includes."""
    ref_id = _ref_id(data, ref_type)
    if not ref_id:
        return None
    author_id = None
    for t in includes.get("tweets", []):
        if str(_get(t, "id")) == str(ref_id):
            author_id = _get(t, "author_id")
            break
    if not author_id:
        return None
    for u in includes.get("users", []):
        if str(_get(u, "id")) == str(author_id):
            return _get(u, "username")
    return None


def _ref_id(data: dict, ref_type: str) -> str | None:
    for r in (data.get("referenced_tweets") or []):
        if r.get("type") == ref_type:
            return str(r.get("id"))
    return None


def _get(obj, key):
    """Get attr or dict key from either a dict or tweepy object."""
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def _clean(text: str) -> str:
    """Strip trailing t.co links (media URLs X appends)."""
    cleaned = re.sub(r"\s*https://t\.co/\w+$", "", text).strip()
    return cleaned if cleaned else text


# ===================================================================
#  Media download
# ===================================================================
def download_media(data: dict, includes: dict, tmp_dir: str) -> dict:
    """Download attached images/video. Returns {image_path, video_path}."""
    result = {"image_path": None, "video_path": None}

    media_map = {}
    for m in includes.get("media", []):
        key = _get(m, "media_key")
        if key:
            media_map[key] = m

    for key in (data.get("attachments") or {}).get("media_keys", []):
        media = media_map.get(key)
        if not media:
            continue

        mtype = _get(media, "type") or ""

        if mtype == "photo" and not result["image_path"]:
            url = _get(media, "url")
            if url:
                result["image_path"] = _dl(url, tmp_dir, f"{key}.jpg")

        elif mtype in ("video", "animated_gif") and not result["video_path"]:
            variants = _get(media, "variants") or []
            mp4s = [v for v in variants
                    if v.get("content_type") == "video/mp4" and v.get("bit_rate")]
            if mp4s:
                best = max(mp4s, key=lambda v: v.get("bit_rate", 0))
                result["video_path"] = _dl(best["url"], tmp_dir, f"{key}.mp4")
            elif variants:
                result["video_path"] = _dl(variants[0].get("url", ""), tmp_dir, f"{key}.mp4")

    return result


def _dl(url: str, directory: str, filename: str) -> str | None:
    if not url:
        return None
    try:
        r = requests.get(url, timeout=60, stream=True)
        r.raise_for_status()
        fp = os.path.join(directory, filename)
        with open(fp, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        logger.info("    ↓ %s (%d KB)", filename, os.path.getsize(fp) // 1024)
        return fp
    except Exception as e:
        logger.warning("    ✗ Download failed: %s", e)
        return None


# ===================================================================
#  Threads poster
# ===================================================================
class ThreadsPoster:
    def __init__(self):
        from metathreads import MetaThreads, config

        ph = os.getenv("THREADS_PROXY_HTTP")
        ps = os.getenv("THREADS_PROXY_HTTPS")
        if ph or ps:
            config.PROXY = {}
            if ph: config.PROXY["http"] = ph
            if ps: config.PROXY["https"] = ps
        t = os.getenv("THREADS_TIMEOUT")
        if t:
            config.TIMEOUT = int(t)

        self._user = os.getenv("THREADS_USERNAME")
        self._pass = os.getenv("THREADS_PASSWORD")
        if not self._user or not self._pass:
            raise ValueError("THREADS_USERNAME and THREADS_PASSWORD required")

        self._client = MetaThreads()
        self._login()

    def _login(self):
        logger.info("Logging in to Threads as '%s'...", self._user)
        self._client.login(self._user, self._pass)
        logger.info("Threads OK — %s", self._client.me.get("username", "?"))

    def post(self, caption: str, image_path: str = None, video_path: str = None):
        kw = {"thread_caption": caption}
        if image_path: kw["image_path"] = image_path
        if video_path: kw["video_path"] = video_path
        try:
            return self._client.post_thread(**kw)
        except Exception as e:
            if any(s in str(e).lower() for s in ("login", "auth", "session", "401", "403")):
                logger.warning("Threads session expired — re-auth...")
                self._login()
                return self._client.post_thread(**kw)
            raise


# ===================================================================
#  Stream rule setup
# ===================================================================
def setup_stream_rule(client: tweepy.Client, username: str):
    """
    Set one rule: from:USERNAME -is:reply
    Deletes any stale x-to-threads rules first.
    """
    rule_value = f"from:{username} -is:reply"
    tag = "x-to-threads"

    existing = client.get_rules()
    rules = existing.data or []

    # Already set?
    for r in rules:
        if r.value == rule_value:
            logger.info("Stream rule already active: '%s'", rule_value)
            return

    # Clean old rules with our tag
    old = [r.id for r in rules if r.tag and "x-to-threads" in r.tag]
    if old:
        logger.info("Removing %d stale rule(s)...", len(old))
        client.delete_rules(old)

    # Add the rule
    logger.info("Adding stream rule: '%s'", rule_value)
    res = client.add_rules(tweepy.StreamRule(value=rule_value, tag=tag))
    if res.errors:
        logger.error("Rule add failed: %s", res.errors)
        sys.exit(1)
    logger.info("Rule active.")


# ===================================================================
#  Stream listener — the core of the whole thing
# ===================================================================
class StreamListener(tweepy.StreamingClient):
    """
    Persistent connection to GET /2/tweets/search/stream.

    X keeps this HTTP connection open. When a tweet matches our rule,
    X pushes it through the pipe. We process it and post to Threads.

    No polling. No repeated API calls. The connection just sits idle
    between your posts — zero cost while idle.
    """

    def __init__(self, bearer_token: str, threads: ThreadsPoster,
                 state: SyncState, **kwargs):
        super().__init__(bearer_token, **kwargs)
        self._threads = threads
        self._state = state

    def on_response(self, response: tweepy.StreamResponse):
        tweet = response.data
        if not tweet:
            return

        tweet_id = str(tweet.id)
        logger.info("⚡ Received tweet %s", tweet_id)

        if self._state.already_synced(tweet_id):
            logger.info("  Already synced — skipping.")
            return

        # Normalize to dicts for our processing functions
        data = self._to_dict(tweet)
        includes = self._normalize_includes(response.includes or {})

        # Double-check: skip replies (safety net beyond server rule)
        if not should_crosspost(data):
            logger.info("  Reply detected client-side — skipping.")
            return

        tweet_type = classify_tweet(data)
        caption = format_for_threads(data, includes)
        logger.info("  [%s] %s", tweet_type.upper(), caption[:120])

        # Download media + post to Threads
        with tempfile.TemporaryDirectory(prefix="x2t_") as tmp:
            media = download_media(data, includes, tmp)
            try:
                self._threads.post(
                    caption=caption,
                    image_path=media.get("image_path"),
                    video_path=media.get("video_path"),
                )
                logger.info("  ✓ Posted to Threads!")
                self._state.mark_synced(tweet_id)
            except Exception as e:
                logger.error("  ✗ Threads post failed: %s", e)

    def on_errors(self, errors):
        logger.error("Stream errors: %s", errors)

    def on_connection_error(self):
        logger.warning("Connection error — Tweepy auto-reconnects with backoff.")

    def on_disconnect(self):
        logger.warning("Stream disconnected by X.")

    def on_closed(self, response):
        logger.warning("Stream closed (HTTP %s).", response.status_code if response else "?")

    # --- helpers to normalize tweepy objects into plain dicts ---

    @staticmethod
    def _to_dict(tweet) -> dict:
        d = {
            "id": str(tweet.id),
            "text": tweet.text,
            "author_id": str(tweet.author_id) if tweet.author_id else None,
            "attachments": tweet.attachments,
            "in_reply_to_user_id": tweet.in_reply_to_user_id,
            "note_tweet": getattr(tweet, "note_tweet", None),
            "referenced_tweets": None,
        }
        if tweet.referenced_tweets:
            d["referenced_tweets"] = [
                {"type": getattr(r, "type", None) or r.get("type"),
                 "id": str(getattr(r, "id", None) or r.get("id"))}
                for r in tweet.referenced_tweets
            ]
        return d

    @staticmethod
    def _normalize_includes(raw: dict) -> dict:
        out = {"tweets": [], "users": [], "media": []}
        for t in raw.get("tweets", []):
            out["tweets"].append({
                "id": str(t.id), "text": t.text,
                "author_id": str(t.author_id) if t.author_id else None,
            })
        for u in raw.get("users", []):
            out["users"].append({"id": str(u.id), "username": u.username})
        for m in raw.get("media", []):
            out["media"].append({
                "media_key": m.media_key, "type": m.type,
                "url": getattr(m, "url", None),
                "variants": getattr(m, "variants", None),
            })
        return out


# ===================================================================
#  Main
# ===================================================================
def main():
    load_dotenv()

    bearer = os.getenv("X_BEARER_TOKEN")
    username = os.getenv("X_USERNAME")
    if not bearer:
        logger.error("X_BEARER_TOKEN required in .env"); sys.exit(1)
    if not username:
        logger.error("X_USERNAME required in .env (your handle, no @)"); sys.exit(1)

    # Authenticate + set stream rule
    client = tweepy.Client(bearer_token=bearer, wait_on_rate_limit=True)
    setup_stream_rule(client, username)

    # Init state + Threads
    state = SyncState()
    logger.info("Loaded %d previously synced tweets.", state.count)
    threads = ThreadsPoster()

    # Open the stream
    logger.info("=" * 60)
    logger.info("STREAM LISTENER ACTIVE")
    logger.info("  Rule: from:%s -is:reply", username)
    logger.info("  Copies: originals ✓ | retweets ✓ | quotes ✓ | replies ✗")
    logger.info("  Cost: $0 while idle — only charged per tweet delivered")
    logger.info("  Ctrl+C to stop")
    logger.info("=" * 60)

    stream = StreamListener(
        bearer_token=bearer,
        threads=threads,
        state=state,
        wait_on_rate_limit=True,
    )

    # .filter() blocks — it holds the HTTP connection open.
    # Tweepy handles reconnection + backoff automatically.
    try:
        stream.filter(
            tweet_fields=",".join(TWEET_FIELDS),
            expansions=",".join(EXPANSIONS),
            media_fields=",".join(MEDIA_FIELDS),
        )
    except KeyboardInterrupt:
        pass
    finally:
        stream.disconnect()
        logger.info("Stream closed. Synced %d total tweets.", state.count)


if __name__ == "__main__":
    main()
