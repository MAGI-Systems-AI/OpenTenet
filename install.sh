#!/bin/sh
# install.sh — create a new Tenet workspace in one command.
#
#   curl -fsSL https://raw.githubusercontent.com/MAGI-Systems-AI/OpenTenet/main/install.sh | sh
#   curl -fsSL https://raw.githubusercontent.com/MAGI-Systems-AI/OpenTenet/main/install.sh | sh -s -- my-workspace
#
# Or, from a checkout:   sh install.sh [DIR] [--ref REF] [--no-commit]
#
# What it does:
#   1. Checks for git and Python 3.9+
#   2. Downloads Tenet into DIR (default: ./tenet-workspace)
#   3. Makes it YOUR repo: fresh git history, no remote pointing back at OpenTenet
#   4. Runs ./bootstrap.sh (session context, skills catalog, pre-commit hook)
#   5. Makes an initial commit so you start from a clean tree
#
# It never prompts, never uses sudo, and only writes inside DIR.
# Overrides: TENET_REPO (source repo URL), TENET_REF (branch or tag).

set -eu

# Everything runs inside main(), called on the last line, so a partially
# downloaded script (curl | sh cut off mid-stream) cannot run half the steps.
main() {
    REPO="${TENET_REPO:-https://github.com/MAGI-Systems-AI/OpenTenet.git}"
    REF="${TENET_REF:-main}"
    DIR=""
    COMMIT=1

    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help) usage; exit 0 ;;
            --ref) [ $# -ge 2 ] || die "--ref needs a value"; REF="$2"; shift 2 ;;
            --ref=*) REF="${1#--ref=}"; shift ;;
            --no-commit) COMMIT=0; shift ;;
            -*) die "unknown option: $1 (try --help)" ;;
            *) [ -z "$DIR" ] || die "only one target directory allowed"; DIR="$1"; shift ;;
        esac
    done
    DIR="${DIR:-tenet-workspace}"

    say "Tenet installer"
    echo ""

    # ----- prerequisites -----
    command -v git >/dev/null 2>&1 || die "git is required. Install it, then re-run."
    PY=""
    for cand in python3 python; do
        if command -v "$cand" >/dev/null 2>&1 &&
           "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
            PY="$cand"; break
        fi
    done
    [ -n "$PY" ] || die "Python 3.9 or newer is required (as python3). Install it, then re-run."
    step "git $(git --version | awk '{print $3}'), $("$PY" -c 'import platform; print("python " + platform.python_version())')"

    # ----- target directory -----
    if [ -e "$DIR" ]; then
        [ -d "$DIR" ] || die "$DIR exists and is not a directory."
        if [ -n "$(ls -A "$DIR" 2>/dev/null)" ]; then
            die "$DIR already exists and is not empty. Pick a new directory name:
       sh install.sh my-tenet-workspace"
        fi
        CREATED=0
    else
        CREATED=1
    fi

    # ----- download -----
    step "downloading Tenet ($REF)"
    TMP_LOG="$(mktemp 2>/dev/null || echo "/tmp/tenet-install.$$")"
    trap 'on_fail' EXIT
    if ! git clone --quiet --depth 1 --branch "$REF" "$REPO" "$DIR" >"$TMP_LOG" 2>&1; then
        cat "$TMP_LOG" >&2
        die "could not download $REPO at $REF"
    fi
    SRC_SHA="$(git -C "$DIR" rev-parse --short HEAD)"
    DIR="$(cd "$DIR" && pwd)"

    # ----- make it the user's own repo -----
    step "starting a fresh git history (no link back to OpenTenet)"
    rm -rf "$DIR/.git"
    if ! git -C "$DIR" init --quiet -b main 2>/dev/null; then
        git -C "$DIR" init --quiet
        git -C "$DIR" symbolic-ref HEAD refs/heads/main
    fi

    # ----- bootstrap -----
    step "running bootstrap (session context, skills catalog, pre-commit hook)"
    if ! (cd "$DIR" && ./bootstrap.sh) </dev/null >"$TMP_LOG" 2>&1; then
        cat "$TMP_LOG" >&2
        die "bootstrap failed (output above)"
    fi

    # ----- initial commit -----
    COMMITTED=0
    if [ "$COMMIT" -eq 1 ]; then
        if [ -n "$(git -C "$DIR" config user.name 2>/dev/null)" ] &&
           [ -n "$(git -C "$DIR" config user.email 2>/dev/null)" ]; then
            step "making the initial commit"
            git -C "$DIR" add -A
            if git -C "$DIR" commit --quiet -m "Start Tenet workspace (from OpenTenet $SRC_SHA)" >"$TMP_LOG" 2>&1; then
                COMMITTED=1
            else
                cat "$TMP_LOG" >&2
                warn "initial commit failed; your files are in place, commit them yourself."
            fi
        else
            warn "git user.name / user.email not set, so no initial commit was made."
        fi
    fi

    trap - EXIT
    rm -f "$TMP_LOG"

    echo ""
    say "Done. Your Tenet workspace is ready:"
    echo "    $DIR"
    echo ""
    echo "Next:"
    echo "    cd \"$DIR\""
    echo "    claude      # or: gemini, aider, cursor . , Copilot Chat. Wiring files are already in place."
    echo ""
    echo "    Codex users, one extra step (edits ~/.codex/config.toml, makes a backup first):"
    echo "    $PY tools/scripts/install-codex-config.py"
    echo ""
    echo "Personalize it (optional, any time):"
    echo "    $PY dashboard/server.py    # local UI at http://localhost:3131"
    echo "    or edit memory/identity.md and memory/current-focus.md, then ./bootstrap.sh"
    echo ""
    echo "Check it loaded: ask your AI"
    echo "    \"What's in memory/session-context.md? Summarize the rules I'm operating under.\""
    echo "    It should name the six phases: OBSERVE, THINK, PLAN, EXECUTE, VERIFY, LEARN."
    if [ "$COMMIT" -eq 1 ] && [ "$COMMITTED" -eq 0 ]; then
        echo ""
        echo "Then save your starting point:"
        echo "    git config --global user.name \"Your Name\"; git config --global user.email you@example.com"
        echo "    git add -A && git commit -m \"Start Tenet workspace\""
    fi
}

usage() {
    cat <<'USAGE'
Usage: install.sh [DIR] [--ref REF] [--no-commit]

Create a new Tenet workspace in DIR (default: ./tenet-workspace).

  DIR          target directory; must not exist or must be empty
  --ref REF    branch or tag of OpenTenet to install (default: main)
  --no-commit  skip the initial commit
  -h, --help   show this help

Environment: TENET_REPO overrides the source repo URL, TENET_REF the ref.
USAGE
}

say()  { printf '==> %s\n' "$*"; }
step() { printf '  - %s\n' "$*"; }
warn() { printf '  ! %s\n' "$*" >&2; }
die()  { printf 'error: %s\n' "$*" >&2; exit 1; }

# On a failed run, remove only what this script created, then report.
on_fail() {
    status=$?
    if [ "$status" -ne 0 ] && [ -n "${DIR:-}" ] && [ -d "$DIR" ]; then
        if [ "${CREATED:-0}" -eq 1 ]; then
            rm -rf "$DIR"
        else
            find "$DIR" -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true
        fi
        printf 'Install did not finish; cleaned up %s.\n' "$DIR" >&2
    fi
    rm -f "${TMP_LOG:-}"
}

main "$@"
