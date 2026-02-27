const fs = require('fs');
const path = require('path');
const readline = require('readline');
const chalk = require('chalk');
const { checkConflict } = require('../conflict');
const { pickInstallItems } = require('../picker');
const { copyDirRecursive, ensureDir, detectProjectStack, getVaultSkills, getVaultCategories, getVaultCommands, MEMORY_DIR, COMMANDS_DIR } = require('../utils');

async function init(opts) {
  const targetDir = path.join(process.cwd(), '.claude');
  const templateDir = path.join(__dirname, '../../templates/claude');

  console.log('');
  console.log(chalk.bold('⚡ Katana Agent → Claude Code'));
  console.log('');

  // ─── Conflict Detection ──────────────────────────────────
  let action = 'fresh';

  if (fs.existsSync(targetDir)) {
    action = await checkConflict('.claude');

    if (action === 'cancel') {
      console.log(chalk.dim('  Cancelled.'));
      return;
    }

    if (action === 'backup') {
      const backupName = `.claude.backup-${Date.now()}`;
      fs.renameSync(targetDir, path.join(process.cwd(), backupName));
      console.log(chalk.green(`  ✓ Backed up existing .claude/ → ${backupName}`));
    }

    if (action === 'replace') {
      fs.rmSync(targetDir, { recursive: true, force: true });
      console.log(chalk.green('  ✓ Removed existing .claude/'));
    }
  }

  const overwrite = action !== 'merge';

  // ─── Copy Template (base structure, WITHOUT settings.json) ──
  copyDirRecursive(templateDir, targetDir, { overwrite, skip: ['settings.json'] });

  // ─── Settings.json Prompt ───────────────────────────────
  const settingsPath = path.join(targetDir, 'settings.json');
  const vaultSettingsPath = path.join(MEMORY_DIR, 'settings.json');
  const templateSettingsPath = path.join(templateDir, 'settings.json');

  // Source priority: vault > bundled template
  const settingsSource = fs.existsSync(vaultSettingsPath) ? vaultSettingsPath : templateSettingsPath;
  const sourceLabel = fs.existsSync(vaultSettingsPath) ? '~/.katana/memory/settings.json' : 'bundled default';

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

  // ─── Interactive Picker (unless --all or --minimal) ─────
  const categories = getVaultCategories();
  const userCommands = getVaultCommands();

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

  // ─── Install Selected Commands ──────────────────────────
  const commandsTarget = path.join(targetDir, 'commands');
  ensureDir(commandsTarget);

  let commandCount = 0;
  for (const cmd of userCommands) {
    if (!selectedCommands.includes(cmd.name)) continue;
    const dest = path.join(commandsTarget, cmd.name + '.md');
    if (!overwrite && fs.existsSync(dest)) continue;
    fs.copyFileSync(cmd.path, dest);
    commandCount++;
  }

  if (commandCount > 0) {
    console.log(chalk.green(`  ✓ Loaded ${commandCount} command(s) from ~/.katana/commands/`));
  }

  // ─── Install Selected Skill Categories ──────────────────
  const skillsTarget = path.join(targetDir, 'skills');
  ensureDir(skillsTarget);

  let skillCount = 0;
  const allSkills = getVaultSkills();

  for (const skill of allSkills) {
    if (!selectedCategories.includes(skill.category)) continue;
    const dest = path.join(skillsTarget, skill.name);
    if (!overwrite && fs.existsSync(dest)) continue;
    copyDirRecursive(skill.path, dest, { overwrite: true });
    skillCount++;
  }

  if (skillCount > 0) {
    console.log(chalk.green(`  ✓ Synced ${skillCount} skill(s) from Obsidian vault`));
  }

  // ─── Detect Project ──────────────────────────────────────
  const project = detectProjectStack();

  // ─── Generate CLAUDE.md ──────────────────────────────────
  const claudeMdPath = path.join(targetDir, 'CLAUDE.md');
  if (overwrite || !fs.existsSync(claudeMdPath)) {
    const claudeMd = generateClaudeMd(project);
    fs.writeFileSync(claudeMdPath, claudeMd);
    console.log(chalk.green(`  ✓ Generated CLAUDE.md (detected: ${project.stack})`));
  } else {
    console.log(chalk.dim('  → Kept existing CLAUDE.md (merge mode)'));
  }

  // ─── Register Project in Obsidian Vault ──────────────────
  registerProject(project.name);

  // ─── Summary ─────────────────────────────────────────────
  const totalSkills = fs.existsSync(skillsTarget)
    ? fs.readdirSync(skillsTarget, { withFileTypes: true }).filter(d => d.isDirectory()).length
    : 0;
  const totalCommands = fs.existsSync(commandsTarget)
    ? fs.readdirSync(commandsTarget).filter(f => f.endsWith('.md')).length
    : 0;
  const installedAgents = fs.existsSync(commandsTarget)
    ? fs.readdirSync(commandsTarget).filter(f => f.endsWith('.md')).map(f => '/' + f.replace('.md', ''))
    : [];

  console.log('');
  console.log(chalk.bold.green('  ✓ Katana agent initialized in .claude/'));
  console.log('');
  console.log(chalk.dim('  Commands: ') + chalk.white(`${totalCommands} installed`));
  console.log(chalk.dim('  Skills:   ') + chalk.white(`${totalSkills} installed`));
  console.log(chalk.dim('  Memory:   ') + chalk.white('~/.katana/memory/ (Obsidian vault)'));
  console.log('');
  console.log(chalk.dim('  Usage: Open this project in Claude Code — your agent is ready.'));
  if (installedAgents.length > 0) {
    console.log(chalk.dim('  Agents: ') + chalk.cyan(installedAgents.join(', ')));
  }
  console.log(chalk.dim('  Memory: /remember to save, /recall to search'));
  console.log('');
}

function generateClaudeMd(project) {
  return `# ${project.name}

## Stack
${project.stack}
${project.commands ? `\n## Available Commands\n${project.commands.split(', ').map(c => '- \`' + c + '\`').join('\n')}` : ''}

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
- Skills available in \`.claude/skills/\` — check what's installed before solving complex problems
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
