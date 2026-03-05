---
name: reddit-bot
triggers: "reddit, subreddit, reddit comment, reddit marketing, reddit analytics, reddit post, reddit engagement, reddit bot, comment performance, carpet bomb, sniper strategy"
description: "Reddit marketing automation — comment engagement, subreddit discovery, Supabase analytics, and performance tracking."
---

# Reddit Bot Skill

Auto-activate for Reddit marketing tasks, analytics checks, or subreddit discovery.

## Quick Operations

| What | Command |
|------|---------|
| Status overview | "Check Reddit bot status" |
| Active targets | Query `targets` table (is_active=true) |
| Run analytics | "Pull Reddit analytics from Supabase" |
| Discover subs | "Find trending subreddits for our niche" |
| Run manual mode | `python reddit_bot.py` → manual mode |
| Run agent mode | `python reddit_bot.py` → agent mode |
| Run dynamic mode | `python reddit_bot.py` → dynamic mode |
| Check performance | `check_comment_performance(days_back=7)` |

## Supabase Tables

| Table | Purpose |
|-------|---------|
| `targets` | Subreddits + threads to monitor |
| `comments` | Every comment posted (dedup: submission_id) |
| `comment_performance` | Time-series engagement snapshots |

## Analytics Views

`v_latest_performance` | `v_subreddit_performance` | `v_strategy_performance` | `v_keyword_performance`

## Key Metrics

- `engagement_ratio` = comment_score / thread_num_comments
- `controversy_engagement` = engagement_ratio × (1 + controversiality)
- Watch for `comment_is_visible = false` — adjust approach

## Strategy Modes

- **Manual:** Keyword-match scan on curated subreddits
- **Agent:** Discovery + sniper on rising/hot posts
- **Dynamic:** Deduplicated union of both (no double-posting)

→ Full docs: `.claude/commands/reddit-bot.md`
