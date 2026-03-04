# Katana Agent V1.1 — Migration & Feature Build Prompt

> **What:** Migrate katana-agent from a split architecture (code in `~/katana-agent/`, data in hidden `~/.katana/`) to a single self-contained package with everything in `~/katana-agent/agent/`. Ship V1.1 with pre-installed base features, news stream, the new `/katana` master agent, and a setup assistant.
>
> **Run this from inside `~/katana-agent/`.** The agent should audit first, confirm with the user at each phase, then execute.

---

## SUMMARY — WHAT V1.1 SHIPS WITH

**Katana Agent V1.1** is the "batteries included" release. Everything lives in one folder. Users clone or npm install, run `setup.sh`, and they're ready.

### What's New in V1.1

1. **Self-contained package** — No more hidden `~/.katana/` folder. Memory, skills, commands, and settings all live inside `~/katana-agent/agent/`. One folder, one repo, one npm package.

2. **`/katana` master agent** — Replaces the old `/sensei` command. This is the main agent personality — personal life & business assistant. The command file is `agent/commands/katana.md`.

3. **`/stream` news agent** — RSS feed monitoring and market intelligence. Fetches from Seeking Alpha, MarketWatch, CNBC, Federal Reserve, and X financial influencers. Feed URLs stored in `agent/skills/productivity/stream/feeds.json`. The `/katana` morning routine calls `/stream` automatically.

4. **Setup assistant** — `setup.sh` (shell script) handles system-level install (npm, linking, verification). `agent/skills/agents/installer/SKILL.md` turns any CLI agent into a setup wizard that walks users through API key config, user profile, and skill enabling.

5. **26 pre-installed skills** organized into 7 categories (email, social, development, productivity, memory, agents, business).

6. **6 agent commands** — `/katana`, `/oracle`, `/stream`, `/vibe-curator`, `/voice`, plus the installer.

### Architecture Change

```
BEFORE (V1.0):                          AFTER (V1.1):
~/katana-agent/  ← code only            ~/katana-agent/  ← EVERYTHING
~/.katana/       ← hidden, separate     ├── agent/       ← memory + skills + commands
    ├── memory/                          │   ├── memory/
    ├── commands/                        │   ├── commands/
    └── skills/                          │   ├── skills/
                                         │   └── settings.json
                                         ├── bin/         ← CLI
                                         ├── src/         ← installer code
                                         ├── templates/   ← platform scaffolds
                                         ├── setup.sh     ← NEW: bootstrap script
                                         ├── package.json
                                         ├── README.md
                                         └── LICENSE
```

---

## CURRENT ~/.katana/ CONTENTS (source of truth for migration)

This is the complete tree of what exists in `~/.katana/` right now. Every file and folder listed here must be migrated into `~/katana-agent/agent/`.

