---
title: Team Map
type: map
domain: tenet
product: Tenet
audience: team
owner: team
status: active
updated: 2026-10-19
tags:
  - team
  - map
  - navigation
artifact_type: navigation-map
---

# Team Map

The team layer is **optional**. A workspace is in **team mode** once `team/members/` holds at least one member
file; until then everything here is inert and Tenet behaves as a solo workspace. The rules live in
[`core/team-operations.md`](../core/team-operations.md).

## Files

| File | What it holds |
|------|---------------|
| [roster.md](./roster.md) | Who is on the team, their role, and the lanes they drive |
| [conventions.md](./conventions.md) | Branches, review, generated files, the handoff contract |
| [discoveries.md](./discoveries.md) | Team-specific environment gotchas, written at LEARN |
| [members/members-map.md](./members/members-map.md) | One context file per member |
| [lanes/lanes-map.md](./lanes/lanes-map.md) | Operational lanes: owner, scope, status |
| [prompts/member-morning.md](./prompts/member-morning.md) | Session-start routine for a member |
| [prompts/member-close.md](./prompts/member-close.md) | Session-close routine for a member |

## Turning team mode on

1. Copy `templates/member-template.md` to `team/members/{slug}.md` for each person and add them to [roster.md](./roster.md) and [members-map.md](./members/members-map.md).
2. Copy `templates/lane-template.md` to `team/lanes/{slug}.md` for each standing area of work and add it to [lanes-map.md](./lanes/lanes-map.md).
3. Run `bin/tenet-lane check` — it validates owners, statuses and scope overlaps.
4. Run `tools/scripts/build_session_context.sh` so the roster and lanes load at session start.
