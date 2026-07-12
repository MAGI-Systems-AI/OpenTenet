# Tenet — secret pattern scanner (CI-safe diff scanner)
# tools/scripts/secret_scan_diff.sh — run the Tenet secret-pattern scan against
# the diff between two git refs. Used by CI workflows (GitHub Actions, Azure
# Pipelines) and also runnable locally to vet a feature branch before pushing.
#
# Usage:
#   tools/scripts/secret_scan_diff.sh [BASE_REF [HEAD_REF]]
#
# Defaults:
#   BASE_REF  origin/main
#   HEAD_REF  HEAD
#
# Exit codes:
#   0  no high-confidence secret patterns found in added lines
#   1  one or more patterns matched (CI fails the build, human re-runs locally)
#
# This script intentionally duplicates the regex set in .githooks/pre-commit
# rather than sourcing it, so the hook remains a self-contained file that
# works on a fresh clone before this script is even present. If you change a
# pattern in one file, change it in the other — they must stay in sync.

set -eu

BASE_REF="${1:-origin/main}"
HEAD_REF="${2:-HEAD}"

# Resolve BASE_REF to a commit; if origin/main isn't available (e.g. shallow
# clone in CI), fall back to the merge-base via the previous commit.
if ! git rev-parse --verify --quiet "$BASE_REF" >/dev/null 2>&1; then
    if git rev-parse --verify --quiet "HEAD~1" >/dev/null 2>&1; then
        BASE_REF="HEAD~1"
    else
        # No prior commit to diff against — this is a fresh repo on its first
        # commit. There is no diff surface, so nothing for the secret scan to
        # flag. Exit clean rather than fail the build.
        echo "secret_scan_diff: no prior commit available to diff against (single-commit history); nothing to scan."
        exit 0
    fi
fi

DIFF="$(git diff "$BASE_REF...$HEAD_REF" --no-color || true)"
if [ -z "$DIFF" ]; then
    echo "secret_scan_diff: no diff between $BASE_REF and $HEAD_REF; nothing to scan."
    exit 0
fi

FOUND=0

# AWS-style keys — long-lived AKIA and short-lived STS ASIA
if printf '%s' "$DIFF" | grep -qE '^\+.*(AKIA|ASIA)[0-9A-Z]{16}'; then
    echo "FAIL — possible AWS access key (AKIA/ASIA…)" >&2
    FOUND=1
fi

# OpenAI-style keys (sk-...)
if printf '%s' "$DIFF" | grep -qE '^\+.*sk-[A-Za-z0-9]{32,}'; then
    echo "FAIL — possible OpenAI-style API key (sk-…)" >&2
    FOUND=1
fi

# Anthropic-style keys (sk-ant-...)
if printf '%s' "$DIFF" | grep -qE '^\+.*sk-ant-[A-Za-z0-9_-]{20,}'; then
    echo "FAIL — possible Anthropic API key (sk-ant-…)" >&2
    FOUND=1
fi

# PEM private key blocks
if printf '%s' "$DIFF" | grep -qE '^\+.*-----BEGIN ((RSA|DSA|EC|OPENSSH|PGP) )?PRIVATE KEY-----'; then
    echo "FAIL — PEM private key block detected" >&2
    FOUND=1
fi

# Slack tokens
if printf '%s' "$DIFF" | grep -qE '^\+.*xox[abprs]-[0-9A-Za-z]{10,}'; then
    echo "FAIL — possible Slack token (xox?-…)" >&2
    FOUND=1
fi

# GitHub classic PAT (ghp_/gho_/ghs_/ghu_)
if printf '%s' "$DIFF" | grep -qE '^\+.*gh[opsu]_[A-Za-z0-9]{36,}'; then
    echo "FAIL — possible GitHub classic personal access token (gh?_…)" >&2
    FOUND=1
fi

# GitHub fine-grained PAT (github_pat_…) — newer format, distinct prefix
if printf '%s' "$DIFF" | grep -qE '^\+.*github_pat_[A-Za-z0-9_]{22,}'; then
    echo "FAIL — possible GitHub fine-grained personal access token (github_pat_…)" >&2
    FOUND=1
fi

# GitLab PAT (glpat-…)
if printf '%s' "$DIFF" | grep -qE '^\+.*glpat-[A-Za-z0-9_-]{20,}'; then
    echo "FAIL — possible GitLab personal access token (glpat-…)" >&2
    FOUND=1
fi

# Azure storage / SQL connection strings (AccountKey=…)
if printf '%s' "$DIFF" | grep -qE '^\+.*AccountKey=[A-Za-z0-9+/]{40,}={0,2}'; then
    echo "FAIL — possible Azure storage AccountKey in connection string" >&2
    FOUND=1
fi

# GCP API key (AIza… — 39 chars total)
if printf '%s' "$DIFF" | grep -qE '^\+.*AIza[0-9A-Za-z_-]{35}'; then
    echo "FAIL — possible GCP API key (AIza…)" >&2
    FOUND=1
fi

# GCP service-account JSON private_key field
if printf '%s' "$DIFF" | grep -qE '^\+.*"private_key"[[:space:]]*:[[:space:]]*"-----BEGIN'; then
    echo "FAIL — GCP service-account JSON with embedded private_key" >&2
    FOUND=1
fi

# Stripe live/test keys
if printf '%s' "$DIFF" | grep -qE '^\+.*(sk|pk|rk)_(live|test)_[A-Za-z0-9]{24,}'; then
    echo "FAIL — possible Stripe key (sk_/pk_/rk_ live/test)" >&2
    FOUND=1
fi

# Twilio Account SID (AC + 32 hex)
if printf '%s' "$DIFF" | grep -qE '^\+.*AC[0-9a-f]{32}'; then
    echo "FAIL — possible Twilio Account SID (AC…)" >&2
    FOUND=1
fi

# Twilio auth token (32 hex, contextualised with 'twilio' nearby to reduce FPs)
if printf '%s' "$DIFF" | grep -qiE '^\+.*twilio.*[[:space:]:=]+[0-9a-f]{32}([^0-9a-f]|$)'; then
    echo "FAIL — possible Twilio auth token near 'twilio' reference" >&2
    FOUND=1
fi

# JWT — header.payload.signature shape (eyJ… prefix)
if printf '%s' "$DIFF" | grep -qE '^\+.*eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}'; then
    echo "FAIL — possible JWT (three base64 segments separated by dots, eyJ… prefix)" >&2
    FOUND=1
fi

if [ "$FOUND" -eq 1 ]; then
    echo "" >&2
    echo "secret_scan_diff: BLOCKED — fix the leaks above before merging." >&2
    echo "If a false positive, please open an issue with the matched line so the pattern can be tightened." >&2
    exit 1
fi

echo "secret_scan_diff: no high-confidence secret patterns in $BASE_REF...$HEAD_REF"
exit 0