```
.katana/
├── commands/
│   ├── katana.md                    ← MASTER AGENT (was sensei.md, renamed)
│   ├── oracle.md
│   ├── stream.md                    ← NEW
│   ├── vibe-curator.md
│   └── voice.md
├── memory/
│   ├── core/
│   │   ├── soul.md
│   │   ├── user.md
│   │   └── routines.md
│   ├── work.md
│   ├── projects/
│   │   └── (per-project session files)
│   ├── sessions/
│   └── settings.json
├── project.yaml
└── skills/
    ├── RentAHuman/
    │   ├── SKILL.md
    │   └── scripts/
    │       └── bounty_hunter.py
    ├── competitive-ads-extractor/
    │   └── SKILL.md
    ├── email-best-practices/
    │   ├── README.md
    │   ├── SKILL.md
    │   └── resources/
    │       ├── branding.md
    │       ├── compliance.md
    │       ├── deliverability.md
    │       ├── email-capture.md
    │       ├── email-types.md
    │       ├── list-management.md
    │       ├── marketing-emails.md
    │       ├── sending-reliability.md
    │       ├── transactional-email-catalog.md
    │       ├── transactional-emails.md
    │       └── webhooks-events.md
    ├── email-non-gmail-himalaya/
    │   ├── SKILL.md
    │   └── references/
    │       ├── configuration.md
    │       └── message-composition.md
    ├── go-places/
    │   ├── SKILL.md
    │   └── _meta.json
    ├── google-workspace-gog/
    │   └── SKILL.md
    ├── installer/
    │   └── SKILL.md                 ← NEW: setup wizard skill
    ├── new-mcp-builder/
    │   └── SKILL.md
    ├── new-skill/
    │   ├── SKILL.md
    │   └── references/
    │       └── skill-authoring-guide.md
    ├── new-skill-builder/
    │   ├── SKILL.md
    │   └── references/
    │       ├── Agent-Skills-Architecture-Guide.md
    │       └── claude-skills-guide.md
    ├── obsidian/
    │   ├── SKILL.md
    │   └── _meta.json
    ├── obsidian-memory/
    │   └── SKILL.md
    ├── oracle/
    │   └── SKILL.md
    ├── playwright/
    │   └── SKILL.md
    ├── pulse/
    │   └── SKILL.md
    ├── recall/
    │   └── SKILL.md
    ├── reddit-bot/
    │   └── SKILL.md
    ├── remember/
    │   └── SKILL.md
    ├── katana/
    │   └── SKILL.md                 ← Was sensei/, renamed
    ├── stream/
    │   ├── SKILL.md                 ← NEW: RSS feed skill
    │   └── feeds.json               ← NEW: feed URL config
    ├── telegram/
    │   └── SKILL.md
    ├── threads-bot/
    │   ├── .env.example
    │   ├── SKILL.md
    │   └── scripts/
    │       ├── post_to_threads.py
    │       └── x_to_threads_stream.py
    ├── trello/
    │   └── SKILL.md
    ├── vibe-curator/
    │   └── SKILL.md
    ├── weather/
    │   └── SKILL.md
    ├── x-auto-dm/
    │   ├── SKILL.md
    │   ├── references/
    │   │   ├── data_dictionary.md
    │   │   ├── docs-index.md
    │   │   ├── migration-oauth2.md
    │   │   ├── quick-ref.md
    │   │   ├── send-dm.md
    │   │   ├── stream-posts.md
    │   │   ├── x-api-costs.md
    │   │   └── x-api-endpoint-map.md
    │   └── scripts/
    │       ├── data/
    │       │   ├── cost_stats.json
    │       │   ├── processed_comments.json
    │       │   ├── processed_users.json
    │       │   ├── stream_rules.json
    │       │   └── unsuccessful_first_dm.json
    │       ├── post_to_x.py
    │       ├── x_auto_dm_config.json
    │       ├── x_dm_campaign_manager.py
    │       └── x_send_dm.py
    └── x-thread/
        ├── SKILL.md
        └── scripts/
            └── post_to_x.py
```

**Total: 6 commands, 27 skills (including new installer + stream), 70+ files**

---

## SKILL CATEGORY MAPPING

When organizing skills into `agent/skills/`, use these categories:

