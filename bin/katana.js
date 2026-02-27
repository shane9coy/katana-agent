#!/usr/bin/env node

const { program } = require('commander');
const { version } = require('../package.json');
const chalk = require('chalk');

program
  .name('katana')
  .description('Katana Agent — Install your AI agent into any project')
  .version(version);

// ─── Init Commands ───────────────────────────────────────────

program
  .command('claude')
  .description('Initialize .claude/ folder with Katana skills & commands')
  .argument('[action]', 'Action to perform', 'init')
  .option('--minimal', 'Only install core skills (skip vault)')
  .option('--all', 'Install all skills and commands (skip picker)')
  .action((action, opts) => {
    if (action === 'init') require('../src/init/claude').init(opts);
    else console.log(chalk.red(`Unknown action: ${action}. Use: katana claude init`));
  });

program
  .command('kilocode')
  .description('Initialize .kilocode/ folder with Katana skills & agents')
  .argument('[action]', 'Action to perform', 'init')
  .option('--minimal', 'Only install core skills')
  .option('--all', 'Install all skills and commands (skip picker)')
  .action((action, opts) => {
    if (action === 'init') require('../src/init/kilocode').init(opts);
    else console.log(chalk.red(`Unknown action: ${action}. Use: katana kilocode init`));
  });

program
  .command('codex')
  .description('Initialize .codex/ folder with Katana skills')
  .argument('[action]', 'Action to perform', 'init')
  .option('--minimal', 'Only install core skills')
  .option('--all', 'Install all skills and commands (skip picker)')
  .action((action, opts) => {
    if (action === 'init') require('../src/init/codex').init(opts);
    else console.log(chalk.red(`Unknown action: ${action}. Use: katana codex init`));
  });

program
  .command('generic')
  .description('Initialize agent folder for Gemini, Cursor, Windsurf, self-hosted, etc.')
  .argument('[action]', 'Action to perform', 'init')
  .option('--dir <name>', 'Custom folder name (default: .agent)')
  .action((action, opts) => {
    if (action === 'init') require('../src/init/generic').init(opts);
    else console.log(chalk.red(`Unknown action: ${action}. Use: katana generic init`));
  });

program
  .command('init')
  .description('Initialize .katana/ folder (universal Katana format)')
  .action((opts) => {
    require('../src/init/universal').init(opts);
  });

// ─── Skill Commands ──────────────────────────────────────────

const skills = program.command('skills').description('Manage skills in your Obsidian vault');

skills
  .command('list')
  .description('List all skills in your vault')
  .action(() => require('../src/skills').list());

skills
  .command('sync')
  .description('Sync current project skills with vault')
  .action(() => require('../src/skills').sync());

// ─── Memory Commands ─────────────────────────────────────────

const memory = program.command('memory').description('Manage Katana memory vault');

memory
  .command('init')
  .description('Initialize Obsidian memory vault at ~/.katana/memory/')
  .action(() => require('../src/memory').initVault());

memory
  .command('status')
  .description('Show memory vault health and stats')
  .action(() => require('../src/memory').status());

memory
  .command('recall')
  .description('Search memory from terminal')
  .argument('<query>', 'Search term')
  .action((query) => require('../src/memory').recall(query));

memory
  .command('projects')
  .description('List all tracked projects')
  .action(() => require('../src/memory').listProjects());

// ─── Parse ───────────────────────────────────────────────────

program.parse();

// Show help if no command given
if (!process.argv.slice(2).length) {
  console.log('');
  console.log(chalk.bold('  ⚡ Katana Agent'));
  console.log(chalk.dim('  Install your AI agent into any project\n'));
  console.log(chalk.white('  Quick start:'));
  console.log(chalk.cyan('    katana claude init') + chalk.dim('      — .claude/ folder (Claude Code)'));
  console.log(chalk.cyan('    katana kilocode init') + chalk.dim('    — .kilocode/ folder (KiloCode)'));
  console.log(chalk.cyan('    katana codex init') + chalk.dim('       — .codex/ folder (OpenAI Codex)'));
  console.log(chalk.cyan('    katana generic init') + chalk.dim('     — .agent/ folder (Gemini, Cursor, Windsurf, etc.)'));
  console.log(chalk.cyan('    katana init') + chalk.dim('             — .katana/ folder (universal Katana format)'));
  console.log('');
  console.log(chalk.white('  Memory:'));
  console.log(chalk.cyan('    katana memory init') + chalk.dim('      — Create Obsidian memory vault'));
  console.log(chalk.cyan('    katana memory status') + chalk.dim('    — Vault health & stats'));
  console.log(chalk.cyan('    katana memory recall') + chalk.dim(' <q> — Search memory from terminal'));
  console.log(chalk.cyan('    katana memory projects') + chalk.dim('  — List tracked projects'));
  console.log('');
  console.log(chalk.white('  Skills:'));
  console.log(chalk.cyan('    katana skills list') + chalk.dim('      — List skills in vault'));
  console.log(chalk.cyan('    katana skills sync') + chalk.dim('      — Sync vault skills into project'));
  console.log('');
  program.outputHelp();
}
