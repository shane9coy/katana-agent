const readline = require('readline');
const chalk = require('chalk');
const figlet = require('figlet');

/**
 * Interactive picker for skill categories and commands.
 *
 * Preferred UX:
 * - ↑ / ↓ to navigate
 * - Space to toggle items
 * - Navigate to Continue, then press Enter to confirm
 *
 * Falls back to line-based selection only when the terminal cannot support
 * raw interactive input.
 *
 * @param {Array} categories - From getVaultCategories(): [{ name, skillCount, skills }]
 * @param {Array} commands - From getVaultCommands(): [{ name, path }]
 * @returns {Promise<{ categories: string[], commands: string[] }>} Selected category names and command names
 */

let headerPromise = null;

function renderFiglet(text) {
  return new Promise((resolve) => {
    figlet(text, { font: 'Standard' }, (err, data) => {
      resolve(err ? null : chalk.cyan(data));
    });
  });
}

function getHeader() {
  if (!headerPromise) {
    headerPromise = (async () => {
      const katanaWordmark = await renderFiglet('Katana');

      if (katanaWordmark) {
        return katanaWordmark;
      }

      return [
        chalk.cyan('  ╔════════════════╗'),
        chalk.cyan('  ║     ') + chalk.bold.cyan('Katana') + chalk.cyan('     ║'),
        chalk.cyan('  ╚════════════════╝'),
      ].join('\n');
    })();
  }

  return headerPromise;
}

async function displayHeader() {
  console.log(await getHeader());
}

function askQuestion(prompt) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    rl.question(prompt, (answer) => {
      rl.close();
      resolve(answer);
    });
  });
}

function parseFallbackSelection(answer, items) {
  const trimmed = answer.trim().toLowerCase();

  if (!trimmed || trimmed === 'a' || trimmed === 'all') {
    return { valid: true, values: items.map(item => item.value) };
  }

  if (trimmed === 'n' || trimmed === 'none') {
    return { valid: true, values: [] };
  }

  const tokens = trimmed.split(',').map(token => token.trim()).filter(Boolean);
  if (tokens.length === 0) {
    return { valid: false, values: [] };
  }

  const selectedIndexes = [];
  for (const token of tokens) {
    if (!/^\d+$/.test(token)) {
      return { valid: false, values: [] };
    }

    const parsed = Number.parseInt(token, 10);
    if (parsed < 1 || parsed > items.length) {
      return { valid: false, values: [] };
    }

    selectedIndexes.push(parsed - 1);
  }

  const uniqueIndexes = [...new Set(selectedIndexes)];
  return {
    valid: true,
    values: uniqueIndexes.map(index => items[index].value),
  };
}

async function promptFallbackMultiSelect(title, items, promptLabel) {
  while (true) {
    console.log('');
    console.log(chalk.bold.underline('  ' + title));
    console.log('');
    console.log(chalk.yellow('  Interactive arrow navigation is unavailable in this terminal.'));
    console.log(chalk.dim('  Enter numbers separated by commas. a = all, n = none, Enter = all'));
    console.log('');

    items.forEach((item, index) => {
      const desc = item.description ? chalk.dim(' — ' + item.description) : '';
      console.log(
        chalk.cyan(`  ${index + 1}. `) +
        chalk.white(item.label) +
        desc
      );
    });

    console.log('');
    const answer = await askQuestion(chalk.white(`  ${promptLabel} [a]: `));
    const parsed = parseFallbackSelection(answer, items);

    if (parsed.valid) {
      return parsed.values;
    }

    console.log(chalk.red('  Invalid selection. Example: 1,3,5'));
  }
}

function canUseInteractiveMenu() {
  return Boolean(
    process.stdin.isTTY &&
    process.stdout.isTTY &&
    typeof process.stdin.setRawMode === 'function'
  );
}

function createInitialSelection(items) {
  return new Set(items.map(item => item.value));
}

function areAllSelected(selectedValues, items) {
  return items.length > 0 && selectedValues.size === items.length;
}

function toggleAll(selectedValues, items) {
  if (areAllSelected(selectedValues, items)) {
    return new Set();
  }

  return createInitialSelection(items);
}

function toggleValue(selectedValues, value) {
  const next = new Set(selectedValues);

  if (next.has(value)) {
    next.delete(value);
  } else {
    next.add(value);
  }

  return next;
}

function buildRows(items) {
  return [
    {
      type: 'all',
      label: 'Select All',
      description: 'Toggle every option',
    },
    ...items.map(item => ({
      type: 'item',
      ...item,
    })),
    {
      type: 'action',
      label: 'Continue',
      description: 'Confirm current selection',
    },
  ];
}