| Category | Skills |
|----------|--------|
| **email/** | email-best-practices, email-non-gmail-himalaya |
| **social/** | x-auto-dm, x-thread, telegram, threads-bot, reddit-bot |
| **development/** | playwright, new-mcp-builder, new-skill, new-skill-builder |
| **productivity/** | google-workspace-gog, trello, weather, go-places, stream, pulse |
| **memory/** | obsidian, obsidian-memory, remember, recall |
| **agents/** | oracle, katana, vibe-curator, installer |
| **business/** | RentAHuman, competitive-ads-extractor |

Each skill folder keeps its internal structure intact (SKILL.md, references/, scripts/, feeds.json, etc). Only the parent category grouping changes.

---

## IMPORTANT NAMING CHANGES

Throughout the entire codebase, the following renames MUST be applied:

| Old Name | New Name | Affected Files |
|----------|----------|---------------|
| `sensei.md` | `katana.md` | commands/, skills/agents/, generated CLAUDE.md, README, help text |
| `/sensei` | `/katana` | All console output, summary lines, help text, template SKILL.md files |
| `~/.katana/` | `~/katana-agent/agent/` | Every path reference in src/, bin/, templates/ |
| `~/.katana/memory/` | `~/katana-agent/agent/memory/` | Every vault reference |
| `~/.katana/commands/` | `~/katana-agent/agent/commands/` | Every command loading reference |

**Grep the entire codebase for "sensei" and replace with "katana". Grep for "~/.katana" and update paths.**

---

## NEW FILES TO CREATE

These files are provided separately and should be placed BEFORE running the migration:

### 1. setup.sh → ~/katana-agent/setup.sh

Shell script for bootstrapping. Verifies install, links CLI, checks agent/ folder, lists skills/commands, outputs next steps. Already provided as a separate file.

### 2. agent/commands/katana.md

The master agent personality. This is the main `/katana` command — personal life & business assistant. The morning routine should include calling `/stream` for news.

### 3. agent/commands/stream.md

The news/market intelligence agent personality. Reads `feeds.json`, curls RSS feeds, summarizes into a categorized briefing.

### 4. agent/skills/productivity/stream/SKILL.md + feeds.json

The stream skill with feed configuration. `feeds.json` contains 13 RSS/JSON feed URLs across markets, economy, government, and X financial influencers.

### 5. agent/skills/agents/installer/SKILL.md

Setup wizard skill. Any CLI agent reads this and becomes the onboarding assistant — walks users through API keys, user profile, skill configuration.

---

## PHASE 1: AUDIT CURRENT STATE

Before making any changes, audit both locations:

### Step 1A: Map the katana-agent repo
```bash
find ~/katana-agent -not -path '*/node_modules/*' -not -path '*/.git/*' | sort
```

Read every file in `src/` to catalog all path references to `~/.katana/`, `KATANA_HOME`, `MEMORY_DIR`, `VAULT_SKILLS_DIR`, `COMMANDS_DIR`.

### Step 1B: Map the ~/.katana folder
```bash
find ~/.katana -not -path '*/.obsidian/*' -not -name '.DS_Store' | sort
```

Catalog everything that needs to be moved.

### Step 1C: Identify every file with path references

These files contain paths that MUST be updated:

| File | References to update |
|------|---------------------|
| `src/utils.js` | `KATANA_HOME`, `MEMORY_DIR`, `VAULT_SKILLS_DIR`, `COMMANDS_DIR` — lines 7-10 |
| `src/memory.js` | Imports `KATANA_HOME`, `MEMORY_DIR` from utils |
| `src/skills.js` | Imports `VAULT_SKILLS_DIR` from utils |
| `src/init/claude.js` | Imports `MEMORY_DIR`, `COMMANDS_DIR`, references to settings.json source |
| `src/init/kilocode.js` | Imports `MEMORY_DIR`, `COMMANDS_DIR` |
| `src/init/codex.js` | Imports `MEMORY_DIR`, `COMMANDS_DIR` |
| `src/init/generic.js` | Imports `MEMORY_DIR`, `COMMANDS_DIR` |
| `src/init/universal.js` | Imports from utils |
| `bin/katana.js` | Help text references |
| `templates/*/skills/obsidian-memory/SKILL.md` | Vault location references |
| `templates/*/skills/remember/SKILL.md` | Vault location references |
| `templates/*/skills/recall/SKILL.md` | Vault location references |
| `README.md` | All path references |

### Step 1D: Check for any "sensei" references
```bash
grep -r "sensei" ~/katana-agent/src/ ~/katana-agent/bin/ ~/katana-agent/templates/ --include='*.js' --include='*.md'
```

**Show me the audit results before proceeding. Confirm with me.**

---

## PHASE 2: CREATE THE AGENT FOLDER STRUCTURE

### Step 2A: Create agent/ directory
```bash
cd ~/katana-agent
mkdir -p agent
```

### Step 2B: Copy memory
```bash
rsync -av --exclude='.obsidian' --exclude='.DS_Store' ~/.katana/memory/ ~/katana-agent/agent/memory/
```

### Step 2C: Copy commands
```bash
rsync -av --exclude='.DS_Store' ~/.katana/commands/ ~/katana-agent/agent/commands/
```

### Step 2D: Copy and organize skills into categories
```bash
# Create category folders
mkdir -p ~/katana-agent/agent/skills/{email,social,development,productivity,memory,agents,business}

