---
name: stream
description: "RSS news feed monitoring and market intelligence. Use when user says /stream, 'check my news', 'market update', 'headlines', or 'morning briefing'. Fetches and summarizes financial news, X influencer feeds, and government press releases."
tags: [news, rss, markets, finance, briefing]
created: 2026-03-04
---

# Stream — News & Market Intelligence Skill

## What This Does

Fetches and summarizes news from configured RSS feeds, financial sources, X/Twitter influencers, and government press releases. Outputs a categorized, concise briefing.

## Feed Configuration

Feeds are stored in `~/katana-agent/agent/skills/productivity/stream/feeds.json`. The agent reads this file, curls each URL, parses the response, and summarizes.

## How to Fetch

### JSON Feeds (rss.app)
```bash
curl -s "https://rss.app/feeds/v1.1/FEED_ID.json"
```
Extract: `items[].title`, `items[].content_text`, `items[].date_published`, `items[].url`

### XML Feeds (standard RSS)
```bash
curl -s "https://feeds.content.dowjones.io/public/rss/mw_bulletins"
```
Extract from `<item>`: `<title>`, `<description>`, `<pubDate>`, `<link>`

### Federal Reserve (Atom XML)
```bash
curl -s "https://www.federalreserve.gov/feeds/press_all.xml"
```
Parse `<entry>`: `<title>`, `<link>`, `<updated>`

## Processing Rules

1. Fetch all feeds from `feeds.json`
2. Filter to last 24 hours
3. Deduplicate — keep original source
4. Categorize by `category` field in feeds.json
5. Summarize each item in 1-2 sentences
6. Rank by importance within each category
7. Flag urgent items at the top

## Integration

### Morning Routine (/katana)
The `/katana` master agent calls `/stream` during morning check-in. Include top 3-5 headlines. Check `user.md` for tracked topics.

### Memory
After each pull, optionally log to `~/katana-agent/agent/memory/work.md`:
```
## 2026-03-04 — Stream
Checked 13 feeds, 18 new items. Key: Fed held rates, NVDA beat, EU AI regulation proposed.
```

### Feed Management
- "Add a feed" → ask for URL, name, category → append to feeds.json
- "Remove [name]" → remove from feeds.json
- "List feeds" → display all sources

## Files
- `SKILL.md` — this file
- `feeds.json` — feed URL configuration
