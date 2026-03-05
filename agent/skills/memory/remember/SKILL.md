---
name: remember
description: >
  Store a memory from the current session. Triggered by /remember command, 
  "remember this", "save that", or automatically on session end in auto mode.
  Summarizes what happened, detects project context, and appends to the 
  correct memory file (soul.md, user.md, or work.md).
---

# Remember — Store Memory

## When This Fires
- User types `/remember`
- User says "remember this", "save that", "note that down"
- Auto mode: agent detects a natural breakpoint (topic switch, milestone, wrap-up)

## What To Do

### Step 1: Determine what type of memory this is

Read the conversation and classify:

| If the conversation contains... | Write to... |
|--------------------------------|-------------|
| User preference about how the agent should behave ("be more direct", "stop asking if I want to proceed") | `~/.katana/memory/soul.md` → Learned Behaviors section |
| What user is currently working on, struggling with, goals, life events, mood, accomplishments | `~/.katana/memory/user.md` → appropriate section (Current Focus, Recent Context, Wins, etc.) |
| Work done on a project, code changes, architecture decisions, tasks completed | `~/.katana/memory/work.md` → new entry at top |

If the session contains multiple types, write to multiple files.

### Step 2: Summarize

- Strip all raw code blocks longer than 5 lines
- Strip tool call outputs and error logs
- Strip repetitive back-and-forth troubleshooting
- Keep: decisions made, problems solved, features built, user preferences stated
- Condense to 1-3 sentences for work.md entries
- For user.md and soul.md: extract the specific context, pattern, or preference (not a session summary)

### Step 3: Detect project context

For work.md entries:
1. Check if user specified a project: `/remember --project myapp`
2. Check current working directory for git repo name: run `basename $(git rev-parse --show-toplevel 2>/dev/null)` or check the current directory name
3. If neither available, ask the user: "What project was this for?"
4. Fallback: tag as `general`

### Step 4: Write

**For work.md** — prepend new entry at the top of the file (after the header comments):
```
## YYYY-MM-DD — project-tag
Summary sentence(s) here.
```

**For user.md** — find the right section header and append the new context:
```
## Recent Context
- YYYY-MM-DD: Description of what happened or what the agent learned.
```

**For soul.md** — append to Learned Behaviors:
```
## Learned Behaviors
- Existing behavior
- NEW: User wants responses under 5 sentences unless asked for detail
```

### Step 5: Confirm (manual mode only)

Check `~/.katana/katana.toml` for the memory mode setting.

If `memory.mode = "manual"` (default), show the user what will be saved and where:

```
📝 Memory save:
→ work.md: "Designed v1 memory system with three files and two commands."
   Tagged: katana-agent | 2026-02-22

Save this? (y/n/edit)
```

If `memory.mode = "auto"`, skip confirmation and write directly.

### Step 6: Acknowledge

After saving, briefly confirm:
```
✓ Saved to work.md (katana-agent, 2026-02-22)
```

## Auto Mode Rules

When `memory.mode = "auto"` in katana.toml:

**Save to work.md when:**
- The user switches to a different project or topic
- Something major gets completed (tests pass, feature works, bug fixed)
- 20+ exchanges have happened without a save
- The user says goodbye, thanks, or wraps up

**Save to user.md when:**
- The user shares how they're feeling, what they're struggling with, or goals
- The user mentions a life event, big win, or setback

**Save to soul.md when:**
- The user corrects the agent's behavior or states a preference

## Retention

work.md has a max entry limit (default 200, configurable in katana.toml).
When work.md exceeds this count, trim the oldest entries (bottom of file)
on the next write. soul.md and user.md don't need retention — they're 
living documents that get updated in place, not appended infinitely.
