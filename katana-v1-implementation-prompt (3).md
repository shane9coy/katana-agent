# KATANA V1 IMPLEMENTATION PROMPT

> **Instructions:** Copy this entire prompt and paste it into your CLI agent (Claude Code, Cursor, Windsurf, etc.) from inside your Katana project root directory. The agent will audit your project, architect the folder structure, build the installer, and produce all documentation.

---

## SYSTEM CONTEXT

You are a senior software architect working inside the Katana Agent project directory. Katana is an open-source NPM package that installs an agentic framework with pre-built skills (integrations) into any project. Users install via `npm install katana` then `npx katana init`. Your job is to implement the v1 release with a full agent-assisted installer, updated documentation, and clean architecture.

**Do not assume anything about the current state of the project. You must audit first.**

---

## PHASE 1: FULL PROJECT AUDIT

Before writing a single line of code or documentation, perform a complete audit of the entire project directory.

### Step 1A — Map the full file tree
Recursively list every file and folder in this project. Output the complete tree structure. Pay special attention to:
- Any `.agent/` or `katana-agent/` or `.katana/` directories
- Any `skills/` directories and what's inside each skill folder
- Any `manual/` or `docs/` or `manuals/` directories
- Any `.env` or `.env.example` or config files
- Any `commands/` directory
- The current `package.json` (read it fully)
- The current `README.md` (read it fully)
- Any existing install scripts (Python, bash, or JS)
- Any loose or orphaned files that seem related to features but aren't organized

### Step 1B — Analyze every skill/feature
For each skill or feature folder you find:
1. Read every file inside it (including empty skeleton files)
2. Identify what the feature does
3. Identify what credentials/API keys/env vars it needs
4. Identify what dependencies it requires
5. Note whether it's a working implementation, a skeleton/placeholder, or incomplete
6. Note the file path of any `.env` references or config patterns

### Step 1C — Identify floating/orphaned content
Find any files that:
- Exist in the `manual/` folder or similar documentation directories
- Are loose in the root or in unexpected locations
- Contain useful information about features but aren't properly organized
- Are duplicates or outdated versions of other files

### Step 1D — Output the audit report
Before proceeding, output a structured audit report with:
- Complete file tree
- Feature inventory table (feature name, status, folder path, env vars needed, dependencies)
- List of orphaned/misplaced files and what to do with each
- Current README assessment (what's missing, what's outdated)
- Current package.json assessment

**STOP HERE and show me the audit report before proceeding to Phase 2. Ask me to confirm before continuing.**

---

## PHASE 2: FOLDER ARCHITECTURE

Based on the audit, restructure the project to follow this architecture. Do NOT delete any working code — move and reorganize.

### Target Structure

```
katana/
├── package.json
├── README.md
├── LICENSE
├── bin/
│   └── katana.js                    # CLI entry point (npx katana init, katana installer, etc.)
├── src/
│   ├── init.js                      # Scaffolding logic for npx katana init
│   ├── installer.js                 # Agent installer activation logic
│   └── utils/
├── template/                        # What gets copied into user's project on init
│   ├── katana-agent/
│   │   ├── .katana/                 # Memory, user config, installed skill registry
│   │   │   ├── memory/
│   │   │   ├── config/
│   │   │   │   └── .env             # All credentials go here — single source of truth
│   │   │   └── installed.json       # Tracks which skills are active
│   │   ├── skills/                  # Pre-built skill folders (ship with all of them)
│   │   │   ├── gmail/
│   │   │   ├── google-suite/
│   │   │   ├── google-calendar/
│   │   │   ├── telegram-bot/
│   │   │   ├── trello/
│   │   │   ├── obsidian-memory/
│   │   │   ├── web-browsing/        # Playwright
│   │   │   ├── skill-builder/
│   │   │   ├── mcp-builder/
│   │   │   ├── live-news/
│   │   │   ├── oracle/
│   │   │   └── [any others found in audit]
│   │   ├── commands/
│   │   │   ├── installer.md         # The setup guide the agent reads
│   │   │   └── [other command definitions]
│   │   └── docs/
│   │       └── setup-guide.md       # Detailed human-readable setup reference
│   └── .env.example                 # Template showing all possible env vars
├── docs/
│   └── FEATURES.md                  # Compiled feature documentation
└── scripts/
    └── [any utility scripts]
```

