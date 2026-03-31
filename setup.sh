#!/bin/bash
# ============================================================================
# Katana Agent — Setup Script
# ============================================================================
# Run directly from this package directory: bash ./setup.sh
# Or use the CLI after linking/installing globally: katana memory init
#
# This script:
# 1. Verifies katana-agent installation
# 2. Checks Node.js and npm
# 3. Installs dependencies if needed
# 4. Links the CLI command globally
# 5. Ensures the ~/.katana data folder exists
# 6. Reports what skills and commands are available
# 7. Outputs instructions for the agent to continue setup
# ============================================================================

set -e

KATANA_ROOT="$(cd "$(dirname "$0")" && pwd)"
DATA_ROOT="$HOME/.katana"
MEMORY_DIR="$DATA_ROOT/memory"
COMMANDS_DIR="$DATA_ROOT/commands"
SKILLS_DIR="$MEMORY_DIR/skills"
SETTINGS_FILE="$DATA_ROOT/settings.json"

echo ""
echo "⚡ Katana Agent — Setup"
echo "========================"
echo ""

# ─── Step 1: Verify installation ──────────────────────────
echo "📁 Katana root: $KATANA_ROOT"

if [ ! -f "$KATANA_ROOT/package.json" ]; then
  echo "❌ ERROR: package.json not found at $KATANA_ROOT"
  echo "   Make sure you're running this from the katana-agent directory."
  exit 1
fi

if [ ! -d "$KATANA_ROOT/bin" ] || [ ! -f "$KATANA_ROOT/bin/katana.js" ]; then
  echo "❌ ERROR: bin/katana.js not found."
  exit 1
fi

echo "✅ Package found"

# ─── Step 2: Check Node.js ────────────────────────────────
if ! command -v node &> /dev/null; then
  echo "❌ ERROR: Node.js not found. Install 18+ from https://nodejs.org"
  exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
  echo "❌ ERROR: Node.js $NODE_VERSION too old. Need 18+."
  exit 1
fi

echo "✅ Node.js $(node -v)"

# ─── Step 3: Install dependencies ─────────────────────────
if [ ! -d "$KATANA_ROOT/node_modules" ]; then
  echo "📦 Installing dependencies..."
  cd "$KATANA_ROOT" && npm install
  echo "✅ Dependencies installed"
else
  echo "✅ Dependencies already installed"
fi

# ─── Step 4: Link CLI globally ────────────────────────────
echo "🔗 Linking katana CLI globally..."
cd "$KATANA_ROOT" && npm link 2>/dev/null || {
  echo "⚠️  npm link failed. Trying with sudo..."
  sudo npm link 2>/dev/null || echo "⚠️  Could not link globally. Use: node $KATANA_ROOT/bin/katana.js"
}

if command -v katana &> /dev/null; then
  echo "✅ 'katana' command available globally"
else
  echo "⚠️  'katana' not in PATH. Use: node $KATANA_ROOT/bin/katana.js"
fi

# ─── Step 5: Ensure ~/.katana exists ───────────────────────
echo ""
echo "🗂  Initializing ~/.katana data folder..."
cd "$KATANA_ROOT" && node ./bin/katana.js memory init >/dev/null 2>&1 || true

# ─── Step 6: Verify ~/.katana folder ───────────────────────
echo ""
echo "📂 Checking ~/.katana folder..."

MISSING=0

if [ ! -d "$DATA_ROOT" ]; then
  echo "❌ ~/.katana folder missing"
  MISSING=1
