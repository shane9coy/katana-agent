const fs = require('fs');
const path = require('path');
const readline = require('readline');
const chalk = require('chalk');
const { checkConflict } = require('../conflict');
const { pickInstallItems } = require('../picker');
const { copyDirRecursive, ensureDir, detectProjectStack, getVaultSkills, getVaultCategories, getVaultCommands, MEMORY_DIR, COMMANDS_DIR } = require('../utils');

async function init(opts) {
  // Gemini uses both .gemini/ (official) and .agents/ (preferred alias)
  const agentsDir = path.join(process.cwd(), '.agents');
  const geminiDir = path.join(process.cwd(), '.gemini');
  const templateAgentsDir = path.join(__dirname, '../../templates/gemini/.agents');
  const templateGeminiDir = path.join(__dirname, '../../templates/gemini/.gemini');

  console.log('');
  console.log(chalk.bold('⚡ Katana Agent → Gemini CLI'));
  console.log('');
  console.log(chalk.dim('  Setting up .agents/ and .gemini/ folders'));
  console.log('');

  // ─── Conflict Detection for .agents/ ───────────────────────────
  let action = 'fresh';

  if (fs.existsSync(agentsDir)) {
    action = await checkConflict('.agents');
    if (action === 'cancel') { console.log(chalk.dim('  Cancelled.')); return; }
    if (action === 'backup') {
      const backupName = `.agents.backup-${Date.now()}`;
      fs.renameSync(agentsDir, path.join(process.cwd(), backupName));
      console.log(chalk.green(`  ✓ Backed up .agents/ → ${backupName}`));
    }
    if (action === 'replace') {
      fs.rmSync(agentsDir, { recursive: true, force: true });
      console.log(chalk.green('  ✓ Removed existing .agents/'));
    }
  }

  // Check .gemini/ for conflict info only (we don't delete it)
  if (fs.existsSync(geminiDir)) {
    console.log(chalk.dim('  → Using existing .gemini/ (keeping as-is)'));
  }

  const overwrite = action !== 'merge';

  // ─── Copy .agents/ template (preferred location) ───────────────
  if (fs.existsSync(templateAgentsDir)) {
    copyDirRecursive(templateAgentsDir, agentsDir, { overwrite });
  }

  // ─── Copy .gemini/ template (official config) ─────────────────
  let geminiOverwrite = overwrite;
  if (fs.existsSync(geminiDir) && !overwrite) {
    // Merge mode: don't overwrite existing settings.json
    copyDirRecursive(templateGeminiDir, geminiDir, { overwrite: false, skip: ['settings.json'] });
  } else if (!fs.existsSync(geminiDir)) {
    // Fresh install
    ensureDir(geminiDir);
    if (fs.existsSync(templateGeminiDir)) {
      copyDirRecursive(templateGeminiDir, geminiDir, { overwrite: true });
    }
  }

  // ─── Settings.json Prompt ─────────────────────────────────────
  const settingsPath = path.join(geminiDir, 'settings.json');
  const vaultSettingsPath = path.join(MEMORY_DIR, 'settings.json');
  const templateSettingsPath = path.join(templateGeminiDir, 'settings.json');

  // Source priority: vault > bundled template
  const settingsSource = fs.existsSync(vaultSettingsPath) ? vaultSettingsPath : templateSettingsPath;
  const sourceLabel = fs.existsSync(vaultSettingsPath) ? '~/.katana/memory/settings.json' : 'bundled default';

  if (fs.existsSync(settingsPath) && action === 'merge') {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    const answer = await new Promise(resolve => {
      rl.question(chalk.white(`  Install settings.json from ${sourceLabel}? (y/N): `), resolve);
    });
    rl.close();

    if (answer.trim().toLowerCase() === 'y') {
      fs.copyFileSync(settingsSource, settingsPath);
      console.log(chalk.green(`  ✓ Installed settings.json (${sourceLabel})`));
    } else {
      console.log(chalk.dim('  → Kept existing settings.json'));
    }
  } else if (!fs.existsSync(settingsPath) || overwrite) {
    if (fs.existsSync(settingsSource)) {
      fs.copyFileSync(settingsSource, settingsPath);
      console.log(chalk.green(`  ✓ Installed settings.json (${sourceLabel})`));
    }
  }

  // ─── Interactive Picker (unless --all or --minimal) ───────────
  const categories = getVaultCategories();
  const userCommands = getVaultCommands();
  const vaultSkills = getVaultSkills();

  let selectedCategories = categories.map(c => c.name);
  let selectedCommands = userCommands.map(c => c.name);

  if (opts.minimal) {
    selectedCategories = [];
    selectedCommands = [];
    console.log(chalk.dim('  → Minimal mode: bundled skills only'));
  } else if (!opts.all && (categories.length > 0 || userCommands.length > 0)) {
    const selections = await pickInstallItems(categories, userCommands);
    selectedCategories = selections.categories;
    selectedCommands = selections.commands;
  } else if (opts.all) {
    console.log(chalk.dim('  → All mode: installing everything'));
  }

  // ─── Install Selected Commands ────────────────────────────────
  // Commands go to .agents/agents/ (sub-agents) and .gemini/commands/
  if (fs.existsSync(COMMANDS_DIR) && selectedCommands.length > 0) {
    // .agents/agents/ for sub-agents
    const agentsAgentsDir = path.join(agentsDir, 'agents');
    ensureDir(agentsAgentsDir);
    
    // .gemini/commands/ for slash commands
    const commandsTarget = path.join(geminiDir, 'commands');
    ensureDir(commandsTarget);

    const userCommandsAll = fs.readdirSync(COMMANDS_DIR).filter(f => f.endsWith('.md'));
    let agentCount = 0;
    let commandCount = 0;

    for (const file of userCommandsAll) {
      const cmdName = file.replace('.md', '');
      if (!selectedCommands.includes(cmdName)) continue;

      // Copy to .agents/agents/ as sub-agent
      const agentDest = path.join(agentsAgentsDir, file);
      if (!overwrite && !fs.existsSync(agentDest)) {
        fs.copyFileSync(path.join(COMMANDS_DIR, file), agentDest);
        agentCount++;
      } else if (overwrite) {
        fs.copyFileSync(path.join(COMMANDS_DIR, file), agentDest);
        agentCount++;
      }

      // Copy to .gemini/commands/ as command
      const cmdDest = path.join(commandsTarget, file);
      if (!overwrite && !fs.existsSync(cmdDest)) {
        fs.copyFileSync(path.join(COMMANDS_DIR, file), cmdDest);
        commandCount++;
      } else if (overwrite) {
        fs.copyFileSync(path.join(COMMANDS_DIR, file), cmdDest);
        commandCount++;
      }
    }

    if (agentCount > 0) {
      console.log(chalk.green(`  ✓ Loaded ${agentCount} agent(s) to .agents/agents/`));
    }
    if (commandCount > 0) {
      console.log(chalk.green(`  ✓ Loaded ${commandCount} command(s) to .gemini/commands/`));
    }
  }

  // ─── Install Selected Skill Categories ────────────────────────
  // Skills go to .agents/skills/ (highest precedence)
  if (selectedCategories.length > 0) {
    const skillsTarget = path.join(agentsDir, 'skills');
    ensureDir(skillsTarget);
    let skillCount = 0;
    for (const skill of vaultSkills) {
      if (!selectedCategories.includes(skill.category)) continue;
      const dest = path.join(skillsTarget, skill.name);
      if (!overwrite && fs.existsSync(dest)) continue;
      copyDirRecursive(skill.path, dest, { overwrite: true });
      skillCount++;
    }
    if (skillCount > 0) {
      console.log(chalk.green(`  ✓ Synced ${skillCount} skill(s) from Obsidian vault to .agents/skills/`));
    }
  }

  // ─── Generate GEMINI.md ──────────────────────────────────────
  const project = detectProjectStack();
  const geminiMdPath = path.join(geminiDir, 'GEMINI.md');
  if (overwrite || !fs.existsSync(geminiMdPath)) {
    const geminiMd = generateGeminiMd(project);
    fs.writeFileSync(geminiMdPath, geminiMd);
    console.log(chalk.green(`  ✓ Generated GEMINI.md (detected: ${project.stack})`));
  }

  // ─── Generate .geminiignore ───────────────────────────────────
  const ignorePath = path.join(process.cwd(), '.geminiignore');
  if (overwrite || !fs.existsSync(ignorePath)) {
    fs.writeFileSync(ignorePath, `# Gemini CLI ignore patterns
# Dependencies
node_modules/
vendor/
dist/
build/

# Environment
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*

# Cache
.cache/
.turbo/
coverage/
.nyc_output/

# Test
__pycache__/
*.pyc
`);
    console.log(chalk.green('  ✓ Created .geminiignore'));
  }

  // ─── Register Project in Obsidian Vault ──────────────────────
  registerProject(project.name);

  // ─── Summary ─────────────────────────────────────────────────
  const agentsSkillsDir = path.join(agentsDir, 'skills');
  const agentSkillsCount = fs.existsSync(agentsSkillsDir)
    ? fs.readdirSync(agentsSkillsDir, { withFileTypes: true }).filter(d => d.isDirectory()).length
    : 0;

  const agentsAgentsCount = fs.existsSync(path.join(agentsDir, 'agents'))
    ? fs.readdirSync(path.join(agentsDir, 'agents')).filter(f => f.endsWith('.md')).length
    : 0;

  const geminiCommandsCount = fs.existsSync(path.join(geminiDir, 'commands'))
    ? fs.readdirSync(path.join(geminiDir, 'commands')).filter(f => f.endsWith('.md')).length
    : 0;

  console.log('');
  console.log(chalk.bold.green('  ✓ Katana agent initialized for Gemini CLI'));
  console.log('');
  console.log(chalk.dim('  .agents/skills:    ') + chalk.white(`${agentSkillsCount} installed`));
  console.log(chalk.dim('  .agents/agents:    ') + chalk.white(`${agentsAgentsCount} installed`));
  console.log(chalk.dim('  .gemini/commands:  ') + chalk.white(`${geminiCommandsCount} installed`));
  console.log(chalk.dim('  Memory:            ') + chalk.white('~/.katana/memory/ (Obsidian vault)'));
  console.log('');
  console.log(chalk.dim('  Usage: Open this project in Gemini CLI — your agent is ready.'));
  console.log(chalk.dim('  Note: .agents/ takes precedence over .gemini/ for skills'));
  console.log('');
}

