#!/bin/sh
# build_session_context.sh — synthesize workspace startup contexts
#
# Generates TWO output files from the same source set:
#
#   memory/session-context.md        — SLIM (Claude Code)
#     Condensed doctrine + full operational state. ~15–25k.
#     Loaded via @-import in CLAUDE.md. Stays fast as the workspace grows.
#
#   memory/session-context-codex.md  — FULL (Codex / Aider / Gemini CLI)
#     All doctrine files verbatim + operational state. ~55k+.
#     Referenced from ~/.codex/config.toml developer_instructions.
#
# The slim version sources its condensed doctrine from:
#   memory/session-context-local.md  (maintained alongside the doctrine files)
# Specifically: everything from the first ## heading through the line before
# ## SKILLS CATALOG. The operational files are then appended in full.
#
# Usage:
#   tools/scripts/build_session_context.sh           # generate both (default)
#   tools/scripts/build_session_context.sh --claude  # slim only
#   tools/scripts/build_session_context.sh --codex   # full only
#
# Run from workspace root OR anywhere — the script locates root automatically.
#
# Exit codes:
#   0  success
#   1  workspace structure not detected
#   2  required input file missing
#
# Idempotent: safe to run repeatedly.

set -eu

# ---------------------------------------------------------------------------
# Locate workspace root (traverse up from CWD)
# ---------------------------------------------------------------------------
ROOT=""
CANDIDATE="$(pwd)"
for _ in 1 2 3 4 5 6 7 8; do
    if [ -f "$CANDIDATE/LAUNCHER.md" ] && [ -d "$CANDIDATE/core" ] && [ -d "$CANDIDATE/memory" ]; then
        ROOT="$CANDIDATE"
        break
    fi
    CANDIDATE="$(dirname "$CANDIDATE")"
done

if [ -z "$ROOT" ]; then
    echo "ERROR: could not find workspace root (LAUNCHER.md + core/ + memory/)" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Argument parsing — default: build both
# ---------------------------------------------------------------------------
BUILD_CLAUDE=1
BUILD_CODEX=1
for arg in "$@"; do
    case "$arg" in
        --claude) BUILD_CODEX=0 ;;
        --codex)  BUILD_CLAUDE=0 ;;
        --help|-h)
            echo "Usage: $0 [--claude|--codex]"
            echo "  --claude  generate slim session-context.md only"
            echo "  --codex   generate full session-context-codex.md only"
            echo "  (default) generate both"
            exit 0
            ;;
        *)
            echo "ERROR: unknown argument: $arg" >&2
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Required inputs (doctrine + operational state)
# ---------------------------------------------------------------------------
REQUIRED_DOCTRINE="
core/constitution.md
core/ALGORITHM.md
core/ISC.md
core/effort-tiering.md
core/verification-doctrine.md
core/decision-rules.md
memory/identity.md
memory/current-focus.md
memory/goals.md
LAUNCHER.md
"

REQUIRED_SLIM="memory/session-context-local.md"

for f in $REQUIRED_DOCTRINE; do
    [ -f "$ROOT/$f" ] || { echo "ERROR: required file missing: $f" >&2; exit 2; }
done

if [ "$BUILD_CLAUDE" -eq 1 ] && [ ! -f "$ROOT/$REQUIRED_SLIM" ]; then
    echo "ERROR: slim doctrine source missing: $REQUIRED_SLIM" >&2
    echo "This file provides condensed doctrine for the Claude slim context." >&2
    echo "Regenerate it manually or run --codex only." >&2
    exit 2
fi

# ---------------------------------------------------------------------------
# Helper: section divider
# ---------------------------------------------------------------------------
divider() {
    printf '\n\n========================================\n'
    printf '## Source: %s\n' "$1"
    printf '========================================\n\n'
}

# ---------------------------------------------------------------------------
# Helper: append optional files (skills catalog, active-work)
# ---------------------------------------------------------------------------
append_operational() {
    local root="$1"

    if [ -f "$root/memory/skills-catalog.md" ]; then
        divider "memory/skills-catalog.md (auto-generated)"
        cat "$root/memory/skills-catalog.md"
    elif [ -f "$root/skills/skills-map.md" ]; then
        divider "skills/skills-map.md (catalog)"
        cat "$root/skills/skills-map.md"
    elif [ -x "$root/tools/scripts/skills_index.sh" ]; then
        printf '\n\n========================================\n'
        printf '## Skills Catalog (inline)\n'
        printf '========================================\n\n'
        "$root/tools/scripts/skills_index.sh"
    fi

    if [ -f "$root/active-work-map.md" ]; then
        divider "active-work-map.md"
        cat "$root/active-work-map.md"
    fi
}

TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ---------------------------------------------------------------------------
# Generate slim session-context.md (Claude Code edition)
# ---------------------------------------------------------------------------
if [ "$BUILD_CLAUDE" -eq 1 ]; then
    OUT_CLAUDE="$ROOT/memory/session-context.md"
    TMP_CLAUDE="$OUT_CLAUDE.tmp.$$"

    {
        cat <<HEADER
---
title: Session Context — Claude Code Edition (synthesized)
type: synthesized
domain: tenet
product: Tenet
audience: claude-code
owner: operator
status: active
updated: ${TIMESTAMP}
tags:
  - session-context
  - synthesized
  - claude-code-startup
artifact_type: synthesized-context
generated_by: tools/scripts/build_session_context.sh
generated_at: ${TIMESTAMP}
warning: do-not-edit-by-hand
---

# Session Context — Tenet (Claude Code Edition)

Generated by \`tools/scripts/build_session_context.sh --claude\`.
**Do not edit by hand.** Edit source files in \`core/\` and \`memory/\` instead.

**This is the slim Claude Code variant.** Condensed doctrine (all rules intact,
rationale stripped) plus full operational state. Claude Code reads full doctrine
files on-demand (\`core/*.md\`) — verbatim repetition wastes context.

For Codex / Aider / Gemini CLI, use \`memory/session-context-codex.md\` (full)
— those models need the doctrine verbatim to hold the same operational floor.

---

HEADER

        printf '========================================\n'
        printf '## Condensed Doctrine (source: memory/session-context-local.md)\n'
        printf '========================================\n\n'
        awk '
            BEGIN { printing=0 }
            printing && /^## SKILLS CATALOG/ { exit }
            !printing && /^## / { printing=1 }
            printing { print }
        ' "$ROOT/memory/session-context-local.md"

        divider "memory/identity.md"
        cat "$ROOT/memory/identity.md"

        divider "memory/current-focus.md"
        cat "$ROOT/memory/current-focus.md"

        divider "memory/goals.md"
        cat "$ROOT/memory/goals.md"

        append_operational "$ROOT"

        printf '\n\n---\n_end of synthesized context (Claude Code slim edition)_\n'
    } > "$TMP_CLAUDE"

    mv "$TMP_CLAUDE" "$OUT_CLAUDE"
    LINES=$(wc -l < "$OUT_CLAUDE")
    BYTES=$(wc -c < "$OUT_CLAUDE")
    echo "Wrote $OUT_CLAUDE — $LINES lines, $BYTES bytes  [Claude Code slim]"
fi

# ---------------------------------------------------------------------------
# Generate full session-context-codex.md (Codex / Aider / Gemini CLI edition)
# ---------------------------------------------------------------------------
if [ "$BUILD_CODEX" -eq 1 ]; then
    OUT_CODEX="$ROOT/memory/session-context-codex.md"
    TMP_CODEX="$OUT_CODEX.tmp.$$"

    {
        cat <<HEADER
---
title: Session Context — Codex Edition (synthesized)
type: synthesized
domain: tenet
product: Tenet
audience: codex
owner: operator
status: active
updated: ${TIMESTAMP}
tags:
  - session-context
  - synthesized
  - codex-startup
artifact_type: synthesized-context
generated_by: tools/scripts/build_session_context.sh
generated_at: ${TIMESTAMP}
warning: do-not-edit-by-hand
---

# Session Context — Tenet (Codex Edition)

Generated by \`tools/scripts/build_session_context.sh --codex\`.
**Do not edit by hand.** Edit source files in \`core/\` and \`memory/\` instead.

**This is the full Codex variant.** All doctrine files verbatim so that Codex,
Aider, and Gemini CLI have the complete imperative text they need to hold the
same operational floor as Claude Code.

For Claude Code, use \`memory/session-context.md\` (slim) — Claude's intrinsic
discipline and on-demand file reading make verbatim repetition wasteful.

---

HEADER

        for f in $REQUIRED_DOCTRINE; do
            divider "$f"
            cat "$ROOT/$f"
        done

        append_operational "$ROOT"

        printf '\n\n---\n_end of synthesized context (Codex full edition)_\n'
    } > "$TMP_CODEX"

    mv "$TMP_CODEX" "$OUT_CODEX"
    LINES=$(wc -l < "$OUT_CODEX")
    BYTES=$(wc -c < "$OUT_CODEX")
    echo "Wrote $OUT_CODEX — $LINES lines, $BYTES bytes  [Codex full]"
fi

echo ""
echo "Next steps:"
echo "  Claude Code: session-context.md is auto-loaded via @-import in CLAUDE.md"
echo "  Codex:       update ~/.codex/config.toml to reference session-context-codex.md"
