---
title: Member Close
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
  - session-close
artifact_type: session-prompt
---

# Member Close

Session-close routine for a team member. Invoke it with one line:

```
Read team/prompts/member-close.md and follow it as the authoritative session-close routine. I am {member-slug}.
```

## Step 1 — Update the WORK note

For each WORK note this member touched today (`owner: {member}`), make sure it says:

- **What changed** this session
- **Where it stands** — not started / in progress / blocked / done
- **Blockers** — and who can unblock each
- **Next** — the first 1–3 actions on resume
- **Restart state** — enough that any teammate can pick it up cold

## Step 2 — Update owned lanes

For each lane this member owns (`bin/tenet-lane list`):

- Rewrite `## Current state` in two or three lines.
- If the lane is now waiting on someone, set `lane_status: blocked` and add a `## Blockers` entry naming who unblocks.
- If the member is handing the lane off, append the handoff entry from `team/conventions.md` — the lane does not change owner until the receiver accepts.

Then run `bin/tenet-lane check`. Fix what it reports before committing.

## Step 3 — Discoveries

If today revealed a gotcha specific to this team's environment, add a `TD-N` entry to `team/discoveries.md`
(portable failure modes go to `knowledge/domain/anti-patterns.md`).

## Step 4 — Commit and push the personal branch

Only with the member's go-ahead in this session:

```sh
git add -A
git commit -m "close: {member} — {one-line summary}"
git push origin HEAD
```

Report the branch name and commit hash. Never push to `main`; merging happens through a reviewed PR.

## Do not

- Do not hand-edit generated files (`memory/session-context*.md`, `memory/skills-catalog.md`).
- Do not change the `owner:` of a lane without an accepted handoff.
- Do not commit to `main` or merge your own PR.

## Checklist

- [ ] WORK notes updated
- [ ] Owned lanes' current state, blockers and handoffs updated
- [ ] `bin/tenet-lane check` passes
- [ ] Discoveries routed
- [ ] Personal branch committed and pushed (with the member's go-ahead)
