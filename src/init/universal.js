const fs = require('fs');
const path = require('path');
const readline = require('readline');
const chalk = require('chalk');
const { checkConflict } = require('../conflict');
const { pickInstallItems } = require('../picker');
const { copyDirRecursive, ensureDir, detectProjectStack, getVaultSkills, getVaultCategories, getVaultCommands, MEMORY_DIR, COMMANDS_DIR } = require('../utils');

async function init(opts) {
  const targetDir = path.join(process.cwd(), '.katana');
  const templateDir = path.join(__dirname, '../../templates/universal');

  console.log('');
  console.log(chalk.bold('⚡ Katana Agent → Universal'));
  console.log('');

  let action = 'fresh';

  if (fs.existsSync(targetDir)) {
    action = await checkConflict('.katana');
    if (action === 'cancel') { console.log(chalk.dim('  Cancelled.')); return; }
    if (action === 'backup') {
      const backupName = `.katana.backup-${Date.now()}`;
      fs.renameSync(targetDir, path.join(process.cwd(), backupName));
      console.log(chalk.green(`  ✓ Backed up → ${backupName}`));
    }
    if (action === 'replace') {
      fs.rmSync(targetDir, { recursive: true, force: true });
      console.log(chalk.green('  ✓ Removed existing .katana/'));
    }
  }

  const overwrite = action !== 'merge';
  copyDirRecursive(templateDir, targetDir, { overwrite });

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

  // Copy commands from ~/.katana/commands/
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
      console.log(chalk.green(`  ✓ Loaded ${commandCount} command(s) from ~/.katana/commands/`));
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

  // Generate project.yaml
  const project = detectProjectStack();
  const projectYaml = path.join(targetDir, 'project.yaml');
  if (overwrite || !fs.existsSync(projectYaml)) {
    fs.writeFileSync(projectYaml, `# Katana Project Config
name: "${project.name}"
stack: "${project.stack}"
agent: "master-agent"
model: "anthropic"

memory:
  vault: "~/.katana/memory/"
  project: "${project.name}"
`);
    console.log(chalk.green(`  ✓ Generated project.yaml (detected: ${project.stack})`));
  }

  const skillsDir = path.join(targetDir, 'skills');
  const skillCount = fs.existsSync(skillsDir)
    ? fs.readdirSync(skillsDir, { withFileTypes: true }).filter(d => d.isDirectory()).length
    : 0;
  const commandsDir = path.join(targetDir, 'commands');
  const commandCount = fs.existsSync(commandsDir)
    ? fs.readdirSync(commandsDir).filter(f => f.endsWith('.md')).length
    : 0;

  console.log('');
  console.log(chalk.bold.green('  ✓ Katana agent initialized in .katana/'));
  console.log('');
  console.log(chalk.dim('  Commands: ') + chalk.white(`${commandCount} installed`));
  console.log(chalk.dim('  Skills:   ') + chalk.white(`${skillCount} installed`));
  console.log(chalk.dim('  Memory:   ') + chalk.white('~/.katana/memory/ (Obsidian vault)'));
  console.log('');
}

module.exports = { init };
