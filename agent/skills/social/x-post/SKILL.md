---
name: x-thread
triggers: "tweet, twitter, x thread, post to x, post to twitter, twitter thread, social post, draft tweet, write thread, x/twitter"
description: "Draft and post single tweets or multi-tweet threads to X/Twitter — always user-approved before posting. Uses post_to_x.py."
---

# X Thread Skill

Auto-activate when the user wants to draft tweets, write threads, or post to X/Twitter.

## Quick Commands

```
/x-thread "Tweet 1\n\nTweet 2\n\nTweet 3"
/x-thread --dry-run "Preview without posting"
/x-thread --date 2026-02-03 "Thread content"
```

## Key Rules

- **Always show the thread to the user for approval before posting**
- Stock symbols always use `$` prefix: `$TSLA`, `$NVDA`, `$AMD`
- Tweets split by `\n\n` — each chunk = one tweet
- 1.5s delay between tweets (rate limit safety)
- Returns final tweet URL on success

## Implementation

- Script: `.claude/skills/x-thread/scripts/post_to_x` (post to <YOUR> X account)
- Function: `post_to_x(tweets: list[str])`
- `--dry-run` previews without API call

## Writing Style

World-class literary quality. Financial/tech content: data-driven with narrative. Hook first, insight throughout, strong close. Threads should tell a story, not just list facts.

→ Full docs: `.claude/commands/x-thread.md`