### Architecture Rules
1. The `.katana/` folder lives INSIDE `katana-agent/`, not as a sibling — everything is consolidated under one directory
2. There is ONE `.env` file at `.katana/config/.env` — every skill reads credentials from this single location
3. Every skill folder must contain at minimum: a `README.md` explaining what it does, a skill definition file, and any implementation files
4. The `commands/` folder holds `.md` files that the agent reads to know how to execute commands
5. Move all orphaned documentation into `docs/` or into the relevant skill folder
6. Move all orphaned feature code into the correct skill folder

**Show me the proposed moves (old path → new path) before executing. Ask me to confirm.**

---

## PHASE 3: THE AGENT INSTALLER

### 3A — Decide: Command vs. Skill vs. Both

The installer should be BOTH:
- A **command** accessible via `katana installer` in the CLI
- A **skill** that lives in `skills/` so the agent always knows how to help with setup

Create:
1. `commands/installer.md` — the command definition the agent reads when user types `katana installer`
2. `skills/installer/` — a skill folder with the full setup knowledge

### 3B — Create `commands/installer.md`

This is the core file the agent reads to guide users through setup. Write it as agent instructions in this format:

```markdown
# Katana Installer — Agent Setup Guide

## Your Role
You are the Katana setup assistant. When the user activates this command, 
you walk them through enabling and configuring every available feature 
in their Katana agent installation.

## Before You Begin
1. Read the project README.md to understand the full Katana ecosystem
2. Scan the skills/ directory to see all available features
3. Check .katana/config/.env to see what's already configured
4. Check .katana/installed.json to see what's already enabled

## Setup Flow

### Welcome
Greet the user. Explain that you'll walk them through setting up their 
Katana agent features one by one. Tell them they can skip any feature 
and come back later.

### For Each Feature (iterate through skills/ directory):

**[Feature Name]**
- Explain: What this feature does in 1-2 sentences
- Requirements: What API keys, tokens, or credentials are needed
- Where to get them: Direct URLs and step-by-step instructions for obtaining credentials
- Configuration: Which env vars to set in .katana/config/.env
- Validation: How to test that it's working
- Tip: If on desktop, suggest downloading the relevant app for easy copy-paste of API keys

### Feature Details (populate from audit):
[FOR EACH FEATURE FOUND IN THE AUDIT, CREATE A SECTION WITH:]
- Feature name
- Description (from analyzing the skill files)
- Required env vars (exact variable names from the code)
- Where to obtain credentials (URLs)
- Setup steps
- How to verify it works

### After Setup
- Show summary of what's enabled vs skipped
- Update .katana/installed.json with active features
- Remind user they can run `katana installer` again anytime to add more features
- Point them to the README for usage documentation

## Credential Locations
ALL credentials go in: .katana/config/.env
The .env file uses this format:
[LIST EVERY ENV VAR FROM EVERY FEATURE, GROUPED BY FEATURE, WITH COMMENTS]

## Important Notes
- Never ask the user to manually edit .env files — offer to write the values for them
- If a user seems confused, reference the README or the specific skill's documentation
- If a credential is invalid, explain what might be wrong and how to fix it
```

### 3C — Create the `.env.example` file

From the audit, compile EVERY environment variable across ALL features into one `.env.example` file with clear comments grouping them by feature:

```env
# ============================================
# KATANA AGENT CONFIGURATION
# All credentials managed in one place
# ============================================

# --- Core ---
KATANA_MODEL=claude          # LLM provider (claude, openai, etc.)
ANTHROPIC_API_KEY=           # Your Claude API key

# --- Gmail Integration ---
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
GMAIL_REDIRECT_URI=

# --- Google Calendar ---
GOOGLE_CALENDAR_API_KEY=

# [... every feature ...]
```

### 3D — Wire up the CLI command

In `bin/katana.js`, ensure that when a user runs `katana installer` from their terminal, it:
1. Detects the katana-agent directory in the current project
2. Loads the `commands/installer.md` file
3. Passes it to the active LLM agent as system context
4. Starts the interactive setup conversation

---

## PHASE 4: THE README

### 4A — Compile feature documentation

