---
name: rent
triggers: "hire a human, rent a human, delegate to human, find a freelancer, post a bounty, hire someone, human assistant, errands, rentahuman, bounty"
description: "Delegate tasks to real humans via RentAHuman.ai — search skills, post bounties, manage conversations, and run AI-scored opportunity scans."
---

# Rent-A-Human Skill

Auto-activate when the user wants to hire a person, post a job, or delegate a task that needs a human.

## Quick Commands

```
/rent              — Browse + print command menu
/rent scan         — AI-scored bounties (Grok, 12hr cache)
/rent scan force   — Bypass cache, fresh scoring now
/rent scan new     — Only unseen bounties
/rent post <desc>  — Post a new bounty (first sentence = title)
/rent saved        — View saved bounties
/rent skills       — List available human skills
/rent status       — Connection check
```

## Hire Flow

**Direct:** `/rent search <skill>` → `/rent human <id>` → `/rent talk <id> : msg` → negotiate → book  
**Bounty:** `/rent post desc` → humans apply → `/rent applications <id>` → `/rent accept <app_id>`

## Bounty Scanner

Script: `python3 "$HOME/bounty_hunter.py"`  
Cache: `logs/bounties_cache.json` (12hr TTL, Grok-3-mini-fast scoring 0–100)  
After running: read cache file and display scored results to user.

## Rate Limits

Bounties: 5/day | Conversations: 50/day | Messages: 30/hr | API keys: 3 max

## CLI Alternative

```bash
python hire_team.py "Task description"
python hire_team.py talk <human_id> "Message"
python hire_team.py bounty "Title" --description "..." --price 100 --hours 2
```

Payment via Stripe Connect escrow on RentAHuman.ai.

→ Full command tree + MCP tool map: `.claude/commands/rent.md`
