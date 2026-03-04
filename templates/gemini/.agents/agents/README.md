# Custom Sub-Agents

This directory contains custom sub-agents that can be invoked for specialized tasks.

## Structure

Each agent is a markdown file with the agent's definition:

```
.frontend-specialist.md
.tester-agent.md
```

## Usage

Sub-agents can be invoked using Gemini CLI's multi-agent features.
Commands from `~/.katana/commands/` are automatically synced here.

## Synced Commands

Commands are also copied to `.gemini/commands/` for slash command access.
