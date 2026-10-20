---
title: Lane — {Lane Name}
type: reference
domain: tenet
product: Tenet
audience: team
owner: {member-slug}
status: active
updated: YYYY-MM-DD
tags:
  - team
  - lane
artifact_type: lane-charter
lane: {lane-slug}
backup: {member-slug | none}
lane_status: active
scope:
  - projects/{name}/
work_note: memory/work/{slug}.md
---

# Lane — {Lane Name}

Copy to `team/lanes/{lane-slug}.md` and add a row to `team/lanes/lanes-map.md`. The `lane:` field must equal the
filename slug; `owner:` is the driver and must be a member slug. `scope` entries are repo-relative: a trailing `/`
means the whole directory, anything else is a glob (`tools/*_sync.py`). Active and blocked lanes may not overlap.

## Purpose

(One or two sentences: what this lane answers for, and the outcome it keeps true.)

## Scope

- **Owns:** (the paths in `scope:`, in plain words)
- **Shares with:** (other lanes or paths it touches but does not own — edit those through their owner)
- **Out of scope:** (what people might assume is here but is not)

## Duties

- (Recurring responsibilities — e.g. "triage new issues weekly", "cut the monthly release")

## Interfaces

| With lane / person | What passes between |
|--------------------|---------------------|

## Definition of done

(For a time-boxed lane: the end state that closes it. For a standing lane: "standing".)

## Current state

(Two or three lines, rewritten at every member-close.)

## Blockers

<!-- - {YYYY-MM-DD} — {what} — unblocked by {member or outside party} -->

## Handoffs

<!-- Append entries in the format from team/conventions.md → Handoff contract. -->