function renderInteractiveMenu(header, title, items, rows, cursorIndex, selectedValues) {
  console.clear();
  console.log(header);
  console.log('');
  console.log(chalk.bold.underline('  ' + title));
  console.log('');
  console.log(chalk.dim('  Use ↑/↓ arrows to navigate'));
  console.log(chalk.dim('  Press Space to toggle selections'));
  console.log(chalk.dim('  Highlight Continue and press Enter to confirm'));
  console.log('');

  rows.forEach((row, index) => {
    const active = index === cursorIndex;
    const cursor = active ? chalk.cyan('›') : ' ';

    if (row.type === 'action') {
      const label = active ? chalk.bold.white(row.label) : chalk.white(row.label);
      const desc = row.description ? chalk.dim(' — ' + row.description) : '';
      console.log(`${cursor} ${chalk.green('→')} ${label}${desc}`);
      return;
    }

    const checked = row.type === 'all'
      ? areAllSelected(selectedValues, items)
      : selectedValues.has(row.value);

    const box = checked ? chalk.green('[x]') : chalk.dim('[ ]');
    const label = active ? chalk.bold.white(row.label) : chalk.white(row.label);
    const desc = row.description ? chalk.dim(' — ' + row.description) : '';
    console.log(`${cursor} ${box} ${label}${desc}`);
  });

  console.log('');

  let summary = 'none';
  if (selectedValues.size === items.length) summary = 'all';
  else if (selectedValues.size > 0) summary = `${selectedValues.size} selected`;

  console.log(chalk.dim(`  Current selection: ${summary}`));
  console.log('');
}

async function interactiveMultiSelect(title, items) {
  const header = await getHeader();
  const rows = buildRows(items);
  const actionIndex = rows.length - 1;

  let cursorIndex = 0;
  let selectedValues = createInitialSelection(items);

  return new Promise((resolve) => {
    const input = process.stdin;
    let rawModeEnabled = false;

    const cleanup = () => {
      input.removeListener('keypress', onKeyPress);

      if (rawModeEnabled) {
        input.setRawMode(false);
      }

      input.pause();
    };

    const render = () => {
      renderInteractiveMenu(header, title, items, rows, cursorIndex, selectedValues);
    };

    const onKeyPress = (_str, key = {}) => {
      if (key.ctrl && key.name === 'c') {
        cleanup();
        process.stdout.write('\n');
        process.exit(130);
      }

      if (key.name === 'up') {
        cursorIndex = cursorIndex === 0 ? rows.length - 1 : cursorIndex - 1;
        render();
        return;
      }

      if (key.name === 'down') {
        cursorIndex = cursorIndex === rows.length - 1 ? 0 : cursorIndex + 1;
        render();
        return;
      }

      if (key.name === 'space') {
        if (cursorIndex === actionIndex) {
          return;
        }

        if (cursorIndex === 0) {
          selectedValues = toggleAll(selectedValues, items);
        } else {
          selectedValues = toggleValue(selectedValues, rows[cursorIndex].value);
        }

        render();
        return;
      }

      if (key.name === 'return' || key.name === 'enter') {
        if (cursorIndex !== actionIndex) {
          return;
        }

        cleanup();
        resolve([...selectedValues]);
      }
    };

    readline.emitKeypressEvents(input);
    input.resume();
    input.setRawMode(true);
    rawModeEnabled = true;
    input.on('keypress', onKeyPress);
    render();
  });
}

async function pickSection(title, items, promptLabel) {
  if (items.length === 0) {
    return [];
  }

  if (canUseInteractiveMenu()) {
    return interactiveMultiSelect(title, items);
  }

  return promptFallbackMultiSelect(title, items, promptLabel);
}

async function pickInstallItems(categories, commands) {
  console.log('');
  await displayHeader();

  const categoryItems = categories.map(cat => ({
    label: cat.name,
    value: cat.name,
    description: `${cat.skillCount} skill${cat.skillCount !== 1 ? 's' : ''}`,
  }));

  const commandItems = commands.map(cmd => ({
    label: '/' + cmd.name,
    value: cmd.name,
    description: null,
  }));

  const selectedCategories = await pickSection(
    'Skill Categories',
    categoryItems,
    'Select skill categories'
  );

  const selectedCommands = await pickSection(
    'Agent Commands',
    commandItems,
    'Select agent commands'
  );

  const totalSkills = categories
    .filter(c => selectedCategories.includes(c.name))
    .reduce((sum, c) => sum + c.skillCount, 0);

  if (selectedCategories.length > 0 || selectedCommands.length > 0) {
    console.log('');
    console.log(chalk.bold.green('  ✓ Selection confirmed:'));
    console.log('');

    if (selectedCategories.length > 0) {
      console.log(
        chalk.white('  Skills: ') +
        chalk.cyan(selectedCategories.join(', ')) +
        chalk.dim(` (${totalSkills} total)`)
      );
    } else {
      console.log(chalk.white('  Skills: ') + chalk.dim('none selected'));
    }

    if (selectedCommands.length > 0) {
      console.log(
        chalk.white('  Commands: ') +
        chalk.cyan(selectedCommands.map(command => '/' + command).join(', '))
      );
    } else {
      console.log(chalk.white('  Commands: ') + chalk.dim('none selected'));
    }

    console.log('');
  }

  return {
    categories: selectedCategories,
    commands: selectedCommands,
  };
}

module.exports = { pickInstallItems };
