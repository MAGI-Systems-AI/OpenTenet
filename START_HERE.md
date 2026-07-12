---
title: Start Here
type: guide
domain: tenet
product: Tenet
audience: individual
owner: operator
status: active
updated: 2026-05-24
tags:
  - onboarding
  - startup
artifact_type: guide
---

# Start Here

Welcome to Tenet. This is a personal AI workspace — a scaffold that gives any LLM CLI a consistent operating context, a disciplined algorithm for non-trivial work, and a memory system that survives session resets.

## 5-minute orientation

### 1. What you just cloned

```
core/           ← doctrine: the rules your AI follows
memory/         ← your personal context: who you are, what you're working on
skills/         ← reusable AI workflows (planning, research, code review)
projects/       ← one folder per active workstream
knowledge/      ← reference material you curate over time
templates/      ← starter shapes for work notes, learnings, decisions
bin/tenet-skill   ← CLI for discovering and loading skills
bootstrap.sh    ← one-command setup
```

### 2. How it works

Your LLM CLI reads `memory/session-context.md` at session start. That file is a synthesized block containing the constitution, the 4-phase algorithm, the ISC doctrine, your identity, your goals, and the skills catalog. Every vendor (Claude Code, Gemini, Cursor, Aider, Codex) points at this same file through its own wiring file at the repo root.

When you work on something non-trivial, the algorithm kicks in:

```
OBSERVE → PLAN → EXECUTE → VERIFY
```

Each non-trivial task gets a WORK note at `memory/work/{slug}.md`. The WORK note is the system of record — it carries the intent, the acceptance criteria (ISCs), the evidence, and the reflection. Sessions can resume from it without re-explaining context.

### 3. What to fill in

Three seed files need your content before the workspace is personalized:

- `memory/identity.md` — who you are, what you do, how you like to work
- `memory/current-focus.md` — what you're working on this week
- `memory/goals.md` — your mission and active goals

After editing any of these, regenerate the session context:

```sh
tools/scripts/build_session_context.sh
```

### 4. What "LLM agnostic" means here

The doctrine never branches by vendor. The only vendor-specific files are the thin wiring files at the repo root (`CLAUDE.md`, `GEMINI.md`, `.cursorrules`, `.aider.conf.yml`, `.github/copilot-instructions.md`). They all point to the same `memory/session-context.md`. Switch vendors anytime — the workspace behavior is the same.

### 5. The security layer

The pre-commit hook at `.githooks/pre-commit` scans every staged commit for 16 secret patterns (API keys, private keys, tokens, JWTs). It blocks the commit if anything matches. Installed automatically by `bootstrap.sh`.

## Where things go

| What | Where |
|------|-------|
| Active task | `memory/work/{slug}.md` |
| Project workstream | `projects/{name}/` |
| Captured insight | `memory/learnings/{date}_{slug}.md` |
| Decision to remember | `memory/decisions/{date}_{slug}.md` |
| Reference material | `knowledge/collections/{topic}.md` |
| New skill | `skills/{name}/SKILL.md` |

## Verify the wiring

```sh
./bootstrap.sh  # if you haven't already
```

Then ask your LLM: *"What's in memory/session-context.md? Summarize the rules I'm operating under."*

Expected: it names the 4 phases (OBSERVE, PLAN, EXECUTE, VERIFY), the ISC concept, the constitution rules, and the 3 skills.
