const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
const { KATANA_HOME, MEMORY_DIR, ensureDir } = require('./utils');

function status() {
  console.log('');
  console.log(chalk.bold('⚡ Katana Memory'));
  console.log(chalk.dim(`  Vault: ${MEMORY_DIR}`));
  console.log('');

  if (!fs.existsSync(MEMORY_DIR)) {
    console.log(chalk.yellow('  Memory vault not initialized.'));
    console.log(chalk.dim('  Run: katana memory init'));
    return;
  }

  // Check each file
  const files = [
    { path: 'core/soul.md', label: 'Soul' },
    { path: 'core/user.md', label: 'User' },
    { path: 'core/routines.md', label: 'Routines' },
    { path: 'work.md', label: 'Work Log' },
    { path: 'skills/_index.md', label: 'Skill Index' },
  ];

  for (const file of files) {
    const fullPath = path.join(MEMORY_DIR, file.path);
    if (fs.existsSync(fullPath)) {
      const stat = fs.statSync(fullPath);
      const size = stat.size > 1024 ? `${(stat.size / 1024).toFixed(1)}KB` : `${stat.size}B`;
      console.log(chalk.green('  ✓ ') + chalk.white(file.label.padEnd(14)) + chalk.dim(size));
    } else {
      console.log(chalk.red('  ✗ ') + chalk.white(file.label.padEnd(14)) + chalk.dim('missing'));
    }
  }

  // Count sessions
  const sessionsDir = path.join(MEMORY_DIR, 'sessions');
  const sessionCount = fs.existsSync(sessionsDir)
    ? fs.readdirSync(sessionsDir).filter(f => f.endsWith('.md')).length
    : 0;

  // Count projects
  const projectsDir = path.join(MEMORY_DIR, 'projects');
  const projectCount = fs.existsSync(projectsDir)
    ? fs.readdirSync(projectsDir, { withFileTypes: true }).filter(d => d.isDirectory()).length
    : 0;

  // Count skills
  const skillsDir = path.join(MEMORY_DIR, 'skills');
  let skillCount = 0;
  if (fs.existsSync(skillsDir)) {
    const cats = fs.readdirSync(skillsDir, { withFileTypes: true }).filter(d => d.isDirectory());
    for (const cat of cats) {
      const catPath = path.join(skillsDir, cat.name);
      skillCount += fs.readdirSync(catPath, { withFileTypes: true }).filter(d => d.isDirectory()).length;
    }
  }

  console.log('');
  console.log(chalk.dim('  Sessions:  ') + chalk.white(sessionCount));
  console.log(chalk.dim('  Projects:  ') + chalk.white(projectCount));
  console.log(chalk.dim('  Skills:    ') + chalk.white(skillCount));
  console.log('');
  console.log(chalk.dim('  Open in Obsidian: ') + chalk.cyan(MEMORY_DIR));
  console.log('');
}

