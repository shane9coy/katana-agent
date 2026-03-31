![download (2)](https://github.com/user-attachments/assets/7a056c26-0052-42f8-92da-a6e5e71eace0)

# ⚡ Katana Agent

**One command. Every AI agent. Centralized memory.**

Drop your skills, commands, and Obsidian-powered memory into any CLI agent — Claude Code, Codex, KiloCode, Gemini, Cursor, Windsurf, or anything else. Self-hosted. Private. Your data never leaves your machine.

---

## Install

```bash
npm install -g katana-agent
```

## 30-Second Setup

```bash
# 1. Create your memory vault (one time)
katana memory init

# 2. Open ~/.katana/memory/ in Obsidian (optional but powerful)

# 3. Drop your agent into any project
katana init

# Or initialize for a specific CLI agent
katana claude init
katana gemini init
katana codex init
katana kilocode init
katana generic init

(each buildout is tailored to the specific CLI's default .agent folder structure)


```

That's it. Your agent is ready with skills, commands, and centralized memory.

---

## What It Does

Katana manages your AI agent across every project from one place:

```
~/.katana/                           Your agent brain (persistent)
├── memory/                          Obsidian vault — shared across ALL projects
│   ├── core/soul.md                 Agent identity
│   ├── core/user.md                 Facts about you
│   ├── work.md                      Running work log
│   ├── projects/                    Per-project session history
│   └── skills/                      Your skill library (organized by category)
│       ├── email/
│       ├── social/
│       ├── development/
│       └── ...
├── commands/                        Agent personalities
├── settings.json                    Shared default settings
└── AGENT.md                         Shared root agent instructions
```

When you run `katana claude init` in a project, it:

1. **Asks what to install** — interactive picker by skill category
2. **Copies selected skills** from your Obsidian vault into the project
3. **Copies your agent commands** (personalities) into the project
4. **Auto-generates** a project file (CLAUDE.md) with your detected stack
5. **Registers the project** in your memory vault for session tracking

Every agent, every project, same memory. Edit once in Obsidian, it's everywhere.

---

## Supported Platforms

| Command | Creates | For |
|---------|---------|-----|
| `katana claude init` | `.claude/` | Claude Code |
| `katana kilocode init` | `.kilocode/` | KiloCode |
| `katana codex init` | `.codex/` | OpenAI Codex |
| `katana generic init` | `.agent/` | Gemini, Cursor, Windsurf, Aider, anything |
| `katana generic init --dir .cursor` | `.cursor/` | Custom folder name |

### Flags

```bash
katana claude init              # Interactive picker
katana claude init --all        # Install everything, no questions
katana claude init --minimal    # Bundled essentials only
```

---

## Interactive Skill Picker

Choose what to install by category — no flooding your project with 30 skills you don't need:

```
⚡ Katana Agent → Claude Code

  Skill Categories:

  Use ↑/↓ arrows to navigate
  Press Space to toggle selections
  Highlight Continue and press Enter to confirm

  [x] Select All
  [x] agents — 4 skills
  [x] email — 2 skills
  [ ] memory — 4 skills
  → Continue

  Current selection: 2 selected

  ✓ Loaded 4 command(s) from ~/.katana/commands/
  ✓ Synced 5 skill(s) from Obsidian vault
  ✓ Generated CLAUDE.md (detected: Next.js / TypeScript)
  ✓ Registered project in Obsidian vault

  ✓ Katana agent initialized in .claude/
```

---

## Obsidian as Your Agent's Brain

Your memory vault at `~/.katana/memory/` is a standard Obsidian vault:

- **Graph view** — see connections between projects, skills, and memories
- **Full-text search** — find anything your agent has ever learned
- **Wikilinks** — `[[project-name]]` links auto-connect in Obsidian
- **Tags & frontmatter** — `#skill`, `#project`, queryable with Dataview
- **Real-time** — every agent write shows up instantly

```bash
katana memory status          # Vault health
katana memory recall "api"    # Search memory from terminal
katana memory projects        # List tracked projects
```

---

## Conflict Detection

Already have a `.claude/` folder? Katana handles it:

```
⚠️  .claude/ already exists in this project.

  1. Merge    — Add Katana files alongside existing (recommended)
  2. Replace  — Remove existing folder, install fresh
  3. Backup   — Copy existing to .backup, then install fresh
  4. Cancel   — Do nothing
```

Your existing settings.json is preserved unless you explicitly choose to overwrite it.

---

## Roadmap

### V2: Katana Router *(In Development)*

V1 installs your agent. V2 **IS** your agent.

- 🧠 Self-hosted inference daemon — `localhost:3737`
- 🔀 Direct API to Claude, Grok, GPT, Ollama — no middleman, no subscriptions
- 🔧 Own tool-calling loop with parallel execution
- 🎙️ Voice-native via MAGI3
- 📱 Telegram, Slack, Discord gateways
- ⏰ Autonomous cron jobs
- 🔒 100% self-hosted — your keys, your data, your machine

Same Obsidian memory vault. Same skills. Now with its own brain.

---

## License

Source-available with attribution. Free for personal use. Commercial use requires a revenue-sharing agreement. See [LICENSE](LICENSE) for details.

## Author

**Shane Swrld** — [@shaneswrld_](https://x.com/shaneswrld_) · [github.com/shane9coy](https://github.com/shane9coy)
