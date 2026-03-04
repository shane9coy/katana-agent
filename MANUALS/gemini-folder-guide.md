# Gemini CLI Folder Structure Guide (March 2026)

Here's the proper .agents / .gemini folder structure for Gemini CLI (official Google open-source terminal AI agent, as of March 2026).
Gemini CLI's main config folder is .gemini/, but it officially supports .agents/ as a preferred alias — especially for skills and agent-related files.
.agents/skills/ takes precedence over .gemini/skills/ (so use .agents/ for anything new/agent-focused). This makes it feel more "agent-native" and future-proof across tools.
Recommended Full Project Tree (copy-paste ready)
Bashyour-project/                          # ← Git repo root (commit most of this!)
├── GEMINI.md                          # Project context + instructions (loaded first)
├── .geminiignore                      # Ignore patterns (like .gitignore for the agent)
├── .gemini/                           # Official core config dir
│   ├── settings.json                  # ★ Most important: project settings, models, MCP, sandbox
│   ├── .env                           # Project env vars (API keys, etc.)
│   ├── commands/                      # Custom slash commands (/plan, /deploy, etc.)
│   │   ├── plan.toml
│   │   └── deploy/
│   │       └── prod.toml
│   ├── skills/                        # Legacy skills location
│   └── sandbox.Dockerfile             # Custom secure sandbox (optional)
│
├── .agents/                           # ← Preferred alias for agent stuff (recommended!)
│   ├── skills/                        # Agent Skills — highest precedence
│   │   ├── code-review/
│   │   │   ├── SKILL.md               # Instructions + metadata
│   │   │   ├── workflow.sh
│   │   │   └── examples/
│   │   └── security-scan/
│   │       └── SKILL.md
│   └── agents/                        # Custom sub-agents / multi-agent orchestration
│       ├── frontend-specialist.md
│       ├── tester-agent.md
│       └── tasks/                     # Task queue (popular community pattern)
│           └── backlog.json
│
└── (your actual source code...)
Global / User-Level Version (in your home folder)
Bash~/.agents/          # ← Preferred
or
~/.gemini/
    ├── settings.json
    ├── GEMINI.md          # Global instructions that apply to ALL projects
    ├── commands/
    └── skills/
Quick Explanation of Each Part



Folder/FileWhat it doesCommit to Git?LevelGEMINI.mdPersistent system prompt / coding standards / project rulesYesProject + Global.gemini/settings.jsonModel choice, tools, sandbox, experimental agents, MCP serversUsually yesProject.agents/skills/Reusable "skills" (specialized expertise the agent loads on-demand)YesProject.gemini/commands/Custom slash commands (e.g. /plan that only plans changes)YesProject.agents/agents/Custom sub-agents / specialist agents (experimental but very popular)YesProject.geminiignoreFiles/folders the agent should ignoreYesProject
Why .agents/ exists

It's an official alias introduced for better compatibility with the "Agent Skills" open standard.
Inside the same tier (project or user), .agents/ wins over .gemini/.
Feels cleaner when you’re building multi-agent workflows.