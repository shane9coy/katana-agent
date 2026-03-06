const fs = require('fs');
const path = require('path');
const readline = require('readline');
const chalk = require('chalk');
const { checkConflict } = require('../conflict');
const { pickInstallItems } = require('../picker');
const { copyDirRecursive, ensureDir, detectProjectStack, getVaultSkills, getVaultCategories, getVaultCommands, MEMORY_DIR, COMMANDS_DIR, SETTINGS_FILE } = require('../utils');

async function init(opts) {
  const targetDir = path.join(process.cwd(), '.codex');
  const templateDir = path.join(__dirname, '../../templates/codex');

  console.log('');
  console.log(chalk.bold('⚡ Katana Agent → Codex'));
  console.log('');

  let action = 'fresh';

  if (fs.existsSync(targetDir)) {
    action = await checkConflict('.codex');
    if (action === 'cancel') { console.log(chalk.dim('  Cancelled.')); return; }
    if (action === 'backup') {
      const backupName = `.codex.backup-${Date.now()}`;
      fs.renameSync(targetDir, path.join(process.cwd(), backupName));
      console.log(chalk.green(`  ✓ Backed up → ${backupName}`));
    }
    if (action === 'replace') {
      fs.rmSync(targetDir, { recursive: true, force: true });
      console.log(chalk.green('  ✓ Removed existing .codex/'));
    }
  }

  const overwrite = action !== 'merge';
  copyDirRecursive(templateDir, targetDir, { overwrite });

  // ─── Settings.json Prompt ───────────────────────────────
  const settingsPath = path.join(targetDir, 'settings.json');
  const settingsSource = SETTINGS_FILE;
  const sourceLabel = '~/katana-agent/agent/settings.json';

  if (fs.existsSync(settingsPath) && action === 'merge') {
    // Existing settings — ask before overwriting
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
    fs.copyFileSync(settingsSource, settingsPath);
    console.log(chalk.green(`  ✓ Installed settings.json (${sourceLabel})`));
  }

  // Sync vault skills (with interactive picker unless --all or --minimal)
  const categories = getVaultCategories();
  const userCommands = getVaultCommands();
  const vaultSkills = getVaultSkills();

  let selectedCategories = categories.map(c => c.name);
  let selectedCommands = userCommands.map(c => c.name);

  if (opts.minimal) {
    // --minimal: skip vault skills and commands, bundled only
    selectedCategories = [];
    selectedCommands = [];
    console.log(chalk.dim('  → Minimal mode: bundled skills only'));
  } else if (!opts.all && (categories.length > 0 || userCommands.length > 0)) {
    // Interactive picker
    const selections = await pickInstallItems(categories, userCommands);
    selectedCategories = selections.categories;
    selectedCommands = selections.commands;
  } else if (opts.all) {
    console.log(chalk.dim('  → All mode: installing everything'));
  }

  // Copy commands from ~/katana-agent/agent/commands/
  if (fs.existsSync(COMMANDS_DIR) && selectedCommands.length > 0) {
    const commandsTarget = path.join(targetDir, 'commands');
    ensureDir(commandsTarget);
    const userCommandsAll = fs.readdirSync(COMMANDS_DIR).filter(f => f.endsWith('.md'));
    let commandCount = 0;
    for (const file of userCommandsAll) {
      const cmdName = file.replace('.md', '');
      if (!selectedCommands.includes(cmdName)) continue;
      const dest = path.join(commandsTarget, file);
      if (!overwrite && fs.existsSync(dest)) continue;
      fs.copyFileSync(path.join(COMMANDS_DIR, file), dest);
      commandCount++;
    }
    if (commandCount > 0) {
      console.log(chalk.green(`  ✓ Loaded ${commandCount} command(s) from ~/katana-agent/agent/commands/`));
    }
  }

  // Install selected skill categories
  if (selectedCategories.length > 0) {
    const skillsTarget = path.join(targetDir, 'skills');
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
      console.log(chalk.green(`  ✓ Synced ${skillCount} skill(s) from Obsidian vault`));
    }
  }

  // Generate AGENTS.md (Codex native format)
  const agentsMdPath = path.join(targetDir, 'AGENTS.md');
  if (overwrite || !fs.existsSync(agentsMdPath)) {
    const project = detectProjectStack();
    fs.writeFileSync(agentsMdPath, generateAgentsMd(project));
    console.log(chalk.green(`  ✓ Generated AGENTS.md (detected: ${project.stack})`));
  }

  // Register project in vault
  const project = detectProjectStack();
  registerProject(project.name);

  const skillsDir = path.join(targetDir, 'skills');
  const skillCount = fs.existsSync(skillsDir)
    ? fs.readdirSync(skillsDir, { withFileTypes: true }).filter(d => d.isDirectory()).length
    : 0;
  const commandsDir = path.join(targetDir, 'commands');
  const commandCount = fs.existsSync(commandsDir)
    ? fs.readdirSync(commandsDir).filter(f => f.endsWith('.md')).length
    : 0;

  console.log('');
  console.log(chalk.bold.green('  ✓ Katana agent initialized in .codex/'));
  console.log('');
  console.log(chalk.dim('  Commands: ') + chalk.white(`${commandCount} installed`));
  console.log(chalk.dim('  Skills:   ') + chalk.white(`${skillCount} installed`));
  console.log(chalk.dim('  Memory:   ') + chalk.white('~/katana-agent/agent/memory/ (Obsidian vault)'));
  console.log('');
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

## ${new Date().toISOString().split('T')[0]} — Project initialized
Katana Agent initialized for this project.
`);
    console.log(chalk.green(`  ✓ Registered project → projects/${projectName}/`));
  }
}

function generateAgentsMd(project) {
  return `# ${project.name}

## Stack
${project.stack}

## Agent
This project uses **Katana Agent**. Memory: \`~/katana-agent/agent/memory/\` (Obsidian vault).

On session start, read:
- \`~/katana-agent/agent/memory/core/soul.md\` — agent identity
- \`~/katana-agent/agent/memory/core/user.md\` — user context

## Conventions
- (add your conventions here)
`;
}

module.exports = { init };