# Email
cp -r ~/.katana/skills/email-best-practices ~/katana-agent/agent/skills/email/
cp -r ~/.katana/skills/email-non-gmail-himalaya ~/katana-agent/agent/skills/email/

# Social
cp -r ~/.katana/skills/x-auto-dm ~/katana-agent/agent/skills/social/
cp -r ~/.katana/skills/x-thread ~/katana-agent/agent/skills/social/
cp -r ~/.katana/skills/telegram ~/katana-agent/agent/skills/social/
cp -r ~/.katana/skills/threads-bot ~/katana-agent/agent/skills/social/
cp -r ~/.katana/skills/reddit-bot ~/katana-agent/agent/skills/social/

# Development
cp -r ~/.katana/skills/playwright ~/katana-agent/agent/skills/development/
cp -r ~/.katana/skills/new-mcp-builder ~/katana-agent/agent/skills/development/
cp -r ~/.katana/skills/new-skill ~/katana-agent/agent/skills/development/
cp -r ~/.katana/skills/new-skill-builder ~/katana-agent/agent/skills/development/

# Productivity
cp -r ~/.katana/skills/google-workspace-gog ~/katana-agent/agent/skills/productivity/
cp -r ~/.katana/skills/trello ~/katana-agent/agent/skills/productivity/
cp -r ~/.katana/skills/weather ~/katana-agent/agent/skills/productivity/
cp -r ~/.katana/skills/go-places ~/katana-agent/agent/skills/productivity/
cp -r ~/.katana/skills/stream ~/katana-agent/agent/skills/productivity/
cp -r ~/.katana/skills/pulse ~/katana-agent/agent/skills/productivity/

# Memory
cp -r ~/.katana/skills/obsidian ~/katana-agent/agent/skills/memory/
cp -r ~/.katana/skills/obsidian-memory ~/katana-agent/agent/skills/memory/
cp -r ~/.katana/skills/remember ~/katana-agent/agent/skills/memory/
cp -r ~/.katana/skills/recall ~/katana-agent/agent/skills/memory/

# Agents
cp -r ~/.katana/skills/oracle ~/katana-agent/agent/skills/agents/
cp -r ~/.katana/skills/katana ~/katana-agent/agent/skills/agents/
cp -r ~/.katana/skills/vibe-curator ~/katana-agent/agent/skills/agents/
cp -r ~/.katana/skills/installer ~/katana-agent/agent/skills/agents/

