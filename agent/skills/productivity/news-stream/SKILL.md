---
name: stream
version: 1.0.0
category: productivity
triggers:
  - /stream
  - check my news
  - what's happening
  - market update
  - any news
  - morning briefing
  - headlines
  - market pulse
  - my stream
  - my news
tags: [news, rss, markets, finance, briefing]
created: 2026-03-04
---

# Stream — News & Market Intelligence Skill

## What This Does

Fetches and summarizes news from configured RSS feeds, financial sources, X/Twitter influencers, and government press releases. Outputs a categorized, concise briefing.

## Feed Configuration

Feeds are stored in `~/.katana/memory/skills/productivity/news-stream/feeds.json`. This file contains all RSS/JSON feed URLs organized by category. The agent reads this file, curls each URL, parses the response, and summarizes.

## How to Fetch Feeds

### JSON Feeds (rss.app format)

```bash
curl -s "https://rss.app/feeds/v1.1/FEED_ID.json"
```

Response structure:
```json
{
  "items": [
    {
      "title": "Headline",
      "url": "https://...",
      "date_published": "2026-03-04T12:00:00Z",
      "content_text": "Article summary or full text"
    }
  ]
}
```

Extract: `items[].title`, `items[].content_text`, `items[].date_published`, `items[].url`

### XML Feeds (standard RSS)

```bash
curl -s "https://feeds.content.dowjones.io/public/rss/mw_bulletins"
```

Response structure:
```xml
<rss>
  <channel>
    <item>
      <title>Headline</title>
      <link>https://...</link>
      <pubDate>Mon, 04 Mar 2026 12:00:00 GMT</pubDate>
      <description>Summary text</description>
    </item>
  </channel>
</rss>
```

Extract from each `<item>`: `<title>`, `<description>`, `<pubDate>`, `<link>`

### HTML Feeds (Federal Reserve)

```bash
curl -s "https://www.federalreserve.gov/feeds/press_all.xml"
```

This is actually XML/Atom. Parse `<entry>` elements for `<title>`, `<link>`, `<updated>`.

## Processing Rules

1. **Fetch all feeds** from `feeds.json`
2. **Filter to last 24 hours** (or since the timestamp in the last stream check)
3. **Deduplicate** — if multiple feeds have the same story, keep the original source
4. **Categorize** based on the `category` field in feeds.json:
   - `markets` → 📊 Markets section
   - `ai-tech` → 🤖 AI & Tech section
   - `economy` → 💰 Economy section
   - `government` → 🏛️ Fed & Government section
   - `x-feed` → 🐦 X Chatter section
5. **Summarize** each item in 1-2 sentences. Strip HTML tags, marketing fluff, and repetitive disclaimers.
6. **Rank** by importance within each category. Market-moving events first.
7. **Flag urgent items** at the top if any are time-sensitive or market-moving.

## Integration

### Morning Routine (Sensei)
When Sensei runs the morning check-in, it should call `/stream` and include the top 3-5 headlines in the briefing. Check `~/.katana/memory/core/user.md` for the user's interests, active investments, or tracked topics — prioritize news that matches.

### Memory
After each stream pull, optionally log a one-line summary to `~/.katana/memory/work.md`:
```
## 2026-03-04 — Stream
Checked 15 feeds, 23 new items. Key: Fed held rates, NVDA earnings beat, new AI regulation proposed in EU.
```

### Feed Management Commands
- **"Add a feed"** → Ask for URL, name, category. Append to feeds.json.
- **"Remove [name]"** → Remove matching entry from feeds.json.
- **"List feeds"** → Display all configured sources with categories.
- **"Only show [category]"** → Filter output to one section.

## Files

- `feeds.json` — Feed URL configuration (edit this to add/remove sources)
- `SKILL.md` — This file (agent instructions)
