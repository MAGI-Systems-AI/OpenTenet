---
title: Team Conventions
type: rule
domain: tenet
product: Tenet
audience: team
owner: team
status: active
updated: 2026-10-19
tags:
  - team
  - conventions
  - branches
  - handoffs
artifact_type: operating-rule
---

# Team Conventions

Applies in team mode only (see `core/team-operations.md`). Solo workspaces can ignore this file.

## Branches

`main` is the integration branch. Nobody commits to it directly.

- Daily work: `{member}/{YYYY-MM-DD}`, cut from a freshly fetched `origin/main`.
- Lane work that spans days: `{member}/{lane}-{topic}`.
- Continuing a branch: `git fetch origin && git rebase origin/main`. If the rebase is not clean, stop and report — do not force a stale base.

## Review

- Every merge to `main` goes through a pull request reviewed by a member who is **not** the author.
- A change inside another member's lane scope also needs that lane owner's review.
- A change to `core/` (doctrine) needs a reviewer and a re-baselined doctrine manifest (`tools/scripts/verify_doctrine_integrity.py --update`) in the same PR.
- CI must be green. Do not merge a red build.

## Generated files

`memory/session-context.md`, `memory/session-context-codex.md` and `memory/skills-catalog.md` are generated.
Two members regenerating them on separate branches always conflicts. Rule: after rebasing on `main`, if one of
these conflicts, take `main`'s copy and regenerate — never hand-merge a generated file.

## Handoff contract

A lane or a task changes hands only with a written handoff, appended to the lane file's `## Handoffs` (or the
WORK note for a one-off task):

```
### {YYYY-MM-DD} — {from} → {to}
- State: {not started | in progress | blocked | done}
- Next: {first 1–3 actions}
- Open risks: {what could bite the receiver}
- WORK note: {path}
- Accepted: {receiver confirms — yes / date}
```

A handoff that the receiver has not accepted has not happened; the sender still owns the lane.

## Vocabulary

| Term | Meaning |
|------|---------|
| **Team mode** | `team/members/` holds ≥1 member file |
| **Lane** | A standing area of responsibility: one owner, a path scope, a status, a charter |
| **Lane scope** | The repo paths a lane owns (`dir/` prefixes or globs), listed in its frontmatter |
| **Driver** | The lane owner — one per lane at a time |
| **Handoff** | The written transfer above; required to change a lane's owner |
| **Personal branch** | `{member}/{date}` or `{member}/{lane}-{topic}` |
