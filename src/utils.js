const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// ─── Paths ───────────────────────────────────────────────────
// Prefer user-writable ~/.katana data, support legacy ~/katana-agent installs,
// and fall back to bundled package assets when running via npm link or npm install.
const PACKAGE_ROOT = path.resolve(__dirname, '..');
const USER_HOME = process.env.HOME || process.cwd();
const currentFolder = path.basename(PACKAGE_ROOT);
const isLocal = currentFolder.includes('local');

const DATA_ROOT = path.join(USER_HOME, '.katana');
const LEGACY_ROOT = isLocal
  ? path.join(USER_HOME, 'katana-agent-local')
  : path.join(USER_HOME, 'katana-agent');
const LEGACY_AGENT_DIR = path.join(LEGACY_ROOT, 'agent');
const PACKAGE_AGENT_DIR = path.join(PACKAGE_ROOT, 'agent');

const CUSTOM_MEMORY_DIR = path.join(DATA_ROOT, 'memory');
const CUSTOM_MEMORY_SETTINGS_FILE = path.join(CUSTOM_MEMORY_DIR, 'settings.json');
const CUSTOM_COMMANDS_DIR = path.join(DATA_ROOT, 'commands');
const CUSTOM_SETTINGS_FILE = path.join(DATA_ROOT, 'settings.json');
const CUSTOM_SKILLS_DIR = path.join(CUSTOM_MEMORY_DIR, 'skills');
const CUSTOM_AGENT_MD = path.join(DATA_ROOT, 'AGENT.md');

const LEGACY_MEMORY_DIR = path.join(LEGACY_AGENT_DIR, 'memory');
const LEGACY_MEMORY_SETTINGS_FILE = path.join(LEGACY_MEMORY_DIR, 'settings.json');
const LEGACY_COMMANDS_DIR = path.join(LEGACY_AGENT_DIR, 'commands');
const LEGACY_SETTINGS_FILE = path.join(LEGACY_AGENT_DIR, 'settings.json');
const LEGACY_SKILLS_DIR = path.join(LEGACY_AGENT_DIR, 'skills');
const LEGACY_AGENT_MD = path.join(LEGACY_ROOT, 'AGENT.md');

const PACKAGE_MEMORY_SETTINGS_FILE = path.join(PACKAGE_AGENT_DIR, 'memory', 'settings.json');
const PACKAGE_COMMANDS_DIR = path.join(PACKAGE_AGENT_DIR, 'commands');
const PACKAGE_SETTINGS_FILE = path.join(PACKAGE_AGENT_DIR, 'settings.json');
const PACKAGE_SKILLS_DIR = path.join(PACKAGE_AGENT_DIR, 'skills');
const PACKAGE_AGENT_MD = path.join(PACKAGE_ROOT, 'AGENT.md');

const PATH_LABELS = {
  root: '~/.katana',
  memory: '~/.katana/memory/',
  memorySettings: '~/.katana/memory/settings.json',
  commands: '~/.katana/commands/',
  settings: '~/.katana/settings.json',
  skills: '~/.katana/memory/skills/',
  skillIndex: '~/.katana/memory/skills/_index.md',
  agentMd: '~/.katana/AGENT.md',
  legacyRoot: isLocal ? '~/katana-agent-local' : '~/katana-agent',
  legacyMemory: isLocal ? '~/katana-agent-local/agent/memory/' : '~/katana-agent/agent/memory/',
  legacyCommands: isLocal ? '~/katana-agent-local/agent/commands/' : '~/katana-agent/agent/commands/',
  legacySettings: isLocal ? '~/katana-agent-local/agent/settings.json' : '~/katana-agent/agent/settings.json',
};

function firstMatch(candidates, predicate) {
  return candidates.find(candidate => {
    try {
      return predicate(candidate);
    } catch (error) {
      return false;
    }
  }) || candidates[candidates.length - 1];
}

function fileExists(filePath) {
  return fs.existsSync(filePath);
}

function copyFileIfMissing(sourcePath, destinationPath) {
  if (!fs.existsSync(sourcePath) || fs.existsSync(destinationPath)) return false;
  ensureDir(path.dirname(destinationPath));
  fs.copyFileSync(sourcePath, destinationPath);
  return true;
}

function dirHasCommands(dirPath) {
  if (!fs.existsSync(dirPath)) return false;

  return fs.readdirSync(dirPath, { withFileTypes: true })
    .some(entry => entry.isFile() && entry.name.endsWith('.md'));
}

