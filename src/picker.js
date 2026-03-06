const readline = require('readline');
const chalk = require('chalk');
const figlet = require('figlet');

/**
 * Interactive picker for skill categories and commands.
 * 
 * Uses radio button interface with arrow key navigation.
 * "Select All" is the first option, mutually exclusive with individual selections.
 * 
 * @param {Array} categories - From getVaultCategories(): [{ name, skillCount, skills }]
 * @param {Array} commands - From getVaultCommands(): [{ name, path }]
 * @returns {Promise<{ categories: string[], commands: string[] }>} Selected category names and command names
 */

const RADIO_UNSELECTED = '○';
const RADIO_SELECTED = '●';

function displayHeader() {
  return new Promise((resolve) => {
    figlet('Katana Inventory', { font: 'Standard' }, (err, data) => {
      if (err) {
        console.log(chalk.cyan('  ╔═══════════════════════════════╗'));
        console.log(chalk.cyan('  ║    ') + chalk.bold.cyan('Katana Inventory') + chalk.cyan('    ║'));
        console.log(chalk.cyan('  ╚═══════════════════════════════╝'));
      } else {
        console.log(chalk.cyan(data));
      }
      resolve();
    });
  });
}

/**
 * Render a radio button list and handle user interaction
 * @param {Array} items - Array of { label, value, description } objects
 * @param {string} title - Section title to display
 * @param {Function} rl - readline interface
 * @param {Function} ask - question function
 * @returns {Promise<string[]>} - Selected values (empty if "Select All" was selected)
 */
async function radioPick(items, title, rl, ask) {
  if (items.length === 0) {
    return [];
  }

  let selectedIndex = 0; // Default to first item ("Select All")

  // Clear screen and render the menu
  const render = () => {
    console.clear();
    displayHeader().then(() => {
      console.log('');
      console.log(chalk.bold.underline('  ' + title));
      console.log('');
      console.log(chalk.dim('  Use ↑/↓ arrows to navigate, Enter to confirm'));
      console.log('');

      items.forEach((item, i) => {
        const isSelected = i === selectedIndex;
        const radio = isSelected ? RADIO_SELECTED : RADIO_UNSELECTED;
        
        if (i === 0 && item.value === 'all') {
          // "Select All" option
          console.log(
            chalk.cyan(`  ${radio}  `) +
            chalk.white(item.label)
          );
        } else {
          // Individual item
          const desc = item.description ? chalk.dim(' — ' + item.description) : '';
          console.log(
            chalk.cyan(`  ${radio}  `) +
            chalk.white(item.label) +
            desc
          );
        }
      });

      console.log('');
      console.log(chalk.dim('  Press Enter to confirm selection'));
    });
  };

  // Set up raw mode for arrow key handling
  return new Promise((resolve) => {
    const onKeyPress = (key) => {
      if (key === '\u001b[A') { // Up arrow
        selectedIndex = Math.max(0, selectedIndex - 1);
        render();
      } else if (key === '\u001b[B') { // Down arrow
        selectedIndex = Math.min(items.length - 1, selectedIndex + 1);
        render();
      } else if (key === '\r' || key === '\n') { // Enter
        rl.input.removeListener('keypress', onKeyPress);
        rl.close();
        
        // Determine selection based on radio button behavior
        const selected = items[selectedIndex];
        if (selected.value === 'all') {
          // "Select All" - return all values
          resolve(items.slice(1).map(item => item.value));
        } else {
          // Individual selection - return just that value
          resolve([selected.value]);
        }
      }
    };

    rl.input.on('keypress', onKeyPress);
    render();
  });
}

async function pickInstallItems(categories, commands) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const ask = (q) => new Promise((resolve) => rl.question(q, resolve));

  // ─── Figlet Header ─────────────────────────────────────────────
  
  await displayHeader();

  // ─── Skill Categories ─────────────────────────────────────────

  let selectedCategories = [];

  if (categories.length > 0) {
    // Build items array with "Select All" as first option
    const categoryItems = [
      { label: 'Select All', value: 'all', description: 'Install all skill categories' },
      ...categories.map(cat => ({
        label: cat.name,
        value: cat.name,
        description: `${cat.skillCount} skill${cat.skillCount !== 1 ? 's' : ''}`
      }))
    ];

    console.log('');
    console.log(chalk.bold.underline('  Skill Categories'));
    console.log('');
    console.log(chalk.dim('  Use ↑/↓ to navigate, Enter to confirm'));
    console.log(chalk.dim('  Selecting "Select All" will install all categories'));
    console.log('');

    const result = await radioPick(categoryItems, 'Skill Categories', rl, ask);
    selectedCategories = result;
  }

  // ─── Commands ───────────────────────────────────────────────

  let selectedCommands = [];

  if (commands.length > 0) {
    // Build items array with "Select All" as first option
    const commandItems = [
      { label: 'Select All', value: 'all', description: 'Install all commands' },
      ...commands.map(cmd => ({
        label: '/' + cmd.name,
        value: cmd.name,
        description: null
      }))
    ];

    console.clear();
    await displayHeader();
    
    console.log('');
    console.log(chalk.bold.underline('  Agent Commands'));
    console.log('');
    console.log(chalk.dim('  Use ↑/↓ to navigate, Enter to confirm'));
    console.log(chalk.dim('  Selecting "Select All" will install all commands'));
    console.log('');

    const result = await radioPick(commandItems, 'Agent Commands', rl, ask);
    selectedCommands = result;
  }

  // Summary
  const totalSkills = categories
    .filter(c => selectedCategories.includes(c.name))
    .reduce((sum, c) => sum + c.skillCount, 0);

  console.clear();
  await displayHeader();
  
  if (selectedCategories.length > 0 || selectedCommands.length > 0) {
    console.log('');
    console.log(chalk.bold.green('  ✓ Selection confirmed:'));
    console.log('');
    if (selectedCategories.length > 0) {
      console.log(chalk.white('  Skills: ') + chalk.cyan(selectedCategories.join(', ')) + chalk.dim(` (${totalSkills} total)`));
    }
    if (selectedCommands.length > 0) {
      console.log(chalk.white('  Commands: ') + chalk.cyan(selectedCommands.map(c => '/' + c).join(', ')));
    }
  }

  return {
    categories: selectedCategories,
    commands: selectedCommands,
  };
}

module.exports = { pickInstallItems };
