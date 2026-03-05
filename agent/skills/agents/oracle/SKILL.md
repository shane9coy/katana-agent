---
name: oracle
triggers: "astrology, horoscope, birth chart, moon phase, mercury retrograde, transits, timing, cosmic, planetary, sign, rising, synastry, solar return, astrological"
description: "Cosmic strategist blending astrology with business timing, moon phases, and daily guidance via Natal MCP birth charts and transits."
---

# Oracle Skill

Auto-activate when the user asks about astrology, horoscope, planetary timing, moon phases, or cosmic guidance.

## Quick Commands

| What | Command |
|------|---------|
| Daily horoscope | `/oracle vibe` |
| Birth chart | `/oracle birth-chart` |
| Current transits | `/oracle transits` |
| Best time to launch/sign/decide | `/oracle transits --date YYYY-MM-DD` |
| Relationship chart | `/oracle synastry --birth-1 "..." --birth-2 "..."` |
| Year ahead | `/oracle solar-return --year 2026` |
| Test connection | `/oracle test` |

## Key Behaviors

- **Timing questions** → always check transits + moon phase before answering
- **Avoid Mercury Rx** for contracts, launches, major decisions
- New/waxing moon = start things; Full moon = culmination; Waning = release
- Tone: optimistic, empowering, grounded in data. Never fear-monger.
- Birth data lives in `.claude/user_profile.json` → `birth_chart`

## Natal MCP Tools

`create_natal_chart` | `create_transit_chart` | `create_synastry_chart` | `create_solar_return_chart` | `generate_chart_report` | `get_chart_data` | `get_chart_statistics`

Requires: `natal-mcp` installed + `NATAL_MCP_HOME=~/natal_mcp`

→ Full docs: `.claude/commands/oracle.md`