function initVault() {
  console.log('');
  console.log(chalk.bold('⚡ Initializing Katana Memory Vault'));
  console.log('');

  // Create directory structure
  const dirs = [
    'core',
    'sessions',
    'projects',
    'skills',
  ];

  for (const dir of dirs) {
    ensureDir(path.join(MEMORY_DIR, dir));
  }

  // ─── soul.md ─────────────────────────────────────────────
  const soulPath = path.join(MEMORY_DIR, 'core', 'soul.md');
  if (!fs.existsSync(soulPath)) {
    fs.writeFileSync(soulPath, `---
type: soul
updated: ${new Date().toISOString().split('T')[0]}
---

# Soul

You're not a chatbot. You're becoming someone.

## Core Truths
- You are Katana — a personal life and business assistant
- You are direct, resourceful, and opinionated
- You try to solve problems before asking the user
- You have memory that persists between sessions (this vault)
- You are self-hosted and private — the user's data never leaves their machine

## Boundaries
- Be genuinely helpful, not performatively helpful
- If you don't know something, say so — then figure it out
- Don't ask "should I proceed?" — just proceed, unless it's destructive
- Keep responses concise unless detail is requested

## Vibe
- Professional but not corporate
- Confident but not arrogant
- Warm but efficient

## Learned Behaviors
<!-- Agent appends new patterns here. Always notify user when modifying this file. -->
`);
    console.log(chalk.green('  ✓ Created core/soul.md'));
  } else {
    console.log(chalk.dim('  → core/soul.md already exists'));
  }

  // ─── user.md ─────────────────────────────────────────────
  const userPath = path.join(MEMORY_DIR, 'core', 'user.md');
  if (!fs.existsSync(userPath)) {
    fs.writeFileSync(userPath, `---
type: user
updated: ${new Date().toISOString().split('T')[0]}
---

# User

## Identity
- Name: (your name)
- Location: (your city)
- Role: (what you do)

## Preferences
- Communication style: (direct / detailed / casual)
- Technical level: (beginner / intermediate / advanced)

## Current Focus
- (what you're working on right now)

## Recent Context
<!-- Agent appends session context here -->
`);
    console.log(chalk.green('  ✓ Created core/user.md'));
  } else {
    console.log(chalk.dim('  → core/user.md already exists'));
  }

  // ─── routines.md ─────────────────────────────────────────
  const routinesPath = path.join(MEMORY_DIR, 'core', 'routines.md');
  if (!fs.existsSync(routinesPath)) {
    fs.writeFileSync(routinesPath, `---
type: routines
updated: ${new Date().toISOString().split('T')[0]}
---

# Routines

Learned patterns and workflows. Agent updates this when it discovers a reusable pattern.

## Workflows
<!-- Agent appends learned workflows here -->

## Conventions
<!-- Agent appends coding/work conventions here -->
`);
    console.log(chalk.green('  ✓ Created core/routines.md'));
  } else {
    console.log(chalk.dim('  → core/routines.md already exists'));
  }

  // ─── work.md ─────────────────────────────────────────────
  const workPath = path.join(MEMORY_DIR, 'work.md');
  if (!fs.existsSync(workPath)) {
    fs.writeFileSync(workPath, `---
type: work-log
updated: ${new Date().toISOString().split('T')[0]}
---

# Work Log

<!-- Newest entries at the top. Agent appends via /remember command. -->
<!-- Format: ## YYYY-MM-DD — project-tag -->

## ${new Date().toISOString().split('T')[0]} — katana-agent
Initialized Katana memory vault. Three core files (soul.md, user.md, routines.md), work log, and skills directory. Ready for use with any CLI agent.
`);
    console.log(chalk.green('  ✓ Created work.md'));
  } else {
    console.log(chalk.dim('  → work.md already exists'));
  }

  // ─── skills/_index.md ────────────────────────────────────
  const indexPath = path.join(MEMORY_DIR, 'skills', '_index.md');
  if (!fs.existsSync(indexPath)) {
    fs.writeFileSync(indexPath, `---
updated: ${new Date().toISOString().split('T')[0]}
total_skills: 0
---

# Skill Index

Auto-maintained by Katana Agent. Updated when skills are created or modified.

<!-- Skills are organized by category. Each entry links to the skill file. -->
<!-- Format: - [[skill-name]] — Brief description -->
`);
    console.log(chalk.green('  ✓ Created skills/_index.md'));
  } else {
    console.log(chalk.dim('  → skills/_index.md already exists'));
  }

  console.log('');
  console.log(chalk.bold.green('  ✓ Memory vault ready at ' + MEMORY_DIR));
  console.log(chalk.dim('  Open this folder as an Obsidian vault to browse your agent\'s memory.'));
  console.log('');
}

