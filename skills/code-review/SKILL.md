---
name: code-review
description: Use when reviewing changes for bugs, regressions, edge cases, missing tests, risky assumptions, or maintainability issues. Prioritize findings over summary.
---

# Code Review

Review with a defect-finding mindset.

## Workflow

1. Understand the intended behavior change.
2. Look for correctness risks first.
3. Check interfaces, state transitions, and error handling.
4. Look for missing or outdated tests.
5. Only after findings, provide a short summary.

## What to prioritize

- broken behavior
- data loss or corruption risk
- concurrency or state bugs
- auth or security gaps
- silent failure modes
- missing test coverage for changed logic

## Output shape

- findings ordered by severity
- open questions or assumptions
- brief summary

## Guardrails

- avoid style-only comments unless they hide real risk
- cite files and lines when possible
- say explicitly when no findings were found
