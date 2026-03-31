# Katana Agent V1 — Complete Reference

> **Version:** 1.0.0  
> **Author:** Shane Swrld  
> **Updated:** February 27, 2026  
> **Repo:** github.com/shane9coy/katana-agent  
> **License:** MIT

---

## What Is Katana Agent?

Katana Agent is a CLI tool that installs your personal AI agent into any project. One command drops your skills, commands, and memory config into whatever coding agent you use — Claude Code, KiloCode, Codex, Gemini, Cursor, Windsurf, or anything else.

All agents share a centralized Obsidian vault as their memory. Skills and commands are managed in one place and distributed into projects on demand. Your data never leaves your machine.

**Promo:**

⚡ Life & business personal assistant — orchestrated from any terminal / any CLI agent  
🔒 Secure & self-hosted — your data never leaves your machine  
🎙️ Voice enabled — built-in local voice UI powered by MAGI3  
🧠 Centralized memory between all of your agents and projects

---

## Install

```bash
# From npm (once published)
npm install -g katana-agent

# Or from source
git clone https://github.com/shane9coy/katana-agent.git
cd katana-agent
npm install
npm link
```

After install, the `katana` command is available globally.

---

## Architecture Overview

Katana V1 has two layers:

### 1. The Package (npm install or repo checkout)

The CLI package itself. It can be installed globally via npm or run from a local repository checkout. It reads from your personal `~/.katana/` data folder and writes into projects.

### 2. Your Data (~/.katana/)

Your agent brain. Contains your memory vault, agent personalities, shared settings, and root instructions. This is personal and persistent — it survives across projects, reinstalls, and updates.

```
~/.katana/                           ← YOUR DATA (persistent, personal)
├── memory/                          ← Obsidian vault — THE brain
│   ├── core/
│   │   ├── soul.md                  ← Agent identity and behavior
│   │   ├── user.md                  ← Facts about you
│   │   └── routines.md              ← Learned patterns and workflows
│   ├── work.md                      ← Running work log (newest at top)
│   ├── projects/
│   │   ├── oracle-app/
│   │   │   └── sessions.md          ← Auto-created per project
│   │   ├── katana-agent/
│   │   │   └── sessions.md
│   │   └── ...
│   ├── sessions/                    ← General session summaries
│   └── skills/                      ← Your skill library (organized by category)
│       ├── _index.md                ← Master skill registry
│       ├── email/
│       │   ├── email-best-practices/
│       │   └── email-himalaya/
│       ├── social/
│       │   ├── x-auto-dm/
│       │   ├── x-thread/
│       │   └── telegram/
│       ├── development/
│       │   ├── playwright/
│       │   └── threejs/
│       ├── memory/
│       │   ├── obsidian/
│       │   ├── remember/
│       │   └── recall/
│       ├── agents/
│       │   ├── oracle/
│       │   └── sensei/
│       ├── business/
│       │   └── rent/
│       └── productivity/
│           ├── google-workspace/
│           ├── trello/
│           └── weather/
│
├── commands/                        ← Agent personalities (separate from vault)
│   ├── sensei.md                    ← Main agent
│   ├── oracle.md                    ← Astrology & scheduling
│   ├── stream.md                    ← Content & streaming
│   └── vibe-curator.md              ← Taste & lifestyle
│
├── settings.json                    ← Shared default settings
└── AGENT.md                         ← Shared root agent instructions
```

### How They Connect

When you run `katana claude init` inside a project:

```
~/.katana/commands/sensei.md      →  .claude/commands/sensei.md
~/.katana/commands/oracle.md      →  .claude/commands/oracle.md
~/.katana/memory/skills/email/*   →  .claude/skills/email-best-practices/
~/.katana/memory/skills/social/*  →  .claude/skills/x-auto-dm/
(bundled templates)               →  .claude/skills/obsidian-memory/
(bundled templates)               →  .claude/skills/remember/
(bundled templates)               →  .claude/settings.json
(auto-generated)                  →  .claude/CLAUDE.md
```

Skills come from your Obsidian vault. Commands come from `~/.katana/commands/`. Bundled templates fill in the essentials (obsidian-memory, remember, recall, new-skill). The CLAUDE.md is auto-generated with your detected stack.

---

## Commands Reference

### Init Commands

| Command | Creates | For |
|---------|---------|-----|
| `katana claude init` | `.claude/` | Claude Code |
| `katana kilocode init` | `.kilocode/` | KiloCode |
| `katana codex init` | `.codex/` | OpenAI Codex |
| `katana generic init` | `.agent/` | Gemini, Cursor, Windsurf, Aider, any agent |
| `katana generic init --dir .cursor` | `.cursor/` | Custom folder name |
| `katana init` | `.katana/` | Universal Katana format |

