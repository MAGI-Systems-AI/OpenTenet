---
title: Core Map
type: map
domain: tenet
product: Tenet
audience: individual
owner: operator
status: active
updated: 2026-05-24
version: v1.0
tags:
  - core
  - map
  - navigation
  - doctrine-index
artifact_type: navigation-map
---

# Core Map

> Index of the `core/` doctrine files in recommended read order. Read top-to-bottom on first contact with the workspace; read on-demand thereafter when the task pattern calls for it.

## Recommended Read Order

Read these five in order — they form the operational floor.

| # | File | One-line description | Why read it |
|---|------|---------------------|-------------|
| 1 | [`constitution.md`](./constitution.md) | Hard NEVER / ALWAYS / BEFORE imperatives | The non-negotiable defaults. Every other doctrine file assumes the constitution is in force. |
| 2 | [`ALGORITHM.md`](./ALGORITHM.md) | The four-phase loop: OBSERVE → PLAN → EXECUTE → VERIFY | The universal operating loop. Every non-trivial task runs through these phases. |
| 3 | [`ISC.md`](./ISC.md) | Ideal State Criteria — one-binary-tool-probe acceptance criteria | The primitive that makes the Algorithm verifiable. Without ISCs, "done" is a feeling. |
| 4 | [`verification-doctrine.md`](./verification-doctrine.md) | Required probes per artifact type | What evidence counts as passing an ISC. The substitute for runtime hooks. |
| 5 | [`effort-tiering.md`](./effort-tiering.md) | Quick / Standard / Deep tier rules | When to run the Algorithm at all and how much ceremony to apply. Gates how the loop fires. |

## On-Demand Reference

Read these when the task pattern matches.

| File | When to read it |
|------|-----------------|
| [`decision-rules.md`](./decision-rules.md) | When weighing tradeoffs — reversibility, uncertainty reduction, what to surface vs. handle silently |
| [`front-matter-standard.md`](./front-matter-standard.md) | When creating or editing a markdown file in `core/`, `memory/`, `projects/`, `knowledge/`, `templates/`, or `skills/` |
| [`AI_CLI_ADAPTERS.md`](./AI_CLI_ADAPTERS.md) | When wiring a new coding-assistant CLI (Codex, Claude Code, Gemini, Cursor, Aider, etc.) — includes Codex critical pitfalls |

## How These Files Compose

- The **constitution** sets the hard floor: what NEVER happens, what ALWAYS happens, what gets checked BEFORE.
- The **Algorithm** is the loop that everything runs through.
- **ISC** is the primitive the Algorithm uses to measure progress and define "done".
- **Verification doctrine** is what makes ISC completion auditable — the evidence standard.
- **Effort tiering** gates the loop: not every task earns the ceremony, and not every task escapes it.
- **Decision rules**, **front matter**, and **AI CLI adapters** are tactical references — read when the matching task surfaces.

## Where Doctrine Files Get Synthesized

The five core files plus `memory/identity.md`, `memory/current-focus.md`, `LAUNCHER.md`, `skills/skills-map.md`, and `active-work-map.md` are catenated by `tools/scripts/build_session_context.sh` into `memory/session-context.md`. That synthesized file is what your coding-assistant CLI reads at session start. **When you edit any source file in this list, regenerate the session context** — otherwise the synthesized file drifts from its sources.
