#!/bin/bash
# ============================================================================
# Katana Agent — Setup Script
# ============================================================================
# Run this from any CLI agent: "run ~/katana-agent/setup.sh"
# Or run directly: bash ~/katana-agent/setup.sh
#
# This script:
# 1. Verifies katana-agent installation
# 2. Checks Node.js and npm
# 3. Installs dependencies if needed
# 4. Links the CLI command globally
# 5. Verifies the agent/ folder structure
# 6. Reports what skills and commands are available
# 7. Outputs instructions for the agent to continue setup
# ============================================================================

set -e

KATANA_ROOT="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$KATANA_ROOT/agent"

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

# ─── Step 5: Verify agent/ folder ─────────────────────────
echo ""
echo "📂 Checking agent folder..."

MISSING=0

if [ ! -d "$AGENT_DIR" ]; then
  echo "❌ agent/ folder missing"
  MISSING=1
else
  echo "✅ agent/ exists"

  if [ -d "$AGENT_DIR/memory/core" ]; then
    echo "  ✅ memory/core/ (soul.md, user.md, routines.md)"
  else
    echo "  ❌ memory/core/ missing"
    MISSING=1
  fi

  if [ -d "$AGENT_DIR/commands" ]; then
    CMD_COUNT=$(find "$AGENT_DIR/commands" -name "*.md" | wc -l | tr -d ' ')
    echo "  ✅ commands/ ($CMD_COUNT agents)"
  else
    echo "  ❌ commands/ missing"
    MISSING=1
  fi

  if [ -d "$AGENT_DIR/skills" ]; then
    SKILL_COUNT=$(find "$AGENT_DIR/skills" -name "SKILL.md" | wc -l | tr -d ' ')
    CAT_COUNT=$(find "$AGENT_DIR/skills" -maxdepth 1 -type d | tail -n +2 | wc -l | tr -d ' ')
    echo "  ✅ skills/ ($SKILL_COUNT skills in $CAT_COUNT categories)"
  else
    echo "  ❌ skills/ missing"
    MISSING=1
  fi

  if [ -f "$AGENT_DIR/settings.json" ]; then
    echo "  ✅ settings.json"
  else
    echo "  ⚠️  settings.json missing (will use bundled default)"
  fi
fi

# ─── Step 6: List what's available ────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo "  AGENT COMMANDS"
echo "═══════════════════════════════════════"

if [ -d "$AGENT_DIR/commands" ]; then
  for f in "$AGENT_DIR/commands"/*.md; do
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

if [ -d "$AGENT_DIR/skills" ]; then
  for dir in "$AGENT_DIR/skills"/*/; do
    [ -d "$dir" ] || continue
    CAT_NAME=$(basename "$dir")
    SKILLS=$(find "$dir" -name "SKILL.md" | wc -l | tr -d ' ')
    SKILL_NAMES=$(find "$dir" -name "SKILL.md" -exec dirname {} \; | xargs -I{} basename {} | tr '\n' ', ' | sed 's/,$//')
    echo "  📁 $CAT_NAME ($SKILLS) — $SKILL_NAMES"
  done
fi

# ─── Step 7: User profile check ──────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo "  USER PROFILE"
echo "═══════════════════════════════════════"

USER_MD="$AGENT_DIR/memory/core/user.md"
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

# ─── Step 8: Next steps ──────────────────────────────────
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
echo "     Edit: $AGENT_DIR/memory/core/user.md"
echo ""
echo "  2. Open memory vault in Obsidian:"
echo "     Open folder → $AGENT_DIR/memory/"
echo ""
echo "  3. Configure skills (API keys, etc):"
echo "     Tell your agent: 'Read $AGENT_DIR/skills/agents/installer/SKILL.md"
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
