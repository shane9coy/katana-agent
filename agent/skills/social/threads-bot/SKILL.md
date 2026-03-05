---
name: x-to-threads
description: >
  Cross-post content from X (Twitter) to Meta Threads via real-time stream listener.
  Uses X API v2 Filtered Stream — a persistent connection where X pushes your tweets
  to you in real-time. No polling. Zero idle cost. Copies originals, retweets, and
  quote tweets. Never copies replies.
---

# X-to-Threads Stream Listener

## How It Works

One persistent HTTP connection to X's Filtered Stream API. X pushes your matching
tweets through the pipe in real-time. No polling. No repeated API calls.

```
You post on X
      │
      ▼
X pushes tweet through open stream connection
      │
      ▼
Listener receives it instantly
      │
      ├─ Original post → posts text + media to Threads
      ├─ Retweet       → posts "RT @author: text" to Threads
      ├─ Quote tweet   → posts "your text 📎 @author: quoted" to Threads
      └─ Reply         → ignored (blocked server-side by rule)
```

## Stream Rule

```
from:YOUR_USERNAME -is:reply
```

Set once via `POST /2/tweets/search/stream/rules`. The connection sits idle
between your posts at zero cost — you're only charged per tweet delivered.

## Cost

X API is pay-per-use. At 3-4 posts/day, the stream costs essentially nothing.
The persistent connection itself is free — you only pay when a tweet actually
flows through. No idle polling burn.

## What Gets Copied

| Type          | Copied? | Threads Format |
|---------------|---------|----------------|
| Original post | ✓       | Text + media as-is |
| Retweet       | ✓       | `RT @author: <text>` |
| Quote tweet   | ✓       | `<your text>\n\n📎 @author: "<quoted>"` |
| Reply         | ✗       | Never (blocked by `-is:reply` rule) |

## Files

```
x-to-threads-agent/
├── skill/SKILL.md              # This file
├── x_stream_to_threads.py      # The stream listener
├── post_to_threads.py          # One-shot CLI poster
├── synced_tweets.json          # Auto-created dedup state
├── .env.example                # Credential template
└── requirements.txt
```

## X API v2 Endpoints

| Endpoint | Purpose | When called |
|---|---|---|
| `POST /2/tweets/search/stream/rules` | Set filter rule | Once at startup |
| `GET /2/tweets/search/stream` | Persistent stream | Held open continuously |

## Reconnection

Tweepy handles reconnection with automatic exponential backoff. If X drops the
connection (maintenance, network blip), it reconnects automatically. The
`backfill_minutes` parameter can recover up to 5 minutes of missed tweets on
reconnect.

## Running in Production

```bash
# Foreground
python x_stream_to_threads.py

# Background with nohup
nohup python x_stream_to_threads.py > stream.log 2>&1 &

# With screen
screen -S x2threads python x_stream_to_threads.py

# With systemd (recommended for always-on)

# X-to-Threads Stream Listener

Real-time mirror of your X posts to Meta Threads. Uses X API v2 Filtered Stream — a persistent connection where X pushes your tweets to you instantly. No polling. Zero idle cost.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in X_BEARER_TOKEN, X_USERNAME, THREADS_USERNAME, THREADS_PASSWORD
```

## Run

```bash
python x_stream_to_threads.py
```

That's it. The listener opens a persistent connection, sets the rule `from:YOUR_USERNAME -is:reply`, and waits. When you post on X, the tweet arrives instantly and gets cross-posted to Threads with media.

## What Gets Copied

- ✓ **Original posts** — text + images/video
- ✓ **Retweets** — formatted as `RT @author: text`
- ✓ **Quote tweets** — your commentary + quoted text
- ✗ **Replies** — never copied

## One-Shot Posting

```bash
python post_to_threads.py "Hello Threads!" --image photo.jpg
```

## Cost

X API is pay-per-use. The open stream connection costs nothing while idle. You only pay per tweet delivered through the stream. At 3-4 posts/day, cost is negligible.

```
