---
title: Work Notes
type: reference
domain: tenet
product: Tenet
audience: individual
owner: operator
status: active
updated: 2026-05-24
tags:
  - work
  - readme
  - convention
artifact_type: directory-readme
---

# Work Notes (`memory/work/`)

A WORK note is the system of record for a single non-trivial task. One file per task. Slug is kebab-case, short, and descriptive (`auth-token-rotation`, `ingest-pdf-pipeline`).

## Required sections

```markdown
# Task title

## Intent
One sentence restating what was actually asked for.

## Effort
Quick | Standard | Deep

## Criteria
- [ ] ISC-1: criterion — what tool probe returns yes/no on this
- [ ] ISC-2: Anti: what MUST NOT happen

## Plan
D1: [explicit sub-task]
D2: ...

## Risks
- Riskiest assumption: ...
- Premortem: ...

## Verification
ISC-1: grep — "pattern found in file:line" (evidence)
ISC-2: curl -i — 200 OK, body contains expected field

## Reflection
What would I do differently, or what surprised me.

## Decisions
Timestamped log of choices and dead ends.
```

## Frontmatter

```yaml
---
task: Short description
slug: task-slug
phase: observe | plan | execute | verify | complete
tier: quick | standard | deep
reasoning_effort: low | medium | high
started: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

## Lifecycle

- **Created at OBSERVE** of any Standard or Deep task
- **Updated through every phase**
- **Archived at complete** — stay in the repo as durable record; never deleted
