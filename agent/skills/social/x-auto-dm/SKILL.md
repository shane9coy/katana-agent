---
name: x-auto-dm
description: "Monitor X/Twitter post replies for keyword triggers and auto-DM followers with gated content. Use when setting up lead-gen campaigns, gated PDF/repo distribution, or automated DM funnels on X. Handles reply polling, follower verification, DM delivery, follow-nudge replies, unsuccessful_first_dm retry list, ignore list, and per-action cost tracking."
---

# X Auto-DM Campaign Bot (v2)

## Overview

Monitors replies on a specific X post for keyword triggers (`skill`, `skills`, `agent skills`), verifies the commenter follows you, and sends a DM with your gated content. Non-followers get a public reply nudge and land on `unsuccessful_first_dm`. If DM fails a 2nd time, the user is added to `ignore_list` permanently for that campaign.

## Folder Structure

```
x-auto-dm/
├── SKILL.md
├── scripts/
│   ├── x_auto_dm.py              # Main bot (classes + CLI)
│   └── x_auto_dm_config.json     # Campaign config (edit this, not Python)
│       └── data/                  # Auto-created at runtime
│           ├── processed_users.json
│           ├── unsuccessful_first_dm.json
│           ├── ignored_users.json
│           ├── processed_comments.json
│           ├── cursors.json
│           └── cost_stats.json
│       └── logs/
│           └── x_auto_dm.log
└── references/
    └── x-api-costs.md
```

## Prerequisites

### .env Variables

```
X_CONSUMER_KEY=your_consumer_key
X_CONSUMER_KEY_SECRET=your_consumer_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### Packages

```bash
pip install tweepy python-dotenv
```

### X App Permissions

Read + Write + Direct Messages in the X Developer Portal.

## Configuration

Edit `scripts/x_auto_dm_config.json` — never touch the Python file:

```json
{
  "post_id": "1234567890123456789",
  "my_user_id": "9876543210",
  "campaign_name": "agent_skills_guide",
  "keywords": ["agent skills", "skills", "skill"],
  "dm_message": "Hey! Here's the guide...",
  "follow_nudge": "@{username} Follow me to get the DM...",
  "polling_interval_seconds": 600,
  "pending_retry_delay_minutes": 60,
  "max_results_per_poll": 1000
}
```

To run a **second campaign**, copy the config, change `campaign_name` and `post_id`, run a second instance. All data files are campaign-namespaced.

## CLI Commands

```bash
python x_auto_dm.py run            # continuous monitoring
python x_auto_dm.py run --once     # single poll cycle (testing)
python x_auto_dm.py verify         # test X API auth
python x_auto_dm.py status         # show campaign stats
python x_auto_dm.py clear          # reset campaign data
```

## Campaign Flow

```
Poll replies on post_id (every polling_interval_seconds)
│
For each reply containing keyword:
│
├── Already in processed_users? ───────────→ SKIP
├── Already in ignore_list? ───────────────→ SKIP
│
├── CALL 1: Search replies ($0.005)
├── CALL 2: Check if user follows me ($0.005)
│   │
│   ├── FOLLOWS → CALL 3: Send DM ($0.015)
│   │             ├── Success → processed_users ✓
│   │             └── Fail    → unsuccessful_first_dm
│   │
│   └── DOESN'T FOLLOW
│       ├── On unsuccessful_first_dm?
│       │   ├── YES → CALL 3: Try DM ($0.015)
│       │   │         ├── Success → processed_users ✓
│       │   │         └── Fail    → ignore_list ✗ (DONE)
│       │   │
│       │   └── NO → Reply nudge ($0.005)
│       │           Add to unsuccessful_first_dm
│
Separate timer (pending_retry_delay_minutes):
│
└── Re-check unsuccessful_first_dm users
    ├── Now following? → Send DM
    └── Still not? → Wait for next retry cycle
```

## Cost Per User

| Scenario | Calls | Cost |
|----------|-------|------|
| Follower + DM works | search + follow + DM | $0.025 |
| Non-follower → nudge | search + follow + reply | $0.015 |
| Retry → DM works | search + follow + DM | $0.025 |
| Retry → DM fails (ignored) | search + follow + DM | $0.025 |
| Already processed/ignored | search only | $0.005 |

## Architecture Notes

- **XClient class** wraps all API calls with automatic cost tracking
- **CampaignMonitor class** handles campaign logic, signal handling, retry timer
- **since_id pagination** — only fetches new replies each cycle (cheaper)
- **Signal handling** — catches SIGINT/SIGTERM, 1-second sleep granularity for fast exit
- **Separate retry timer** — pending users checked on their own schedule to avoid wasting follower-check calls
- **All state is campaign-namespaced** — multiple campaigns share the same data files safely
