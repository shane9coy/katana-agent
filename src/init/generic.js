const fs = require('fs');
const path = require('path');
const readline = require('readline');
const chalk = require('chalk');
const { checkConflict } = require('../conflict');
const { copyDirRecursive, ensureDir, detectProjectStack, getVaultSkills, MEMORY_DIR, COMMANDS_DIR } = require('../utils');

async function init(opts) {
  const folderName = opts.dir || '.agent';
  const targetDir = path.join(process.cwd(), folderName);
  const templateDir = path.join(__dirname, '../../templates/generic');

  console.log('');
  console.log(chalk.bold('⚡ Katana Agent → Generic'));
  console.log(chalk.dim(`  Target: ${folderName}/`));
  console.log(chalk.dim('  Works with: Gemini CLI, Cursor, Windsurf, Aider, self-hosted, any agent'));
  console.log('');

  let action = 'fresh';

  if (fs.existsSync(targetDir)) {
    action = await checkConflict(folderName);
    if (action === 'cancel') { console.log(chalk.dim('  Cancelled.')); return; }
    if (action === 'backup') {
      const backupName = `${folderName}.backup-${Date.now()}`;
      fs.renameSync(targetDir, path.join(process.cwd(), backupName));
      console.log(chalk.green(`  ✓ Backed up → ${backupName}`));
    }
    if (action === 'replace') {
      fs.rmSync(targetDir, { recursive: true, force: true });
      console.log(chalk.green(`  ✓ Removed existing ${folderName}/`));
    }
  }

  const overwrite = action !== 'merge';

  // Copy generic template
  copyDirRecursive(templateDir, targetDir, { overwrite });

  // Copy commands from ~/.katana/commands/ (overrides bundled templates)
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

  // Generate AGENT.md (generic project memory file)
  const project = detectProjectStack();
  const agentMdPath = path.join(targetDir, 'AGENT.md');
  if (overwrite || !fs.existsSync(agentMdPath)) {
    fs.writeFileSync(agentMdPath, generateAgentMd(project));
    console.log(chalk.green(`  ✓ Generated AGENT.md (detected: ${project.stack})`));
  }

  // Register project in memory vault
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
  console.log(chalk.bold.green(`  ✓ Katana agent initialized in ${folderName}/`));
  console.log('');
  console.log(chalk.dim('  Commands: ') + chalk.white(`${commandCount} installed`));
  console.log(chalk.dim('  Skills:   ') + chalk.white(`${skillCount} installed`));
  console.log(chalk.dim('  Memory:   ') + chalk.white('~/.katana/memory/ (Obsidian vault)'));
  console.log('');
  console.log(chalk.dim('  Point your agent to read AGENT.md on session start.'));
  console.log(chalk.dim('  All skills are standard SKILL.md format (AgentSkills spec).'));
  console.log('');
}

function generateAgentMd(project) {
  return `# ${project.name}

## Stack
${project.stack}
${project.commands ? `\n## Available Commands\n${project.commands.split(', ').map(c => '- \`' + c + '\`').join('\n')}` : ''}

## Agent Configuration
This project uses **Katana Agent** with centralized Obsidian memory.

### Memory Vault Location
All persistent memory lives at \`~/.katana/memory/\`. This is an Obsidian-compatible vault.

### On Session Start
1. Read \`~/.katana/memory/core/soul.md\` — your identity and behavior guidelines
2. Read \`~/.katana/memory/core/user.md\` — facts about the user
3. Read \`~/.katana/memory/core/routines.md\` — learned patterns and workflows
4. Check \`~/.katana/memory/projects/${project.name}/\` for project-specific history

### Memory Commands
- **Remember:** When user says "remember this" or session ends, summarize key decisions and append to \`~/.katana/memory/work.md\` (newest at top). Format: \`## YYYY-MM-DD — ${project.name}\`
- **Recall:** When user asks about past work, search \`~/.katana/memory/work.md\` and \`~/.katana/memory/projects/\`

### Skills
Check \`./skills/\` directory for available skills. Each skill has a \`SKILL.md\` with instructions.
Check \`~/.katana/memory/skills/_index.md\` for skills in the central vault.

## Code Conventions
- (add your project conventions here)

## Notes
- Skills use the AgentSkills spec (SKILL.md with YAML frontmatter)
- Memory files use Obsidian-compatible markdown with [[wikilinks]] and #tags
- Open \`~/.katana/memory/\` in Obsidian to browse your agent's brain
`;
}

function registerProject(projectName) {
  const projectDir = path.join(MEMORY_DIR, 'projects', projectName);
  if (!fs.existsSync(projectDir)) {
    ensureDir(projectDir);
    const sessionsFile = path.join(projectDir, 'sessions.md');
    fs.writeFileSync(sessionsFile, `---
project: ${projectName}
created: ${new Date().toISOString().split('T')[0]}
tags: [project]
---

# ${projectName} — Session History

<!-- Agent appends session summaries here. Newest at top. -->

## ${new Date().toISOString().split('T')[0]} — Project initialized
Katana Agent initialized for this project.
`);
  }
}

module.exports = { init };
