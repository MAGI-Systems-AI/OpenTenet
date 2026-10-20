---
title: Lanes Map
type: map
domain: tenet
product: Tenet
audience: team
owner: team
status: active
updated: 2026-10-19
tags:
  - team
  - lanes
  - map
artifact_type: navigation-map
---

# Lanes Map

An **operational lane** is a standing area of responsibility: one owner (the driver), a backup, a scope of repo
paths, a status, and a charter. Projects say *what* is being built; lanes say *who answers for which paths and
ongoing duties* — a lane can cover one project, several, or an operational duty such as releases or security
review. Rules: `core/team-operations.md`.

One file per lane, `team/lanes/{slug}.md`, copied from `templates/lane-template.md`. The machine view:

```sh
bin/tenet-lane list              # every lane: slug, owner, backup, status, scope
bin/tenet-lane whose <path>      # which lane owns a path (run before editing)
bin/tenet-lane show <slug>       # print one lane charter
bin/tenet-lane check             # validate owners, statuses, scope overlaps
```

## Lanes

| Lane | Owner | Backup | Status | Scope | Charter |
|------|-------|--------|--------|-------|---------|

> No lanes yet. Add a row per lane; `bin/tenet-lane check` fails if a lane file is missing from this table.

## Status values

| `lane_status` | Means |
|---------------|-------|
| `active` | Owner is driving; scope is held — others ask before editing |
| `blocked` | Owner is driving but waiting on someone; `## Blockers` names who unblocks |
| `paused` | Nobody is driving; scope is not held, but read the charter before editing |
| `closed` | Lane retired; kept for history; scope released |
