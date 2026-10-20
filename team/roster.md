---
title: Team Roster
type: reference
domain: tenet
product: Tenet
audience: team
owner: team
status: active
updated: 2026-10-19
tags:
  - team
  - roster
  - members
artifact_type: team-reference
---

# Team Roster

> Empty until you add your team. One row per person; the `Member` slug must match `team/members/{slug}.md`.
> `bin/tenet-lane members` prints the machine view (from member-file frontmatter) — keep this table in step with it.

| Member | Name | Role | Lanes driven | Backup on | Status |
|--------|------|------|--------------|-----------|--------|
| <!-- slug --> | <!-- Full name --> | <!-- e.g. maintainer, reviewer --> | <!-- lane slugs --> | <!-- lane slugs --> | <!-- active / away / alumni --> |

## Roles

| Role | Means |
|------|-------|
| **Member** | Works in this workspace; owns their own WORK notes and personal branches |
| **Lane owner** | The one driver of a lane: decides within its scope, keeps its charter current, accepts or refuses edits from others |
| **Backup** | Covers a lane when its owner is away; becomes owner only through a recorded handoff |
| **Reviewer** | Any member other than the author; required on every PR to `main` and on every `core/` change |

## Changing the roster

- **Joining:** add the member file, the row above, and the members-map row in one change.
- **Leaving:** set the member file `member_status: alumni`, mark the row `alumni`, and hand off every lane they drive first (`bin/tenet-lane check` fails while an alumni member still owns an active lane).
