const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
const { VAULT_SKILLS_DIR, getVaultSkills, copyDirRecursive, ensureDir } = require('./utils');

function list() {
  console.log('');
  console.log(chalk.bold('⚡ Katana Skills'));
  console.log(chalk.dim(`  Vault: ${VAULT_SKILLS_DIR}`));
  console.log('');

  if (!fs.existsSync(VAULT_SKILLS_DIR)) {
    console.log(chalk.yellow('  No skills vault found. Run: katana memory init'));
    return;
  }

  const skills = getVaultSkills();

  if (skills.length === 0) {
    console.log(chalk.dim('  No skills in vault yet.'));
    console.log(chalk.dim('  Skills are created automatically when your agent solves complex problems,'));
    console.log(chalk.dim('  or you can create them manually in ~/.katana/memory/skills/'));
    return;
  }

  // Group by category
  const grouped = {};
  for (const skill of skills) {
    if (!grouped[skill.category]) grouped[skill.category] = [];
    grouped[skill.category].push(skill);
  }

  for (const [category, categorySkills] of Object.entries(grouped)) {
    console.log(chalk.bold.white(`  ${category}/`));
    for (const skill of categorySkills) {
      console.log(chalk.cyan(`    ${skill.name}`));
    }
  }

  console.log('');
  console.log(chalk.dim(`  ${skills.length} skill(s) total`));
  console.log('');
}

function sync() {
  console.log('');
  console.log(chalk.bold('⚡ Syncing skills from vault'));
  console.log('');

  const vaultSkills = getVaultSkills();

  if (vaultSkills.length === 0) {
    console.log(chalk.yellow('  No skills in vault to sync.'));
    return;
  }

  // Find which agent folder exists in current project
  const targets = [
    { dir: '.claude/skills', name: 'Claude Code' },
    { dir: '.kilocode/skills', name: 'KiloCode' },
    { dir: '.codex/skills', name: 'Codex' },
    { dir: '.agent/skills', name: 'Generic Agent' },
    { dir: '.katana/skills', name: 'Katana' },
  ];

  let synced = 0;

  for (const target of targets) {
    const targetPath = path.join(process.cwd(), target.dir);
    if (!fs.existsSync(targetPath)) continue;

    for (const skill of vaultSkills) {
      const dest = path.join(targetPath, skill.name);
      copyDirRecursive(skill.path, dest, { overwrite: true });
    }

    console.log(chalk.green(`  ✓ ${target.name}: synced ${vaultSkills.length} skill(s) → ${target.dir}/`));
    synced++;
  }

  if (synced === 0) {
    console.log(chalk.yellow('  No agent folders found in this project.'));
    console.log(chalk.dim('  Run: katana claude init, katana kilocode init, or katana init'));
  }

  console.log('');
}

module.exports = { list, sync };