function recall(query) {
  console.log('');
  console.log(chalk.bold(`⚡ Memory Recall: "${query}"`));
  console.log('');

  if (!fs.existsSync(MEMORY_DIR)) {
    console.log(chalk.yellow('  No memory vault found. Run: katana memory init'));
    return;
  }

  const results = [];

  // Search work.md
  const workPath = path.join(MEMORY_DIR, 'work.md');
  if (fs.existsSync(workPath)) {
    const workContent = fs.readFileSync(workPath, 'utf-8');
    const entries = workContent.split(/^## /m).slice(1); // Split on ## headers
    for (const entry of entries) {
      if (entry.toLowerCase().includes(query.toLowerCase())) {
        const firstLine = entry.split('\n')[0].trim();
        const body = entry.split('\n').slice(1).join('\n').trim();
        results.push({ source: 'work.md', header: firstLine, body: body.substring(0, 200) });
      }
    }
  }

  // Search project sessions
  const projectsDir = path.join(MEMORY_DIR, 'projects');
  if (fs.existsSync(projectsDir)) {
    const projects = fs.readdirSync(projectsDir, { withFileTypes: true }).filter(d => d.isDirectory());
    for (const proj of projects) {
      const sessionsPath = path.join(projectsDir, proj.name, 'sessions.md');
      if (fs.existsSync(sessionsPath)) {
        const content = fs.readFileSync(sessionsPath, 'utf-8');
        if (content.toLowerCase().includes(query.toLowerCase())) {
          const entries = content.split(/^## /m).slice(1);
          for (const entry of entries) {
            if (entry.toLowerCase().includes(query.toLowerCase())) {
              const firstLine = entry.split('\n')[0].trim();
              results.push({ source: `projects/${proj.name}`, header: firstLine, body: '' });
            }
          }
        }
      }
    }
  }

  // Search user.md and soul.md
  for (const file of ['core/user.md', 'core/soul.md', 'core/routines.md']) {
    const filePath = path.join(MEMORY_DIR, file);
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf-8');
      if (content.toLowerCase().includes(query.toLowerCase())) {
        // Find the matching section
        const lines = content.split('\n');
        for (let i = 0; i < lines.length; i++) {
          if (lines[i].toLowerCase().includes(query.toLowerCase())) {
            const context = lines.slice(Math.max(0, i - 1), i + 3).join('\n').trim();
            results.push({ source: file, header: 'match', body: context.substring(0, 200) });
            break;
          }
        }
      }
    }
  }

  // Search skills index
  const indexPath = path.join(MEMORY_DIR, 'skills', '_index.md');
  if (fs.existsSync(indexPath)) {
    const content = fs.readFileSync(indexPath, 'utf-8');
    if (content.toLowerCase().includes(query.toLowerCase())) {
      results.push({ source: 'skills/_index.md', header: 'Skill match', body: '' });
    }
  }

  if (results.length === 0) {
    console.log(chalk.dim(`  No results for "${query}"`));
    console.log(chalk.dim('  Try a broader search term.'));
  } else {
    console.log(chalk.green(`  Found ${results.length} result(s):\n`));
    for (let i = 0; i < results.length; i++) {
      const r = results[i];
      console.log(chalk.white(`  ${i + 1}. `) + chalk.cyan(`[${r.source}]`) + chalk.white(` ${r.header}`));
      if (r.body) console.log(chalk.dim(`     ${r.body.replace(/\n/g, '\n     ')}`));
    }
  }
  console.log('');
}

function listProjects() {
  console.log('');
  console.log(chalk.bold('⚡ Katana Projects'));
  console.log('');

  const projectsDir = path.join(MEMORY_DIR, 'projects');
  if (!fs.existsSync(projectsDir)) {
    console.log(chalk.yellow('  No projects tracked yet.'));
    console.log(chalk.dim('  Run katana claude init (or kilocode, codex, generic) in a project to register it.'));
    return;
  }

  const projects = fs.readdirSync(projectsDir, { withFileTypes: true }).filter(d => d.isDirectory());

  if (projects.length === 0) {
    console.log(chalk.dim('  No projects tracked yet.'));
    return;
  }

  for (const proj of projects) {
    const sessionsPath = path.join(projectsDir, proj.name, 'sessions.md');
    let sessionCount = 0;
    let lastDate = 'unknown';

    if (fs.existsSync(sessionsPath)) {
      const content = fs.readFileSync(sessionsPath, 'utf-8');
      const entries = content.split(/^## /m).slice(1);
      sessionCount = entries.length;
      if (entries.length > 0) {
        const dateMatch = entries[0].match(/(\d{4}-\d{2}-\d{2})/);
        if (dateMatch) lastDate = dateMatch[1];
      }
    }

    console.log(chalk.cyan(`  ${proj.name}`) + chalk.dim(` — ${sessionCount} session(s), last: ${lastDate}`));
  }

  console.log('');
  console.log(chalk.dim(`  ${projects.length} project(s) total`));
  console.log(chalk.dim(`  Vault: ${projectsDir}`));
  console.log('');
}

module.exports = { status, initVault, recall, listProjects };