**Flags:**

| Flag | Behavior |
|------|----------|
| (no flag) | Interactive picker — choose which skill categories and commands to install |
| `--all` | Install everything from vault, skip the picker |
| `--minimal` | Bundled template skills only, skip vault entirely |

### Memory Commands

| Command | What It Does |
|---------|-------------|
| `katana memory init` | Create the Obsidian vault at `~/.katana/memory/` |
| `katana memory status` | Show vault health — file sizes, session/project/skill counts |
| `katana memory recall <query>` | Search across all memory files from terminal |
| `katana memory projects` | List all tracked projects with session counts |

### Skills Commands

| Command | What It Does |
|---------|-------------|
| `katana skills list` | List all skills in your vault by category |
| `katana skills sync` | Sync vault skills into current project (any detected agent folder) |

---

## Interactive Skill Picker

When you run `katana claude init` (no flags), you get an interactive picker:

```
⚡ Katana Agent → Claude Code

  Skill Categories:

    1. agents (2 skills) — oracle, sensei
    2. business (1 skill) — rent
    3. development (2 skills) — playwright, threejs-fundamentals
    4. email (2 skills) — email-best-practices, email-himalaya
    5. memory (3 skills) — obsidian, recall, remember
    6. social (3 skills) — telegram, x-auto-dm, x-thread

    a = all, n = none, or enter numbers: 1,3,5

  Install skill categories [a]: 4,6

  Agent Commands:

    1. /oracle
    2. /sensei
    3. /stream
    4. /vibe-curator

    a = all, n = none, or enter numbers: 1,3

  Install commands [a]: a

  → Skills: email, social (5 total)
  → Commands: /oracle, /sensei, /stream, /vibe-curator

  ✓ Loaded 4 command(s) from ~/.katana/commands/
  ✓ Synced 5 skill(s) from Obsidian vault
  ✓ Generated CLAUDE.md (detected: Next.js / TypeScript)
  ✓ Registered project in Obsidian vault → projects/my-app/

  ✓ Katana agent initialized in .claude/

  Commands: 5 installed
  Skills:   9 installed
  Memory:   ~/.katana/memory/ (Obsidian vault)

  Usage: Open this project in Claude Code — your agent is ready.
  Agents: /oracle, /sensei, /stream, /vibe-curator, /voice
  Memory: /remember to save, /recall to search
```

Pick by category folder — select "email" and you get both `email-best-practices/` and `email-himalaya/`. No need to select 20+ individual skills.

---

## Conflict Detection

If the target folder already exists when you run init, Katana asks:

```
⚠️  .claude/ already exists in this project.

  1. Merge    — Add Katana files alongside existing (recommended)
  2. Replace  — Remove existing folder, install fresh
  3. Backup   — Copy existing to .backup-{timestamp}, then install fresh
  4. Cancel   — Do nothing

  Choose [1-4] (default: 1):
```

This runs BEFORE the skill picker. Merge mode preserves your existing files and only adds new ones. Replace nukes and starts fresh. Backup gives you a safety net.

---

## Obsidian Integration

The memory vault at `~/.katana/memory/` is a standard Obsidian vault. Open it in Obsidian and you get:

- **Graph view** showing connections between projects, skills, and memories
- **Full-text search** across all agent memories
- **Wikilinks** — the agent writes `[[project-name]]` links that Obsidian auto-connects
- **YAML frontmatter** — skills have metadata (version, tags, times_used) queryable with Dataview
- **Tags** — `#skill`, `#project`, `#session` for filtering
- **Real-time sync** — every agent write shows up instantly in Obsidian

### Setup

```bash
katana memory init
```

Then open `~/.katana/memory/` as a vault in Obsidian.

### Recommended Obsidian Plugins

- **Dataview** — query frontmatter fields, list skills by category, show recent sessions
- **Graph View** (built-in) — see how projects, skills, and memories connect
- **Templates** — create skill/session templates for consistency

### What the Agent Reads/Writes

| File | Read On | Written When |
|------|---------|-------------|
| `core/soul.md` | Every session start | You edit agent identity |
| `core/user.md` | Every session start | `/remember` captures user facts |
| `core/routines.md` | Every session start | Agent detects patterns |
| `work.md` | `/recall` searches | `/remember` or session end |
| `projects/{name}/sessions.md` | Session start in that project | `/remember` or session end |
| `skills/{category}/{name}/SKILL.md` | Agent checks before solving complex tasks | Agent auto-creates skills |
| `skills/_index.md` | Agent checks available skills | Agent creates or discovers skills |

