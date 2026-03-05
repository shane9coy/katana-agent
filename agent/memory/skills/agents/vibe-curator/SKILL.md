---
name: vibe-curator
triggers: "vibe, what to wear, outfit, food recommendation, music recommendation, what to do today, activity, local events, book a table, order food, tickets, restaurant, playlist, things to do, daily recommendation"
description: "Personalized daily recs + action engine — music, food, clothing, events, reservations, orders — blending weather, astrology, and user preferences."
---

# Vibe Curator Skill

Auto-activate when the user wants daily recommendations, asks what to wear/eat/listen to, or wants to book/order/find events.

## Quick Commands

| What | Command |
|------|---------|
| Full daily vibe | `/vibe today` |
| Food recs | `/vibe food` |
| Music | `/vibe music` |
| Outfit | `/vibe outfit` |
| Activities | `/vibe activity` |
| Local events | `/vibe events` |
| Book restaurant | `/vibe book <name> [date] [time] [party size]` |
| Order delivery | `/vibe order <food>` |
| Check tickets | `/vibe tickets <event>` |
| Buy product | `/vibe buy <item>` |
| Price compare | `/vibe price-check <item>` |
| Quick vibe | `/vibe quick` |

## Architecture

**Phase 1 (always):** Weather + Profile + Oracle → recommendations (no browser)  
**Phase 2 (on confirm):** Action Router → Playwright for transactional tasks

Transact actions (order/book/buy) **always stop for explicit confirmation** before submitting.

## Data Sources

- Weather: Open-Meteo (free, no key) — WMO codes route indoor/outdoor
- Preferences: `.claude/user_profile.json` (music_types, cuisines, activities, places)
- Astrology: natal_mcp transit + moon phase
- Location default: Sandusky, OH (41.4489, -82.708)

## Telegram Queue

Playwright tasks from Telegram → `/tmp/telegram_agent_queue.json`  
Process with: `python agent_orchestrator.py --task process-queue`

Disable Playwright: `export VIBE_PLAYWRIGHT_ENABLED=false`

→ Full docs + ActionRouter: `.claude/commands/vibe-curator.md`
