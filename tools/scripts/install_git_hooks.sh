#!/bin/sh
# install_git_hooks.sh — install the workspace's shared git hooks
#
# Wires git to look in .githooks/ for hook scripts (instead of the default
# .git/hooks/). The workspace ships .githooks/pre-commit which runs the
# frontmatter + secret-pattern checks documented in core/CODEX_INTEGRATION.md.
#
# Run once per clone:
#   tools/scripts/install_git_hooks.sh
#
# This is the deterministic Codex-side equivalent of Claude Code's runtime
# inspectors — the discipline lives in the file, not in the model.

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$REPO_ROOT"

if [ ! -d "$REPO_ROOT/.git" ] && ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "Not a git repository at $REPO_ROOT — run 'git init' first." >&2
    exit 1
fi

if [ ! -d "$REPO_ROOT/.githooks" ]; then
    echo "No .githooks/ directory at $REPO_ROOT — nothing to install." >&2
    exit 1
fi

# Only chmod hooks that actually exist; an earlier iteration chmod'd files
# that weren't shipped, which failed on a fresh clone.
HOOKS_INSTALLED=0
for hook in pre-commit pre-push commit-msg post-commit; do
    if [ -f "$REPO_ROOT/.githooks/$hook" ]; then
        chmod +x "$REPO_ROOT/.githooks/$hook"
        echo "  installed: .githooks/$hook"
        HOOKS_INSTALLED=$((HOOKS_INSTALLED + 1))
    fi
done

if [ "$HOOKS_INSTALLED" -eq 0 ]; then
    echo ".githooks/ exists but contains no recognized hook scripts." >&2
    exit 1
fi

git config core.hooksPath .githooks
echo ""
echo "Installed $HOOKS_INSTALLED shared git hook(s) for $REPO_ROOT"
echo "Active hooks path: $(git config --get core.hooksPath)"
echo ""
echo "Hooks will run on every commit. To bypass (discouraged):"
echo "  git commit --no-verify"