function dirHasSkills(dirPath) {
  if (!fs.existsSync(dirPath)) return false;

  for (const category of fs.readdirSync(dirPath, { withFileTypes: true })) {
    if (!category.isDirectory() || category.name.startsWith('.')) continue;

    const categoryPath = path.join(dirPath, category.name);
    for (const skill of fs.readdirSync(categoryPath, { withFileTypes: true })) {
      if (!skill.isDirectory()) continue;
      if (fs.existsSync(path.join(categoryPath, skill.name, 'SKILL.md'))) {
        return true;
      }
    }
  }

  return false;
}

function ensureDefaultDataRoot() {
  const hadCustomMemoryContent = fs.existsSync(CUSTOM_MEMORY_DIR)
    && fs.readdirSync(CUSTOM_MEMORY_DIR).length > 0;

  ensureDir(DATA_ROOT);
  ensureDir(CUSTOM_MEMORY_DIR);

  if (!hadCustomMemoryContent && fs.existsSync(LEGACY_MEMORY_DIR)) {
    copyDirRecursive(LEGACY_MEMORY_DIR, CUSTOM_MEMORY_DIR, { overwrite: false });
  }

  if (!dirHasSkills(CUSTOM_SKILLS_DIR)) {
    if (dirHasSkills(LEGACY_SKILLS_DIR)) {
      copyDirRecursive(LEGACY_SKILLS_DIR, CUSTOM_SKILLS_DIR, { overwrite: false });
    } else if (dirHasSkills(PACKAGE_SKILLS_DIR)) {
      copyDirRecursive(PACKAGE_SKILLS_DIR, CUSTOM_SKILLS_DIR, { overwrite: false });
    }
  }

  if (!dirHasCommands(CUSTOM_COMMANDS_DIR)) {
    if (dirHasCommands(LEGACY_COMMANDS_DIR)) {
      copyDirRecursive(LEGACY_COMMANDS_DIR, CUSTOM_COMMANDS_DIR, { overwrite: false });
    } else if (dirHasCommands(PACKAGE_COMMANDS_DIR)) {
      copyDirRecursive(PACKAGE_COMMANDS_DIR, CUSTOM_COMMANDS_DIR, { overwrite: false });
    }
  }

  if (!fileExists(CUSTOM_SETTINGS_FILE)) {
    if (!copyFileIfMissing(LEGACY_SETTINGS_FILE, CUSTOM_SETTINGS_FILE)) {
      copyFileIfMissing(PACKAGE_SETTINGS_FILE, CUSTOM_SETTINGS_FILE);
    }
  }

  if (!fileExists(CUSTOM_AGENT_MD)) {
    if (!copyFileIfMissing(LEGACY_AGENT_MD, CUSTOM_AGENT_MD)) {
      copyFileIfMissing(PACKAGE_AGENT_MD, CUSTOM_AGENT_MD);
    }
  }

  if (fs.existsSync(CUSTOM_MEMORY_DIR) && !fileExists(CUSTOM_MEMORY_SETTINGS_FILE)) {
    if (!copyFileIfMissing(LEGACY_MEMORY_SETTINGS_FILE, CUSTOM_MEMORY_SETTINGS_FILE)) {
      copyFileIfMissing(PACKAGE_MEMORY_SETTINGS_FILE, CUSTOM_MEMORY_SETTINGS_FILE);
    }
  }
}

const KATANA_ROOT = DATA_ROOT;
const AGENT_DIR = DATA_ROOT;
const MEMORY_DIR = CUSTOM_MEMORY_DIR;
const MEMORY_SETTINGS_FILE = CUSTOM_MEMORY_SETTINGS_FILE;
const VAULT_SKILLS_DIR = CUSTOM_SKILLS_DIR;
const COMMANDS_DIR = CUSTOM_COMMANDS_DIR;
const SETTINGS_FILE = CUSTOM_SETTINGS_FILE;
const AGENT_MD = CUSTOM_AGENT_MD;

// ─── File Operations ─────────────────────────────────────────