function generateGeminiMd(project) {
  return `# ${project.name}

## Stack
${project.stack}
${project.commands ? `\n## Available Commands\n${project.commands.split(', ').map(c => '- `' + c + '`').join('\n')}` : ''}

## Agent
This project uses **Katana Agent**. Memory is stored in \`~/.katana/memory/\` (Obsidian vault).

On session start, read:
- \`~/.katana/memory/core/soul.md\` — your identity and behavior
- \`~/.katana/memory/core/user.md\` — facts about the user
- Check \`~/.katana/memory/projects/${project.name}/\` for project history (if it exists)

## Code Conventions
- (add your project conventions here)

## Notes
- Use \`/remember\` to save session context to memory
- Use \`/recall\` to search past sessions and project history
- Skills available in \`.agents/skills/\` — check what's installed before solving complex problems
- Check \`.gemini/settings.json\` for model and tool configuration
`;
}

function registerProject(projectName) {
  const projectDir = path.join(MEMORY_DIR, 'projects', projectName);
  if (!fs.existsSync(MEMORY_DIR)) return;
  if (!fs.existsSync(projectDir)) {
    ensureDir(projectDir);
    fs.writeFileSync(path.join(projectDir, 'sessions.md'), `---
project: ${projectName}
created: ${new Date().toISOString().split('T')[0]}
tags: [project]
---

# ${projectName} — Session History

<!-- Agent appends session summaries here. Newest at top. -->

## ${new Date().toISOString().split('T')[0]} — Project initialized
Katana Agent initialized for this project.
`);
    console.log(chalk.green(`  ✓ Registered project in Obsidian vault → projects/${projectName}/`));
  }
}

module.exports = { init };
