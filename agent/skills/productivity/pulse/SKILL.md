---
name: pulse
triggers: "newsletter, news update, ranked news, publish newsletter, send newsletter, post to twitter, social media pipeline, RSS feeds, subscriber count, pulse status"
description: "Newsletter pipeline — pull RSS/X feeds, rank with Grok, generate, send, and post to social media. Backed by Supabase subscribers."
---

# Pulse Skill

Auto-activate for newsletter tasks, news feed updates, social posting, or pipeline status checks.

## Quick Commands

| What | Command |
|------|---------|
| Pipeline status | `/pulse status` |
| Pull + rank news | `/pulse news update` |
| Read today's ranked news | `/pulse read ranked` |
| Read X summaries | `/pulse read x` |
| Generate newsletter | `/pulse gen nl` |
| Full pipeline (rank+gen) | `/pulse run nl pipeline` |
| Send newsletter | `/pulse send nl` |
| Post to X only | `/pulse post-x` |
| Full end-to-end | `/pulse full` |
| Analyze themes | `/pulse analyze` |

## Pipeline Flow

```
news update → gen nl → send nl → gen content → post-x
/pulse full  (runs full_pipeline_orchestrator.py end-to-end)
```

## Implementation

- **Working dir:** `/Users/sc/News Letter`
- **CLI:** `python agent_orchestrator.py --task <task> [--date YYYY-MM-DD] [--dry-run]`
- **Ranked news:** `news_letter/ranked_news/ranked_news_{date}.json`
- **X summaries:** `news_letter/x_summaries/x_summaries_{date}.json`
- **Ranking API:** Grok (xAI) via `XAI_API_KEY`

## Telegram Bot Commands (@KatanaAgent_bot)

`/pulse` status | `/pulse news` top 5 headlines | `/pulse newsletter` send to you via TG | `/pulse newsletter gen` generate | `/pulse send` send to subscribers | `/pulse stats` subscriber count

→ Full docs: `.claude/commands/pulse.md`