function copyDirRecursive(src, dest, opts = {}) {
  if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
  const skipFiles = opts.skip || [];

  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    // Skip files in the skip list
    if (skipFiles.includes(entry.name)) continue;

    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDirRecursive(srcPath, destPath, opts);
    } else {
      // In merge mode, skip files that already exist
      if (!opts.overwrite && fs.existsSync(destPath)) continue;
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

// ─── Project Detection ──────────────────────────────────────

function detectProjectStack() {
  const cwd = process.cwd();
  const info = { name: path.basename(cwd), stack: 'Unknown', commands: '' };

  // Git repo name
  try {
    const gitRoot = execSync('git rev-parse --show-toplevel', { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
    info.name = path.basename(gitRoot);
  } catch (e) {
    // Not a git repo
  }

  // Detect stack from config files
  if (fs.existsSync(path.join(cwd, 'package.json'))) {
    try {
      const pkg = JSON.parse(fs.readFileSync(path.join(cwd, 'package.json'), 'utf-8'));
      const deps = { ...pkg.dependencies, ...pkg.devDependencies };
      if (deps.next) info.stack = 'Next.js / TypeScript';
      else if (deps.react) info.stack = 'React';
      else if (deps.express) info.stack = 'Express / Node.js';
      else if (deps.vue) info.stack = 'Vue.js';
      else if (deps.svelte || deps['@sveltejs/kit']) info.stack = 'Svelte';
      else info.stack = 'Node.js';
      info.commands = Object.keys(pkg.scripts || {}).map(s => `npm run ${s}`).join(', ');
    } catch (e) {
      info.stack = 'Node.js';
    }
  } else if (fs.existsSync(path.join(cwd, 'pyproject.toml')) || fs.existsSync(path.join(cwd, 'requirements.txt'))) {
    info.stack = 'Python';
  } else if (fs.existsSync(path.join(cwd, 'Cargo.toml'))) {
    info.stack = 'Rust';
  } else if (fs.existsSync(path.join(cwd, 'go.mod'))) {
    info.stack = 'Go';
  } else if (fs.existsSync(path.join(cwd, 'Gemfile'))) {
    info.stack = 'Ruby';
  } else if (fs.existsSync(path.join(cwd, 'pom.xml')) || fs.existsSync(path.join(cwd, 'build.gradle'))) {
    info.stack = 'Java';
  }

  return info;
}

// ─── Vault Skills ────────────────────────────────────────────

function getVaultSkills() {
  ensureDefaultDataRoot();

  const skillsDir = firstMatch(
    [VAULT_SKILLS_DIR, LEGACY_SKILLS_DIR, PACKAGE_SKILLS_DIR],
    dirHasSkills
  );
  if (!fs.existsSync(skillsDir)) return [];

  const skills = [];
  const categories = fs.readdirSync(skillsDir, { withFileTypes: true });

  for (const cat of categories) {
    if (!cat.isDirectory() || cat.name.startsWith('.') || cat.name === '_index.md') continue;

    const catPath = path.join(skillsDir, cat.name);
    const entries = fs.readdirSync(catPath, { withFileTypes: true });

    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const skillPath = path.join(catPath, entry.name);
      const skillFile = path.join(skillPath, 'SKILL.md');
      if (fs.existsSync(skillFile)) {
        skills.push({
          name: entry.name,
          category: cat.name,
          path: skillPath,
        });
      }
    }
  }

  return skills;
}

function getVaultCategories() {
  ensureDefaultDataRoot();

  const skillsDir = firstMatch(
    [VAULT_SKILLS_DIR, LEGACY_SKILLS_DIR, PACKAGE_SKILLS_DIR],
    dirHasSkills
  );
  if (!fs.existsSync(skillsDir)) return [];

  const categories = [];
  const entries = fs.readdirSync(skillsDir, { withFileTypes: true });

  for (const entry of entries) {
    if (!entry.isDirectory() || entry.name.startsWith('.')) continue;

    const catPath = path.join(skillsDir, entry.name);
    const skills = fs.readdirSync(catPath, { withFileTypes: true })
      .filter(e => e.isDirectory())
      .filter(e => fs.existsSync(path.join(catPath, e.name, 'SKILL.md')));

    if (skills.length > 0) {
      categories.push({
        name: entry.name,
        path: catPath,
        skillCount: skills.length,
        skills: skills.map(s => s.name),
      });
    }
  }

  return categories;
}

function getVaultCommands() {
  ensureDefaultDataRoot();

  const commandsDir = firstMatch(
    [COMMANDS_DIR, LEGACY_COMMANDS_DIR, PACKAGE_COMMANDS_DIR],
    dirHasCommands
  );
  if (!fs.existsSync(commandsDir)) return [];

  return fs.readdirSync(commandsDir)
    .filter(f => f.endsWith('.md'))
    .map(f => ({
      name: f.replace('.md', ''),
      path: path.join(commandsDir, f),
    }));
}

module.exports = {
  DATA_ROOT,
  KATANA_ROOT,
  AGENT_DIR,
  MEMORY_DIR,
  MEMORY_SETTINGS_FILE,
  VAULT_SKILLS_DIR,
  COMMANDS_DIR,
  SETTINGS_FILE,
  PATH_LABELS,
  copyDirRecursive,
  ensureDir,
  ensureDefaultDataRoot,
  detectProjectStack,
  getVaultSkills,
  getVaultCategories,
  getVaultCommands,
};
