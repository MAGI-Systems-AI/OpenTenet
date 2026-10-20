---
title: Team Operations
type: rule
domain: tenet
product: Tenet
audience: individual, small-team
owner: operator
status: active
updated: 2026-10-19
version: v1.0
tags:
  - team
  - lanes
  - handoffs
  - operating-rule
artifact_type: operating-rule
---

# Team Operations

> **Applies in team mode only.** A workspace is in team mode when `team/members/` holds at least one member file
> (`team/members/{slug}.md`, anything other than `members-map.md`). In a solo workspace every rule below is inert —
> skip this file.

Tenet's doctrine was written for one operator. With several people (and their AI CLIs) in one repo, three new
failure modes appear: two people edit the same paths at once, work changes hands without its context, and nobody
can say who answers for a given area. The team layer prevents those with three primitives: a **roster** (who is
here), **operational lanes** (who answers for which paths), and **handoffs** (how responsibility moves).

## Identity

- **The AI acts for exactly one member per session** — the one named in the session prompt (`I am {member}`). It never acts as, signs as, or accepts a handoff on behalf of another member.
- If the session has no member named and the workspace is in team mode, ask who you are working for before any write.

## Lanes

A lane is a standing area of responsibility: `team/lanes/{slug}.md` with frontmatter `lane`, `owner`, `backup`,
`lane_status`, `scope`, and a charter body (`templates/lane-template.md`).

1. **One driver per lane.** `owner:` is the only person who decides inside the lane's scope. `backup:` covers when the owner is `away`.
2. **Scopes do not overlap.** Two `active` or `blocked` lanes may not claim the same path. `bin/tenet-lane check` enforces it.
3. **Check before you edit.** BEFORE editing a file, run `bin/tenet-lane whose <path>`. If it is in an `active` or `blocked` lane owned by someone other than the session's member, do not edit it — ask the owner, or propose the change in a PR they review. `paused` and `closed` lanes do not hold their scope; unowned paths are free.
4. **Doctrine is everybody's.** `core/` changes need a reviewer who is not the author, whatever lane they touch.
5. **Status is honest.** A lane waiting on someone is `blocked` with a `## Blockers` entry naming who unblocks; a lane nobody is driving is `paused`, not `active`.
6. **Owners change only by handoff.** Edit `owner:` only after the receiver accepts a handoff entry in the lane's `## Handoffs` (format: `team/conventions.md`). An unaccepted handoff has not happened.

## WORK notes in team mode

Add two frontmatter fields to every Standard or Deep WORK note:

```yaml
owner: {member-slug}        # who is doing the task
lane: {lane-slug | none}    # the lane it belongs to
```

A WORK note in another member's lane is legitimate only when that lane's owner asked for it or accepted it; say so
in `## Decisions`.

## LEARN routing additions

| Discovery type | Target |
|----------------|--------|
| Gotcha specific to this team's environment | `team/discoveries.md` (`TD-N`) |
| Lane state that the next session needs | the lane file's `## Current state` |
| Responsibility moving between members | the lane file's `## Handoffs` |

Portable failure modes still go to `knowledge/domain/anti-patterns.md` — with a one-line pointer in `team/discoveries.md`.

## Session start and close

- Start with `team/prompts/member-morning.md`; close with `team/prompts/member-close.md`.
- The roster and the lanes map are synthesized into `memory/session-context.md`, so every session starts knowing who owns what.

## Validation

`bin/tenet-lane check` fails when: a lane's `lane:` differs from its filename; its owner or backup is not a member;
its owner is `alumni` while the lane is active; `lane_status` is not one of `active | blocked | paused | closed`;
`scope` is empty; two held lanes overlap; or a lane file is missing from `team/lanes/lanes-map.md`. CI runs it on
every push.