Before writing the README, for EACH feature/skill:
1. Re-read every file in that skill's folder
2. Extract: what it does, how it works, what commands it exposes
3. If there are existing manual pages or docs, incorporate them
4. Compile into a `docs/FEATURES.md` master reference

### 4B — Write the README

The README must include these sections in this order:

```markdown
# 🗡️ Katana Agent

[One-line description: what Katana is]

[2-3 sentence elevator pitch — open source, agentic framework, 
pre-built skills, works with Claude, runs in any CLI]

## Quick Start

### Prerequisites
- Node.js >= [version]
- npm
- A Claude API key (or supported LLM provider)
- Python 3.x (for setup utilities)

### Installation
\`\`\`bash
npm install katana
npx katana init
\`\`\`

### Setup Your Features
\`\`\`bash
katana installer
\`\`\`
This launches the interactive setup agent that walks you through 
enabling and configuring every feature. Just follow the prompts.

## Features

[For EACH feature — compiled from the actual skill files in the project:]

### 📧 Gmail Integration
[What it does, one paragraph]

### 📅 Google Calendar
[What it does]

### 🤖 Telegram Bot
[What it does]

### 📋 Trello Integration
[What it does]

### 🧠 Obsidian Memory
[What it does]

### 🌐 Web Browsing (Playwright)
[What it does]

### 🔧 Skill Builder
[What it does]

### 🔧 MCP Builder
[What it does]

### 📰 Live News Stream
[What it does]

### 🔮 Oracle Agent
[What it does]

### [Any additional features found in audit]

## Architecture
[Explain the folder structure, where skills live, 
where memory lives, where config lives]

## Configuration
All credentials are stored in `katana-agent/.katana/config/.env`
Run `katana installer` for guided setup, or copy `.env.example` 
and fill in manually.

## Adding Custom Skills
[Explain how users can add their own skills to the skills/ folder]
[Note: Also works with any skill downloadable from Claude Skill Hub]

## Roadmap — v2
- Standalone inference engine (choose any LLM provider)
- Voice module ($25 add-on) — plan your day by talking to your agent
- Cron job automation — scheduled recurring tasks
- Process tracking dashboard — see all running agents and their status
- Telegram / Slack messaging — chat with your agent from anywhere
- Business analytics integration
- Web interface

## Contributing
[Standard open source contributing section]

## License
[License info]
```

### 4C — README Rules
- Every feature description must be derived from ACTUALLY READING the skill files in the project — do not make up capabilities
- If a skill folder is empty/skeleton, note it as "coming soon" or describe the intended functionality based on the file structure
- Link to the detailed `docs/FEATURES.md` for full documentation
- Keep the README scannable — someone should understand what Katana does in 30 seconds

---

## PHASE 5: CLEANUP AND VALIDATION

1. Ensure no orphaned files remain outside the proper folder structure
2. Ensure every skill folder has at minimum a README.md
3. Ensure `package.json` has the correct `bin` entry for the CLI commands
4. Ensure `.env.example` contains every env var referenced anywhere in the codebase
5. Ensure `commands/installer.md` references every feature with accurate env var names
6. Ensure the README reflects the actual state of the project (not aspirational features marked as current)
7. Run `npm pack --dry-run` to verify what would be published
8. List any issues or inconsistencies found

---

## EXECUTION ORDER

1. **AUDIT** (Phase 1) → Show me the report, wait for confirmation
2. **ARCHITECTURE** (Phase 2) → Show me proposed moves, wait for confirmation  
3. **INSTALLER** (Phase 3) → Build the installer command, setup guide, .env.example
4. **README** (Phase 4) → Compile features, write README from actual project contents
5. **CLEANUP** (Phase 5) → Final validation pass

**At each phase boundary, stop and ask me to confirm before proceeding.**

---

## CRITICAL REMINDERS

- Read EVERY file before making claims about what a feature does
- The `.env` file is at `.katana/config/.env` — ONE location, not scattered per-feature
- The installer is BOTH a command AND a skill
- The agent writes env values for the user — users should never have to manually edit .env
- Ship with ALL features included, even if some are skeletons
- The README must reflect reality, not aspirations (mark incomplete features honestly)
- The `.katana/` directory lives INSIDE `katana-agent/`, not beside it
- Everything the installer agent needs to know lives in `commands/installer.md`
- The installer agent should also read the README so it understands the full project context
