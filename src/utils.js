const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

// ─── Paths ───────────────────────────────────────────────────
const KATANA_HOME = path.join(os.homedir(), '.katana');
const MEMORY_DIR = path.join(KATANA_HOME, 'memory');
const VAULT_SKILLS_DIR = path.join(MEMORY_DIR, 'skills');
const COMMANDS_DIR = path.join(KATANA_HOME, 'commands');

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
  if (!fs.existsSync(VAULT_SKILLS_DIR)) return [];

  const skills = [];
  const categories = fs.readdirSync(VAULT_SKILLS_DIR, { withFileTypes: true });

  for (const cat of categories) {
    if (!cat.isDirectory() || cat.name.startsWith('.') || cat.name === '_index.md') continue;

    const catPath = path.join(VAULT_SKILLS_DIR, cat.name);
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
  if (!fs.existsSync(VAULT_SKILLS_DIR)) return [];

  const categories = [];
  const entries = fs.readdirSync(VAULT_SKILLS_DIR, { withFileTypes: true });

  for (const entry of entries) {
    if (!entry.isDirectory() || entry.name.startsWith('.')) continue;

    const catPath = path.join(VAULT_SKILLS_DIR, entry.name);
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
  if (!fs.existsSync(COMMANDS_DIR)) return [];
  return fs.readdirSync(COMMANDS_DIR)
    .filter(f => f.endsWith('.md'))
    .map(f => ({
      name: f.replace('.md', ''),
      path: path.join(COMMANDS_DIR, f),
    }));
}

module.exports = {
  KATANA_HOME,
  MEMORY_DIR,
  VAULT_SKILLS_DIR,
  COMMANDS_DIR,
  copyDirRecursive,
  ensureDir,
  detectProjectStack,
  getVaultSkills,
  getVaultCategories,
  getVaultCommands,
};
