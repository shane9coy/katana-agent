const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
const { checkConflict } = require('../conflict');
const { copyDirRecursive, ensureDir, detectProjectStack, getVaultSkills, MEMORY_DIR, COMMANDS_DIR } = require('../utils');

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

  // Copy commands from ~/.katana/commands/
  if (fs.existsSync(COMMANDS_DIR)) {
    const commandsTarget = path.join(targetDir, 'commands');
    ensureDir(commandsTarget);
    const userCommands = fs.readdirSync(COMMANDS_DIR).filter(f => f.endsWith('.md'));
    for (const file of userCommands) {
      const dest = path.join(commandsTarget, file);
      if (!overwrite && fs.existsSync(dest)) continue;
      fs.copyFileSync(path.join(COMMANDS_DIR, file), dest);
    }
    if (userCommands.length > 0) {
      console.log(chalk.green(`  ✓ Loaded ${userCommands.length} command(s) from ~/.katana/commands/`));
    }
  }

  // Sync vault skills
  const vaultSkills = getVaultSkills();
  if (vaultSkills.length > 0) {
    const skillsTarget = path.join(targetDir, 'skills');
    ensureDir(skillsTarget);
    for (const skill of vaultSkills) {
      const dest = path.join(skillsTarget, skill.name);
      if (!overwrite && fs.existsSync(dest)) continue;
      copyDirRecursive(skill.path, dest, { overwrite: true });
    }
    console.log(chalk.green(`  ✓ Synced ${vaultSkills.length} skill(s) from Obsidian vault`));
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

  console.log('');
  console.log(chalk.bold.green('  ✓ Katana agent initialized in .codex/'));
  console.log(chalk.dim('  Skills:   ') + chalk.white(`${skillCount} installed`));
  console.log(chalk.dim('  Memory:   ') + chalk.white('~/.katana/memory/ (Obsidian vault)'));
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
This project uses **Katana Agent**. Memory: \`~/.katana/memory/\` (Obsidian vault).

On session start, read:
- \`~/.katana/memory/core/soul.md\` — agent identity
- \`~/.katana/memory/core/user.md\` — user context

## Conventions
- (add your conventions here)
`;
}

module.exports = { init };
