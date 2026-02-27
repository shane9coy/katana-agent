const readline = require('readline');
const chalk = require('chalk');

/**
 * Interactive picker for skill categories and commands.
 * 
 * Shows checkboxes for each skill category folder and each command.
 * User enters numbers to toggle, 'a' for all, Enter to confirm.
 * 
 * @param {Array} categories - From getVaultCategories(): [{ name, skillCount, skills }]
 * @param {Array} commands - From getVaultCommands(): [{ name, path }]
 * @returns {Promise<{ categories: string[], commands: string[] }>} Selected category names and command names
 */
async function pickInstallItems(categories, commands) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const ask = (q) => new Promise((resolve) => rl.question(q, resolve));

  // ─── Skill Categories ─────────────────────────────────────

  let selectedCategories = categories.map(c => c.name); // default: all

  if (categories.length > 0) {
    console.log('');
    console.log(chalk.bold('  Skill Categories:'));
    console.log('');

    categories.forEach((cat, i) => {
      const skillNames = cat.skills.length <= 4
        ? cat.skills.join(', ')
        : cat.skills.slice(0, 3).join(', ') + ` +${cat.skills.length - 3} more`;
      console.log(
        chalk.cyan(`    ${i + 1}.`) +
        chalk.white(` ${cat.name}`) +
        chalk.dim(` (${cat.skillCount} skill${cat.skillCount !== 1 ? 's' : ''})`) +
        chalk.dim(` — ${skillNames}`)
      );
    });

    console.log('');
    console.log(chalk.dim('    a = all, n = none, or enter numbers: 1,3,5'));
    console.log('');

    const answer = (await ask(chalk.white('  Install skill categories [a]: '))).trim().toLowerCase();

    if (answer === 'n' || answer === 'none') {
      selectedCategories = [];
    } else if (answer !== '' && answer !== 'a' && answer !== 'all') {
      const indices = answer.split(',')
        .map(s => parseInt(s.trim()) - 1)
        .filter(i => i >= 0 && i < categories.length);
      selectedCategories = indices.map(i => categories[i].name);
    }
    // empty or 'a' → all (default)
  }

  // ─── Commands ──────────────────────────────────────────────

  let selectedCommands = commands.map(c => c.name); // default: all

  if (commands.length > 0) {
    console.log('');
    console.log(chalk.bold('  Agent Commands:'));
    console.log('');

    commands.forEach((cmd, i) => {
      console.log(chalk.cyan(`    ${i + 1}.`) + chalk.white(` /${cmd.name}`));
    });

    console.log('');
    console.log(chalk.dim('    a = all, n = none, or enter numbers: 1,3'));
    console.log('');

    const answer = (await ask(chalk.white('  Install commands [a]: '))).trim().toLowerCase();

    if (answer === 'n' || answer === 'none') {
      selectedCommands = [];
    } else if (answer !== '' && answer !== 'a' && answer !== 'all') {
      const indices = answer.split(',')
        .map(s => parseInt(s.trim()) - 1)
        .filter(i => i >= 0 && i < commands.length);
      selectedCommands = indices.map(i => commands[i].name);
    }
  }

  rl.close();

  // Summary
  const totalSkills = categories
    .filter(c => selectedCategories.includes(c.name))
    .reduce((sum, c) => sum + c.skillCount, 0);

  if (selectedCategories.length > 0 || selectedCommands.length > 0) {
    console.log('');
    if (selectedCategories.length > 0) {
      console.log(chalk.dim(`  → Skills: ${selectedCategories.join(', ')} (${totalSkills} total)`));
    }
    if (selectedCommands.length > 0) {
      console.log(chalk.dim(`  → Commands: ${selectedCommands.map(c => '/' + c).join(', ')}`));
    }
  }

  return {
    categories: selectedCategories,
    commands: selectedCommands,
  };
}

module.exports = { pickInstallItems };
