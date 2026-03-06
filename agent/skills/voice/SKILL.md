---
name: voice
triggers: "voice mode, start listening, voice conversation, speak to me, talk to me, enable voice, voice on, continuous listening, push to talk"
description: "Activate continuous voice conversation loop — speak/listen cycle using MCP voice tools with hotkey or continuous mode."
---

# Voice Skill

Auto-activate when the user wants to switch to voice conversation mode.

## Activation

```
/voice
"enter voice mode"
"start voice conversation"
```

## Core Loop (always runs)

1. `mcp__voice__voice_speak` — speak response
2. `mcp__voice__voice_listen` — wait for user speech
3. Process transcript → repeat

On timeout: retry up to 3× before asking "Are you still there?" — **never drop to text on first timeout.**

## Modes

| Mode | Command | Behavior |
|------|---------|---------|
| Push-to-talk | default | Hotkey triggers listen window |
| Continuous | "enable continuous listening" | Always-on speech detection |
| Off | "exit voice mode" / "stop" | Returns to text |

## Rules

- Keep responses **1–3 sentences** for voice — concise by default
- Every response goes through `voice_speak` — no silent tool calls
- Don't narrate tool usage — just do it and report the result
- Use `voice_mode` with mode `"off"` to exit cleanly

→ Full loop spec: `.claude/commands/voice.md`
