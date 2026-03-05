# Agent Skills

This directory contains Katana Agent skills installed from your Obsidian vault.

Skills are loaded on-demand when you reference them in your prompts.

## Structure

Each skill should be in its own folder with a `SKILL.md` file:

```
.skill-name/
├── SKILL.md        # Required: skill definition
├── workflow.sh     # Optional: automation script
└── examples/       # Optional: example prompts
```

## Available Skills

Skills are synced from `~/katana-agent/agent/memory/skills/` during initialization.
Run `katana skills sync` to update.
