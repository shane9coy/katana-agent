---
name: playwright
triggers: "automate browser, web automation, book reservation, scrape website, fill form, automated purchase, opentable, doordash, amazon cart, flight search, price comparison, browser automation, playwright"
description: "Browser automation via Playwright MCP — reservations, ordering, scraping, form filling. Always confirm before final submission."
---

# Playwright Skill

Auto-activate when browser automation is needed for bookings, ordering, scraping, or form filling.  
**Also used internally by Vibe Curator** — prefer `/vibe book` or `/vibe order` for those flows.

## Safety Rules (Non-Negotiable)

- **Stop before final submit** on ANY transaction — show screenshot, ask confirmation
- Human-like delays (1–2s between actions) to avoid bot detection
- If CAPTCHA appears: stop, screenshot, wait for manual solve
- Ticketmaster: reconnaissance only — never attempt queue bypass

## Common Task Templates

| Task | Use Template |
|------|-------------|
| Restaurant reservation | Template 1: OpenTable |
| Food delivery | Template 2: DoorDash |
| Amazon shopping | Template 3: Amazon |
| Flight search | Template 4: Expedia (search only) |
| Ticket availability | Template 5: Ticketmaster (recon only) |
| Web scraping | Template 6 |
| Form filling | Template 7 |
| Price comparison | Template 8 |

## Protocol (every task)

1. Navigate → screenshot to confirm load
2. Check login status before proceeding
3. Execute task steps with delays
4. Screenshot key states
5. **Pause before submit** — show user, await "confirm"

## Troubleshooting

- No Playwright tools? Check Node.js 18+ installed, run `npx playwright install chromium`, restart Claude
- Sessions not persisting? Verify storage state file + permissions

→ Full templates + examples: `.claude/commands/playwright.md`
