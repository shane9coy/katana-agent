# Katana Central .env Implementation Plan

## Goal
Implement a central `.env` file for Katana (like Hermes `~/.hermes/.env`) to store all API keys in one place, with skills referencing this central file.

## Current State
- Katana stores API keys in individual skill folders: `agent/skills/social/x-auto-dm/.env`
- No central .env file at `agent/.env`
- Installer skill writes keys to individual skill folders

## Proposed Structure

```
~/.katana/
├── .env                  # NEW: Central API keys (source of truth)
├── settings.json         # Agent permissions & MCP config
├── commands/             # Agent commands
├── AGENT.md              # Shared root agent instructions
└── memory/               # Obsidian vault
    └── skills/           # Skills (read .env from parent)
```

## Implementation Steps

### 1. Create Central .env Template
File: `agent/.env.example`
```bash
# Katana Agent - Central Environment Variables
# Copy to agent/.env and fill in your keys

# Core
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=

# Social
X_API_KEY=
TELEGRAM_BOT_TOKEN=

# Services
GOOGLE_PLACES_API_KEY=
FIRECRAWL_API_KEY=

# etc.
```

### 2. Update new-skill-builder Template
Add a section in Workflow 1 for skills that need API keys:

```markdown
## API Keys for Your Skill

If your skill requires API keys, use the central .env file instead of creating
a separate .env in the skill folder.

**Central location:** `~/.katana/.env`

Example - instead of creating `skill-folder/.env`:
```bash
# WRONG - individual skill .env
echo "API_KEY=xxx" > .claude/skills/my-skill/.env
```

Do this instead:
```bash
# CORRECT - add to central .env
echo "MY_SKILL_API_KEY=xxx" >> ~/.katana/.env
```

Then in your skill code, read from the central location:
```python
import os
from pathlib import Path

# Read from central .env
CENTRAL_ENV = Path.home() / "katana-agent" / "agent" / ".env"
from dotenv import load_dotenv
load_dotenv(CENTRAL_ENV)

api_key = os.getenv("MY_SKILL_API_KEY")
```

### 2. Update Installer Skill
File: `agent/skills/agents/installer/SKILL.md`

Change from:
```bash
# Write to skill folder
echo "X_BEARER_TOKEN=..." > ~/.katana/memory/skills/social/x-auto-dm/.env
```

To:
```bash
# Write to central .env
echo "X_BEARER_TOKEN=..." >> ~/.katana/.env
```

### 3. Add .env Loading Logic
Create utility in `src/utils.js` to help skills read from central .env:

```javascript
function getEnvVar(key) {
  // Priority: individual skill .env > central agent/.env > process.env
}
```

### 4. Update Existing Skills
Modify skills to check central .env first:

Current:
```python
# x-auto-dm skill
from dotenv import load_dotenv
load_dotenv('./.env')
```

Updated:
```python
# Check skill folder first, then central location
load_dotenv(os.path.expanduser('~/.katana/.env'))
```

### 5. Setup Wizard Enhancement
Add to installer skill - new step for central .env:

```
## Step 3b: Central .env Setup

We can store all your API keys in one central location instead of
individual skill folders. This makes it easier to manage keys.

[Create new central .env] [Use existing skill folders]
```

## Migration Path
1. New users: Start with central .env
2. Existing users: Option to migrate from skill folders to central .env
3. Backward compatibility: Skills check both locations

## Benefits
- Single place to manage all API keys
- Easier backup/restore
- Consistent with Hermes approach
- Skills can share common keys

## Hermes Features to Consider Later
- Model/provider selection (OpenRouter, Anthropic, etc.)
- Terminal backend (local, Docker, Modal)
- Session reset policies
- Messaging platform integration

## Files to Modify
1. `agent/.env.example` (new)
2. `agent/skills/agents/installer/SKILL.md` (update - optional central .env setup)
3. `agent/skills/agent-tools/new-skill-builder/SKILL.md` (update - new skills reference central .env)
4. `src/utils.js` (add env loading helpers)
5. Individual skills (gradual migration - NOT required)

## Implementation Approach

### Option A: Update new-skill-builder only (Recommended)
- Don't modify existing skills
- Update new-skill-builder to tell new skills to use central .env
- Installer can set up central .env later if needed

### Option B: Migrate all existing skills
- Update all existing skills to check central .env
- More work, but consistent

**We'll implement Option A** - Update new-skill-builder to guide new skills to use central .env for API keys, and let installer handle setup later.

## Priority
1. Create .env.example template
2. Update new-skill-builder template with .env instructions
3. Add utility functions for reading central .env
4. (Optional) Installer can offer to set up central .env
