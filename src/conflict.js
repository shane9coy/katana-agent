const readline = require('readline');
const chalk = require('chalk');

async function checkConflict(folderName) {
  console.log('');
  console.log(chalk.yellow(`⚠️  ${folderName}/ already exists in this project.`));
  console.log('');
  console.log(chalk.white('  1.') + chalk.green(' Merge') + chalk.dim('    — Add Katana files alongside existing (recommended)'));
  console.log(chalk.white('  2.') + chalk.red(' Replace') + chalk.dim('  — Remove existing folder, install fresh'));
  console.log(chalk.white('  3.') + chalk.blue(' Backup') + chalk.dim('   — Copy existing to .backup, then install fresh'));
  console.log(chalk.white('  4.') + chalk.dim(' Cancel') + chalk.dim('   — Do nothing'));
  console.log('');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question(chalk.white('  Choose [1-4] (default: 1): '), (answer) => {
      rl.close();
      const choice = answer.trim() || '1';
      const map = { '1': 'merge', '2': 'replace', '3': 'backup', '4': 'cancel' };
      resolve(map[choice] || 'merge');
    });
  });
}

module.exports = { checkConflict };
