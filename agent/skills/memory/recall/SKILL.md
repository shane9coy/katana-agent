---
name: recall
description: >
  Search and retrieve memories. Triggered by /recall command, or when user asks
  "what did we work on", "do you remember", "what do you know about me",
  "what project were we doing". Searches soul.md, user.md, and work.md
  for matching content and returns relevant entries.
---

# Recall — Retrieve Memories

## When This Fires
- User types `/recall` with a query
- User asks: "what did we work on yesterday?"
- User asks: "what do you know about me?"
- User asks: "what's the status of project X?"
- User asks: "do you remember when we..."
- User references a past session or project

## How To Search

### Determine what the user is asking for

| Question type | Search where |
|--------------|-------------|
| "What do you know about me?" / "What are my preferences?" | `~/.katana/memory/user.md` — read and summarize relevant sections |
| "How should you behave?" / "What's your personality?" | `~/.katana/memory/soul.md` — read and summarize |
| "What did we work on?" / "Project status?" / "Yesterday?" | `~/.katana/memory/work.md` — search entries |
| Unclear or broad | Search all three files |

### Search work.md

work.md is organized with entries like:
```
## 2026-02-22 — katana-agent
Summary of work done...
```

**Filter by project:** Look for entries where the project tag matches the user's query.
Example: user asks about "redis" → find all `## YYYY-MM-DD — redis-cache` entries.

**Filter by date:** 
- "yesterday" → find entries with yesterday's date
- "last week" → find entries from the last 7 days
- "this month" → entries from current month
- Specific date: "February 15th" → match `2026-02-15`

**Filter by content:** If the user asks about a specific topic ("auth changes", "voice bug"), 
search the summary text for matching keywords.

Use the filesystem tools available to you:
- `cat ~/.katana/memory/work.md` to read the full file
- `grep -i "keyword" ~/.katana/memory/work.md` for keyword search
- Read and filter in context for date/project matching

### Return Results

Present matching memories naturally in conversation:

**Good:**
> "Yesterday you worked on the Katana memory system — designed the three-file 
> structure (soul.md, user.md, work.md) and defined the /remember and /recall 
> commands. The day before that, you fixed WebSocket streaming in MAGI3."

**Bad:**
> "Here are 47 search results from your memory files..."

Synthesize. Don't dump raw data. Speak like you actually remember it.

### Cross-file recall

Sometimes the user's question spans multiple files:
- "Give me a status update" → read user.md for goals + work.md for recent progress
- "Help me plan today" → read user.md for routines + work.md for what's in progress
- "What should I work on next?" → read work.md recent entries for "Next:" items

### If nothing found

If no matching memories exist, say so honestly:
> "I don't have any memories about that project yet. Want to tell me about it 
> so I can remember for next time?"