# Business
cp -r ~/.katana/skills/RentAHuman ~/katana-agent/agent/skills/business/
cp -r ~/.katana/skills/competitive-ads-extractor ~/katana-agent/agent/skills/business/
```

### Step 2E: Copy settings.json
```bash
cp ~/.katana/memory/settings.json ~/katana-agent/agent/settings.json 2>/dev/null || true
```

### Step 2F: Verify target structure

After all copies, `agent/` should look like:

```
agent/
├── memory/
│   ├── core/
│   │   ├── soul.md
│   │   ├── user.md
│   │   └── routines.md
│   ├── work.md
│   ├── projects/
│   └── sessions/
├── commands/
│   ├── katana.md                    ← Master agent
│   ├── oracle.md
│   ├── stream.md
│   ├── vibe-curator.md
│   └── voice.md
├── skills/
│   ├── _index.md
│   ├── email/
│   │   ├── email-best-practices/
│   │   └── email-non-gmail-himalaya/
│   ├── social/
│   │   ├── x-auto-dm/
│   │   ├── x-thread/
│   │   ├── telegram/
│   │   ├── threads-bot/
│   │   └── reddit-bot/
│   ├── development/
│   │   ├── playwright/
│   │   ├── new-mcp-builder/
│   │   ├── new-skill/
│   │   └── new-skill-builder/
│   ├── productivity/
│   │   ├── google-workspace-gog/
│   │   ├── trello/
│   │   ├── weather/
│   │   ├── go-places/
│   │   ├── stream/
│   │   │   ├── SKILL.md
│   │   │   └── feeds.json
│   │   └── pulse/
│   ├── memory/
│   │   ├── obsidian/
│   │   ├── obsidian-memory/
│   │   ├── remember/
│   │   └── recall/
│   ├── agents/
│   │   ├── oracle/
│   │   ├── katana/
│   │   ├── vibe-curator/
│   │   └── installer/
│   │       └── SKILL.md
│   └── business/
│       ├── RentAHuman/
│       └── competitive-ads-extractor/
└── settings.json
```

**Verify with `tree agent/` and show me before proceeding.**

---

## PHASE 3: UPDATE ALL PATH REFERENCES

### Step 3A: Update src/utils.js (THE SINGLE SOURCE OF TRUTH)

Change from:
```javascript
const KATANA_HOME = path.join(os.homedir(), '.katana');
const MEMORY_DIR = path.join(KATANA_HOME, 'memory');
const VAULT_SKILLS_DIR = path.join(MEMORY_DIR, 'skills');
const COMMANDS_DIR = path.join(KATANA_HOME, 'commands');
```

To:
```javascript
// Resolve katana-agent repo root (works for npm link, global install, or local)
const KATANA_ROOT = path.resolve(__dirname, '..');
const AGENT_DIR = path.join(KATANA_ROOT, 'agent');
const MEMORY_DIR = path.join(AGENT_DIR, 'memory');
const VAULT_SKILLS_DIR = path.join(AGENT_DIR, 'skills');
const COMMANDS_DIR = path.join(AGENT_DIR, 'commands');
const SETTINGS_FILE = path.join(AGENT_DIR, 'settings.json');
```

Update exports to include `KATANA_ROOT`, `AGENT_DIR`, `SETTINGS_FILE`.

**IMPORTANT:** `__dirname` in `src/utils.js` = `katana-agent/src/`. So `path.resolve(__dirname, '..')` = `katana-agent/`. This works everywhere.

### Step 3B: Update src/memory.js

- Replace `KATANA_HOME` with `KATANA_ROOT` or `AGENT_DIR`
- Update display strings from `~/.katana/memory` to actual resolved path
- `initVault()`: since agent/memory/ ships pre-built, change to verify-and-report mode (check if files exist, create stubs if missing)

### Step 3C: Update src/skills.js

- Update display string for vault path
- Update "no skills" message from `~/.katana/memory/skills/` to `katana-agent/agent/skills/`

### Step 3D: Update src/init/claude.js

- Import `SETTINGS_FILE` instead of constructing settings path
- Change `vaultSettingsPath` from `path.join(MEMORY_DIR, 'settings.json')` to `SETTINGS_FILE`
- Update all console output strings referencing `~/.katana/`
- In `generateClaudeMd()`, update vault path references to `~/katana-agent/agent/memory/`
- **Rename all "sensei" references to "katana"** in generated output

### Step 3E: Update src/init/kilocode.js, codex.js, generic.js, universal.js

Same path updates as claude.js. Same sensei → katana rename.

### Step 3F: Update bin/katana.js

- Update help text paths
- Rename any sensei references to katana

### Step 3G: Update ALL template SKILL.md files

Every bundled skill that references the vault location must be updated:

```
templates/claude/skills/obsidian-memory/SKILL.md
templates/claude/skills/remember/SKILL.md
templates/claude/skills/recall/SKILL.md
templates/kilocode/skills/obsidian-memory/SKILL.md
templates/kilocode/skills/remember/SKILL.md
templates/kilocode/skills/recall/SKILL.md
templates/codex/skills/obsidian-memory/SKILL.md
templates/codex/skills/remember/SKILL.md
templates/codex/skills/recall/SKILL.md
templates/generic/skills/obsidian-memory/SKILL.md
templates/generic/skills/remember/SKILL.md
templates/generic/skills/recall/SKILL.md
templates/universal/skills/obsidian-memory/SKILL.md
templates/universal/skills/remember/SKILL.md
templates/universal/skills/recall/SKILL.md
```

In each: replace `~/.katana/memory/` with `~/katana-agent/agent/memory/`

### Step 3H: Global sensei → katana rename

```bash
# Find all remaining sensei references
grep -rn "sensei" ~/katana-agent/src/ ~/katana-agent/bin/ ~/katana-agent/templates/ ~/katana-agent/agent/ --include='*.js' --include='*.md' --include='*.json'

