#!/bin/sh
# bootstrap.sh — one-command setup for Tenet
#
# Run from the repo root after cloning:
#   ./bootstrap.sh
#
# What it does:
#   1. Checks prerequisites (python3, git)
#   2. Generates memory/session-context.md
#   3. Generates memory/skills-catalog.md
#   4. Installs pre-commit hooks (or offers to init git if not a repo)
#   5. Prints per-vendor wiring instructions and the verification prompt
#
# Idempotent: safe to run multiple times.

set -eu

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ ! -f "LAUNCHER.md" ] || [ ! -d "core" ] || [ ! -d "memory" ]; then
    echo "ERROR: bootstrap.sh must run from the workspace root" >&2
    echo "(expected LAUNCHER.md, core/, memory/ in the current directory)" >&2
    exit 1
fi

cat <<HEADER
==========================================
  Tenet v1.0 — Bootstrap
  Workspace: $ROOT
==========================================

HEADER

# ----- 1/4 Prerequisites -----
echo "[1/4] Checking prerequisites..."
MISSING=""
if command -v python3 >/dev/null 2>&1; then
    TENET_PYTHON="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    TENET_PYTHON="$(command -v python)"
else
    MISSING="$MISSING python3"
    TENET_PYTHON=""
fi
if ! command -v git >/dev/null 2>&1; then
    MISSING="$MISSING git"
fi
if [ -n "$MISSING" ]; then
    echo "  MISSING required tools:$MISSING" >&2
    echo "  Install them and re-run." >&2
    exit 1
fi
echo "  python:  $TENET_PYTHON"
echo "  git:     $(command -v git)"
echo ""

# ----- 2/4 Session context -----
echo "[2/4] Generating memory/session-context.md..."
if [ -x "tools/scripts/build_session_context.sh" ]; then
    tools/scripts/build_session_context.sh
else
    echo "  ERROR: tools/scripts/build_session_context.sh missing or not executable" >&2
    exit 1
fi
echo ""

# ----- 3/4 Skills catalog -----
echo "[3/4] Generating memory/skills-catalog.md..."
if [ -x "tools/scripts/skills_index.sh" ]; then
    tools/scripts/skills_index.sh
else
    echo "  WARNING: tools/scripts/skills_index.sh missing — skipping skills catalog" >&2
fi
echo ""

# ----- 4/4 Git hooks -----
echo "[4/4] Git hooks..."
if [ -d ".git" ]; then
    if [ -x "tools/scripts/install_git_hooks.sh" ]; then
        tools/scripts/install_git_hooks.sh
    else
        echo "  WARNING: tools/scripts/install_git_hooks.sh missing — hooks not installed" >&2
    fi
else
    # Non-interactive check: if stdin is a terminal, prompt. Otherwise skip cleanly.
    if [ -t 0 ]; then
        printf "  Not a git repo. Initialize one? [y/N] "
        read -r ANSWER
        case "$ANSWER" in
            y|Y)
                git init
                if [ -x "tools/scripts/install_git_hooks.sh" ]; then
                    tools/scripts/install_git_hooks.sh
                fi
                ;;
            *)
                echo "  Skipping git init. Run 'git init && tools/scripts/install_git_hooks.sh' when ready."
                ;;
        esac
    else
        echo "  Not a git repo and running non-interactively — skipping git init."
    fi
fi
echo ""

cat <<DONE
==========================================
  Bootstrap complete.
==========================================

WIRING YOUR CODING ASSISTANT:

  Claude Code  → CLAUDE.md is already wired. No config needed.
  Gemini CLI   → GEMINI.md is already wired. No config needed.
  Cursor       → .cursorrules is already wired. Open in Cursor.
  Aider        → .aider.conf.yml is already wired. Run from this directory.
  Copilot Chat → .github/copilot-instructions.md is already wired.
  Codex        → Run: python3 tools/scripts/install-codex-config.py

VERIFY WIRING (any vendor):

  Ask your LLM:
  "What's in memory/session-context.md? Summarize the rules I'm operating under."

  Expected: it names OBSERVE, PLAN, EXECUTE, VERIFY, the ISC concept,
  the constitution rules, and the 3 built-in skills.

FIRST STEPS:

  1. Open memory/identity.md    — fill in who you are
  2. Open memory/current-focus.md — fill in this week's priorities
  3. Open memory/goals.md       — write your mission and goals
  4. Run: bin/tenet-skill list    — see the built-in skills

==========================================
DONE
