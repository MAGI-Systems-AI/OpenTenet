---
title: Launcher
type: guide
domain: tenet
product: Tenet
audience: individual
owner: operator
status: active
updated: 2026-05-24
tags:
  - launcher
  - startup
  - session
artifact_type: guide
---

# Launcher

This is the machine-readable session anchor. The `bin/tenet-skill` CLI and `tools/scripts/build_session_context.sh` both detect the workspace root by finding this file.

## Session Bootstrap

**Preferred path:** read `memory/session-context.md`. That single file catenates the constitution, the 4-phase algorithm, the ISC doctrine, the verification doctrine, effort tiering, your identity, current focus, goals, and the skills catalog — in one deterministic block. Regenerate it after any change to its sources with `tools/scripts/build_session_context.sh`.

**Manual path (fallback when session-context.md is stale or absent):**

1. `LAUNCHER.md` ← you are here
2. `START_HERE.md`
3. `core/constitution.md` — hard NEVER/ALWAYS/BEFORE imperatives
4. `core/ALGORITHM.md` — the 4-phase operating loop
5. `core/ISC.md` — acceptance criteria doctrine
6. `core/effort-tiering.md` — Quick / Standard / Deep tier rules
7. `core/verification-doctrine.md` — required probes per artifact type
8. `memory/identity.md`
9. `memory/current-focus.md`
10. `memory/goals.md`

**Read on-demand:**

- `core/decision-rules.md` — tradeoff guidance
- `core/AI_CLI_ADAPTERS.md` — vendor wiring details and Codex pitfalls
- `core/front-matter-standard.md` — YAML frontmatter schema

## What This Workspace Is

A personal operating system for working with AI coding assistants. It keeps your context, work, and reusable methods in one durable place that any LLM CLI can read.

## What To Do First

1. Run `./bootstrap.sh` once after cloning (generates session context, installs hooks)
2. Fill in `memory/identity.md`, `memory/current-focus.md`, and `memory/goals.md`
3. Verify wiring: ask your LLM "What's in memory/session-context.md?"

## Why It Exists

Stronger than a single markdown note because structure, history, and reusable patterns stay separated, searchable, and recoverable across session resets.