# Replace all with katana (case-sensitive)
# /sensei → /katana
# sensei.md → katana.md
# Agents: /sensei → Agents: /katana
```

**Show me all planned path changes before executing. Confirm with me.**

---

## PHASE 4: UPDATE PACKAGE.JSON

```json
{
  "name": "katana-agent",
  "version": "1.1.0",
  "description": "Install your AI agent into any project. Self-hosted, private, model-agnostic. Centralized Obsidian memory across Claude Code, Codex, Gemini, Cursor & more.",
  "author": "Shane Swrld",
  "license": "SEE LICENSE IN LICENSE",
  "main": "src/utils.js",
  "bin": {
    "katana": "./bin/katana.js"
  },
  "files": [
    "bin/",
    "src/",
    "agent/",
    "templates/",
    "setup.sh",
    "README.md",
    "LICENSE"
  ],
  "scripts": {
    "test": "node bin/katana.js",
    "setup": "bash setup.sh"
  },
  "keywords": [
    "ai-agent", "cli", "obsidian", "claude-code", "codex",
    "cursor", "skills", "memory", "self-hosted", "developer-tools"
  ],
  "repository": {
    "type": "git",
    "url": "git+https://github.com/shane9coy/katana-agent.git"
  },
  "homepage": "https://github.com/shane9coy/katana-agent",
  "engines": { "node": ">=18.0.0" },
  "dependencies": {
    "chalk": "^4.1.2",
    "commander": "^12.1.0"
  }
}
```

Key: `"files"` includes `"agent/"` and `"setup.sh"` — these ship with npm publish.

---

## PHASE 5: UPDATE README.md

The README must reflect V1.1 with:
- All paths updated to `~/katana-agent/agent/`
- `/katana` as the master agent (not /sensei)
- `/stream` news agent documented
- `setup.sh` in the Quick Start
- Installer skill mentioned
- Architecture diagram showing the self-contained structure
- 27 skills across 7 categories listed

---

## PHASE 6: UPDATE .gitignore

```
node_modules/
.DS_Store
agent/memory/.obsidian/
agent/skills/**/.DS_Store
agent/skills/**/__pycache__/
agent/skills/**/*.pyc
agent/skills/**/.env
*.log
```

Note: `.env` files inside skill folders (API keys) are gitignored — they contain secrets.

---

## PHASE 7: TEST EVERYTHING

### 7A: katana with no args
```bash
node bin/katana.js
```
Should show help with correct paths, `/katana` in agent list.

### 7B: katana memory status
```bash
node bin/katana.js memory status
```
Should find vault at `agent/memory/`.

### 7C: katana skills list
```bash
node bin/katana.js skills list
```
Should list all 27 skills by category from `agent/skills/`.

### 7D: katana claude init (from a test project)
```bash
mkdir /tmp/test-v11 && cd /tmp/test-v11
echo '{"name":"test","dependencies":{"react":"18"}}' > package.json
node ~/katana-agent/bin/katana.js claude init --all
```

Verify:
- `.claude/CLAUDE.md` references `~/katana-agent/agent/memory/`
- `.claude/commands/katana.md` exists (not sensei.md)
- `.claude/skills/` has skills from `agent/skills/`
- `.claude/settings.json` from `agent/settings.json`
- Project registered in `agent/memory/projects/test/`

### 7E: No sensei references remain
```bash
grep -r "sensei" ~/katana-agent/ --include='*.js' --include='*.md' --include='*.json' --exclude-dir=node_modules --exclude-dir=.git
```
Should return nothing.

### 7F: No ~/.katana/ references remain
```bash
grep -r '\.katana/' ~/katana-agent/src/ ~/katana-agent/bin/ ~/katana-agent/templates/ --include='*.js' --include='*.md'
```
Should return nothing.

### 7G: setup.sh works
```bash
bash ~/katana-agent/setup.sh
```
Should complete successfully, list all agents and skills.

### 7H: npm link and global test
```bash
cd ~/katana-agent
npm unlink -g katana-agent 2>/dev/null
npm link
katana
```
Should work from any directory.

**Run all tests. Fix any failures. Show me results.**

---

## PHASE 8: CLEANUP

### 8A: Remove orphaned files
```bash
find ~/katana-agent -name '.DS_Store' -delete
find ~/katana-agent -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null
find ~/katana-agent -name '*.pyc' -delete
```

### 8B: Verify no old references
```bash
grep -r '\.katana/' ~/katana-agent/src/ ~/katana-agent/bin/ ~/katana-agent/templates/ --include='*.js' --include='*.md'
grep -r "sensei" ~/katana-agent/ --include='*.js' --include='*.md' --include='*.json' --exclude-dir=node_modules --exclude-dir=.git
```

### 8C: Back up ~/.katana/ (DO NOT DELETE YET)
```bash
mv ~/.katana ~/.katana.backup-$(date +%s)
```

Only after V1.1 is fully verified.

---

## EXECUTION ORDER

1. **AUDIT** (Phase 1) → Show report, wait for confirmation
2. **CREATE agent/** (Phase 2) → Copy files, organize skills, verify structure, wait for confirmation
3. **UPDATE PATHS** (Phase 3) → Show all changes, wait for confirmation, execute
4. **UPDATE package.json** (Phase 4)
5. **UPDATE README** (Phase 5)
6. **UPDATE .gitignore** (Phase 6)
7. **TEST** (Phase 7) → Run all tests, show results
8. **CLEANUP** (Phase 8)

**Stop at each phase boundary and confirm with the user.**

---

## CRITICAL RULES

1. **DO NOT delete `~/.katana/` until user confirms V1.1 works.** Keep it as backup.
2. **`src/utils.js` is the single source of truth for all paths.** All other files import from there.
3. **`__dirname` trick is essential.** `path.resolve(__dirname, '..')` resolves to katana-agent root regardless of install method.
4. **Template SKILL.md files use human-readable paths** (`~/katana-agent/agent/memory/`) because agents read them and use bash to access files.
5. **`agent/` ships with npm publish.** The `"files"` array in package.json MUST include `"agent/"`. Verify with `npm pack --dry-run`.
6. **Skills at `agent/skills/`, NOT `agent/memory/skills/`.** Memory is memory. Skills are skills. Separate.
7. **`/katana` is the master agent. NOT `/sensei`.** Every reference must be updated.
8. **Test from a DIFFERENT directory** to verify path resolution works.
9. **API keys go in `.env` files inside skill folders, NOT in memory files or committed to git.**
