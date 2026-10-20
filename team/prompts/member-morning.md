---
title: Member Morning
type: guide
domain: tenet
product: Tenet
audience: team
owner: team
status: active
updated: 2026-10-19
tags:
  - team
  - prompt
  - session-start
artifact_type: session-prompt
---

# Member Morning

Session-start routine for a team member. Invoke it from any AI CLI with one line:

```
Read team/prompts/member-morning.md and follow it as the authoritative session-start routine. I am {member-slug}.
```

The member slug in that line is who you act for this session. You never act as another member.

## Step 1 — Load context

1. Read `memory/session-context.md` (doctrine, focus, roster, lanes).
2. Read `team/members/{member}.md`. If it does not exist, stop: say the member is not on the roster and ask.
3. Run `bin/tenet-lane list` and note the lanes this member owns or backs up.

## Step 2 — Branch

You must not work on `main`.

```sh
git fetch origin
git checkout -b {member}/{YYYY-MM-DD} origin/main      # new day
# or, continuing a branch:
git rebase origin/main
```

If the rebase is not clean, stop and report. If a generated file conflicts, follow `team/conventions.md` → Generated files.

## Step 3 — Pick up where the last session ended

1. For each lane this member owns: read the lane file's `## Current state`, `## Blockers` and any unaccepted entry in `## Handoffs` addressed to them.
2. Read the most recent WORK note with `owner: {member}` in `memory/work/`.
3. A handoff addressed to this member that is not yet accepted: show it and ask whether to accept.

## Step 4 — Brief the member

Report in this order, short:

- **Lanes:** each owned lane — status, the next action from its charter.
- **Waiting on you:** unaccepted handoffs, blockers this member is named to unblock, PRs awaiting their review.
- **Today:** the first task, its lane, and its WORK note path.

## Checklist

- [ ] Session context read
- [ ] Member file read
- [ ] On a personal branch, current with `origin/main`
- [ ] Owned lanes and pending handoffs reviewed
- [ ] Brief delivered
