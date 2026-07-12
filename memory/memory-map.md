---
title: Memory Map
type: map
domain: tenet
product: Tenet
audience: individual
owner: operator
status: active
updated: 2026-05-24
tags:
  - memory
  - map
  - navigation
artifact_type: navigation-map
---

# Memory Map

Index of everything in `memory/`. The AI reads `session-context.md` at session start; everything else here is loaded on-demand or written during work.

## Files loaded at every session

| File | Purpose |
|------|---------|
| `session-context.md` | Auto-generated synthesis of all sources below. Do not edit by hand. |
| `session-context-local.md` | Condensed variant for local / small-context models. Auto-generated. |
| `session-context-codex.md` | Full-doctrine variant for Codex / Aider / Gemini CLI. Auto-generated. |
| `identity.md` | Who you are, what you work on, how you communicate. |
| `current-focus.md` | This week's priorities and blockers. |
| `goals.md` | Mission, active goals, quarterly commitments. |
| `skills-catalog.md` | Auto-generated one-line-per-skill index. |

## Directories written during work

| Directory | What goes here |
|-----------|---------------|
| `work/` | WORK notes (`{slug}.md`) — one per non-trivial task. Created at OBSERVE, updated through VERIFY, archived at complete. |
| `learnings/` | Captured insights from the VERIFY reflection step. `memory/learnings/{date}_{slug}.md` |
| `decisions/` | Decision records for future reference. `memory/decisions/{date}_{slug}.md` |
| `session-summaries/` | Session closure notes. `memory/session-summaries/{date}_{slug}.md` |

## Regenerating session-context.md

Run after editing any source file:

```sh
tools/scripts/build_session_context.sh
```

Source files (in synthesis order):
- `core/constitution.md`
- `core/ALGORITHM.md`
- `core/ISC.md`
- `core/effort-tiering.md`
- `core/verification-doctrine.md`
- `core/decision-rules.md`
- `memory/identity.md`
- `memory/current-focus.md`
- `memory/goals.md`
- `LAUNCHER.md`
- Skills catalog (appended by `tools/scripts/skills_index.sh`)
