const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
const { checkConflict } = require('../conflict');
const { copyDirRecursive, ensureDir, detectProjectStack, getVaultSkills } = require('../utils');

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

  console.log('');
  console.log(chalk.bold.green('  ✓ Katana agent initialized in .katana/'));
  console.log(chalk.dim('  Skills:   ') + chalk.white(`${skillCount} installed`));
  console.log(chalk.dim('  Memory:   ') + chalk.white('~/.katana/memory/ (Obsidian vault)'));
  console.log('');
}

module.exports = { init };