### Organizing Skills in the Vault

Skills are organized by category folder:

```
~/.katana/memory/skills/
├── _index.md              ← Master registry
├── email/                 ← Category: email
│   ├── email-best-practices/
│   │   ├── SKILL.md
│   │   └── resources/
│   └── email-himalaya/
│       ├── SKILL.md
│       └── references/
├── social/                ← Category: social
│   ├── x-auto-dm/
│   ├── x-thread/
│   └── telegram/
├── development/           ← Category: development
│   ├── playwright/
│   └── threejs/
└── ...
```

Each category folder maps to one checkbox in the picker. Create new categories by making a new folder and adding skill subfolders with `SKILL.md` files.

### user.md Template

Fill this in after `katana memory init`:

```markdown
---
type: user
updated: 2026-02-26
---

# User

## Identity
- Name: (your name)
- Location: (your city)
- Role: (what you do)

## Preferences
- Communication style: direct, no fluff
- Technical level: advanced

## Current Focus
- (what you're working on right now)

## Tech Stack
- (your primary languages and tools)

## Recent Context
<!-- Agent appends here when you /remember -->
```

---

## What Gets Installed Per Platform

### Claude Code (.claude/)

```
.claude/
├── CLAUDE.md                        ← Auto-generated (detects stack, lists scripts)
├── settings.json                    ← Permissions for bash, file ops, memory access
├── commands/                        ← Agent personalities from ~/.katana/commands/
│   ├── sensei.md
│   ├── oracle.md
│   ├── stream.md
│   ├── vibe-curator.md
│   └── voice.md                     ← Bundled (MAGI3 voice mode)
└── skills/                          ← Skills from vault + bundled
    ├── obsidian-memory/             ← Bundled: connects agent to vault
    ├── remember/                    ← Bundled: /remember command
    ├── recall/                      ← Bundled: /recall command
    ├── new-skill/                   ← Bundled: skill creator
    └── (selected vault skills...)   ← From interactive picker
```

### KiloCode (.kilocode/)

```
.kilocode/
├── AGENTS.md                        ← Auto-generated project file
├── agents/                          ← Agent personalities
└── skills/                          ← Skills from vault + bundled
```

### Codex (.codex/)

```
.codex/
├── AGENTS.md                        ← Auto-generated project file
├── commands/                        ← Agent personalities
└── skills/                          ← Skills from vault + bundled
```

### Generic (.agent/ or custom)

```
.agent/                              ← Or .cursor/, .windsurf/, whatever you pass --dir
├── AGENT.md                         ← Auto-generated with vault instructions
├── commands/                        ← Agent personalities
└── skills/                          ← Skills from vault + bundled
```

---

## Stack Detection

Katana auto-detects your project stack and generates the appropriate project file:

| Config File | Detected Stack |
|------------|---------------|
| `package.json` with `next` | Next.js / TypeScript |
| `package.json` with `react` | React |
| `package.json` with `express` | Express / Node.js |
| `package.json` with `vue` | Vue |
| `package.json` with `svelte` | Svelte |
| `pyproject.toml` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `Gemfile` | Ruby |
| `pom.xml` / `build.gradle` | Java |

The generated CLAUDE.md / AGENTS.md / AGENT.md includes the detected stack, available npm scripts, and memory vault instructions.

---

## Project Registration

Every `katana {platform} init` automatically creates a project entry in your Obsidian vault:

```
~/.katana/memory/projects/{project-name}/
└── sessions.md
```

This file tracks session history for that project. The agent appends to it when you use `/remember`. You can view all tracked projects with:

```bash
katana memory projects
```

---

## Bundled Skills (Installed with Every Init)

### obsidian-memory

The core skill. Tells the agent:
- Where the vault is (`~/.katana/memory/`)
- What to read on session start (soul.md, user.md)
- How to write (YAML frontmatter, wikilinks, tags, newest-at-top)
- Obsidian-compatible markdown formatting rules

### remember

Triggered by `/remember`, "remember this", or session end. Classifies the memory:
- Behavior changes → soul.md
- User preferences → user.md
- Work done → work.md (new entry at top with date header)
- Project context → projects/{name}/sessions.md

### recall

Triggered by `/recall` or "what did we work on". Searches:
- work.md for work history
- projects/{name}/sessions.md for project context
- Full-text grep across all .md files for broad queries

### new-skill