else
  echo "✅ ~/.katana exists"

  if [ -d "$MEMORY_DIR/core" ]; then
    echo "  ✅ memory/core/ (soul.md, user.md, routines.md)"
  else
    echo "  ❌ memory/core/ missing"
    MISSING=1
  fi

  if [ -d "$COMMANDS_DIR" ]; then
    CMD_COUNT=$(find "$COMMANDS_DIR" -name "*.md" | wc -l | tr -d ' ')
    echo "  ✅ commands/ ($CMD_COUNT agents)"
  else
    echo "  ❌ commands/ missing"
    MISSING=1
  fi

  if [ -d "$SKILLS_DIR" ]; then
    SKILL_COUNT=$(find "$SKILLS_DIR" -name "SKILL.md" | wc -l | tr -d ' ')
    CAT_COUNT=$(find "$SKILLS_DIR" -maxdepth 1 -type d | tail -n +2 | wc -l | tr -d ' ')
    echo "  ✅ skills/ ($SKILL_COUNT skills in $CAT_COUNT categories)"
  else
    echo "  ❌ skills/ missing"
    MISSING=1
  fi

  if [ -f "$SETTINGS_FILE" ]; then
    echo "  ✅ settings.json"
  else
    echo "  ⚠️  settings.json missing (will use bundled default)"
  fi
fi

# ─── Step 7: List what's available ────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo "  AGENT COMMANDS"
echo "═══════════════════════════════════════"

if [ -d "$COMMANDS_DIR" ]; then
  for f in "$COMMANDS_DIR"/*.md; do
    [ -f "$f" ] || continue
    NAME=$(basename "$f" .md)
    if [ "$NAME" = "katana" ]; then
      echo "  ⚡ /$NAME  ← master agent"
    else
      echo "  /$NAME"
    fi
  done
fi

echo ""
echo "═══════════════════════════════════════"
echo "  SKILL CATEGORIES"
echo "═══════════════════════════════════════"

if [ -d "$SKILLS_DIR" ]; then
  for dir in "$SKILLS_DIR"/*/; do
    [ -d "$dir" ] || continue
    CAT_NAME=$(basename "$dir")
    SKILLS=$(find "$dir" -name "SKILL.md" | wc -l | tr -d ' ')
    SKILL_NAMES=$(find "$dir" -name "SKILL.md" -exec dirname {} \; | xargs -I{} basename {} | tr '\n' ', ' | sed 's/,$//')
    echo "  📁 $CAT_NAME ($SKILLS) — $SKILL_NAMES"
  done
fi

# ─── Step 8: User profile check ──────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo "  USER PROFILE"
echo "═══════════════════════════════════════"

USER_MD="$MEMORY_DIR/core/user.md"
if [ -f "$USER_MD" ]; then
  LINES=$(wc -l < "$USER_MD" | tr -d ' ')
  if [ "$LINES" -gt 10 ]; then
    echo "  ✅ user.md configured ($LINES lines)"
  else
    echo "  ⚠️  user.md looks empty ($LINES lines)"
    echo "  → Tell your agent: 'Fill in $USER_MD with my info'"
  fi
else
  echo "  ❌ user.md not found"
fi

# ─── Step 9: Next steps ──────────────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo "  NEXT STEPS"
echo "═══════════════════════════════════════"
echo ""

if [ "$MISSING" -eq 1 ]; then
  echo "  ⚠️  Some components missing. Run the V1.1 migration first."
  echo ""
fi

echo "  1. Fill in your user profile:"
echo "     Edit: $MEMORY_DIR/core/user.md"
echo ""
echo "  2. Open memory vault in Obsidian:"
echo "     Open folder → $MEMORY_DIR/"
echo ""
echo "  3. Configure skills (API keys, etc):"
echo "     Tell your agent: 'Read $SKILLS_DIR/agents/installer/SKILL.md"
echo "     and walk me through setup'"
echo ""
echo "  4. Install into a project:"
echo "     cd ~/your-project && katana claude init"
echo ""
echo "  5. Daily briefing:"
echo "     /katana for your morning routine"
echo "     /stream for news & market intelligence"
echo ""
echo "═══════════════════════════════════════"
echo "  ⚡ Katana Agent is ready."
echo "═══════════════════════════════════════"
echo ""