Creates properly structured skills in the vault:
```
~/.katana/memory/skills/{category}/{skill-name}/
├── SKILL.md              ← Main file with YAML frontmatter
├── references/           ← Supporting docs
└── scripts/              ← Executables
```

Checks `_index.md` first to avoid duplicates. Updates the index after creation.

---

## Data Flow Summary

```
┌─────────────────────────────────────────────────────┐
│                  ~/.katana/memory/                    │
│                  (Obsidian Vault)                     │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐ │
│  │ core/    │  │ work.md  │  │ skills/            │ │
│  │ soul.md  │  │          │  │ ├── email/         │ │
│  │ user.md  │  │          │  │ ├── social/        │ │
│  │routines  │  │          │  │ ├── development/   │ │
│  └────┬─────┘  └────┬─────┘  └────────┬───────────┘ │
│       │              │                  │             │
└───────┼──────────────┼──────────────────┼─────────────┘
        │              │                  │
        │ read on      │ /remember        │ katana claude init
        │ session      │ writes           │ copies selected
        │ start        │ here             │ categories
        │              │                  │
        ▼              ▼                  ▼
┌─────────────────────────────────────────────────────┐
│              Your Project (.claude/)                  │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐ │
│  │CLAUDE.md │  │commands/ │  │ skills/            │ │
│  │(auto-gen)│  │sensei.md │  │ obsidian-memory/   │ │
│  │          │  │oracle.md │  │ remember/          │ │
│  │          │  │stream.md │  │ recall/            │ │
│  │          │  │          │  │ email-best-prax/   │ │
│  │          │  │          │  │ x-auto-dm/         │ │
│  └──────────┘  └──────────┘  └────────────────────┘ │
│                                                       │
│  The agent reads skills locally, writes memory back   │
│  to the vault via obsidian-memory skill instructions  │
└─────────────────────────────────────────────────────┘
```

---

## File Structure (The npm Package)

```
katana-agent/                        ← The tool itself
├── bin/
│   └── katana.js                    ← CLI entry point
├── src/
│   ├── init/
│   │   ├── claude.js                ← .claude/ generator
│   │   ├── kilocode.js              ← .kilocode/ generator
│   │   ├── codex.js                 ← .codex/ generator
│   │   ├── generic.js               ← .agent/ generator (any platform)
│   │   └── universal.js             ← .katana/ generator
│   ├── conflict.js                  ← Merge/replace/backup/cancel prompt
│   ├── picker.js                    ← Interactive skill category + command picker
│   ├── memory.js                    ← Memory vault init, status, recall, projects
│   ├── skills.js                    ← Skills list and sync
│   └── utils.js                     ← File ops, stack detection, vault access
├── templates/
│   ├── claude/                      ← Bundled defaults for Claude Code
│   │   ├── commands/voice.md
│   │   ├── settings.json
│   │   └── skills/
│   │       ├── obsidian-memory/
│   │       ├── remember/
│   │       ├── recall/
│   │       └── new-skill/
│   ├── kilocode/                    ← Bundled defaults for KiloCode
│   ├── codex/                       ← Bundled defaults for Codex
│   ├── generic/                     ← Bundled defaults for generic agents
│   └── universal/                   ← Bundled defaults for .katana/
├── package.json
└── README.md
```

---

## V2 Roadmap

Katana V1 is the skill installer. V2 is the inference layer.

**V2: Katana Router** — A standalone Node.js daemon running on `localhost:3737` with:

- Direct API access to Claude, Grok, GPT, Ollama (no middleman)
- Its own tool-calling inference loop (ported from Hermes Agent patterns)
- Provider routing with fallback chains
- Parallel tool execution
- WebSocket streaming
- MAGI3 voice integration
- Telegram/Slack gateway
- Cron scheduler for autonomous tasks
- All powered by the same Obsidian memory vault

V1 installs your agent. V2 IS your agent.

---

## Quick Reference

```bash
# First time setup
npm install -g katana-agent
katana memory init                    # Create Obsidian vault
# Open ~/.katana/memory/ in Obsidian
# Fill in core/user.md with your info

# Per project
cd ~/projects/my-app
katana claude init                    # Interactive picker
katana claude init --all              # Everything, no questions
katana claude init --minimal          # Bundled only, no vault

# Memory
katana memory status                  # Vault health
katana memory recall "x api"          # Search memory
katana memory projects                # List tracked projects

# Skills
katana skills list                    # List vault skills
katana skills sync                    # Sync vault → current project

# Other platforms
katana kilocode init
katana codex init
katana generic init
katana generic init --dir .cursor
```
