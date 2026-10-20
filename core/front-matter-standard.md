---
title: Front Matter Standard
type: rule
domain: tenet
product: Tenet
audience: individual
owner: operator
status: active
updated: 2026-10-19
version: v1.1
tags:
  - front-matter
  - yaml
  - metadata
artifact_type: operating-rule
---

# Front Matter Standard

Tenet uses two frontmatter schemas — one for durable doctrine and memory files, one for skills. The two are intentionally different because they serve different consumers: the standard schema is for files Tenet's tooling and you both read and route by metadata; the skills schema is for files an external coding-assistant CLI consumes and dispatches by `name` and `description`.

## Standard Schema — durable workspace files

Use this schema for all durable markdown files in `core/`, `memory/`, `projects/`, `knowledge/`, `templates/`, and `team/` (team variant below). Every field is mandatory:

```yaml
---
title: [human-readable title]
type: [rule | reference | memory | guide | map]
domain: tenet
product: Tenet
audience: individual
owner: operator
status: [active | draft | deprecated]
updated: [YYYY-MM-DD]
tags:
  - [tag1]
  - [tag2]
artifact_type: [operating-rule | durable-memory | operational-memory | guide | navigation-map | integration-guide]
---
```

**Field definitions:**

| Field | Purpose |
|-------|---------|
| `title` | Human-readable title; appears in indices and navigation |
| `type` | Coarse classification — what kind of file this is |
| `domain` | Always `tenet` for this workspace |
| `product` | Always `Tenet` |
| `audience` | Always `individual` for this workspace |
| `owner` | Always `operator` (you) |
| `status` | Lifecycle marker — `active` for live docs, `draft` for work-in-progress, `deprecated` for files kept for history |
| `updated` | ISO date of last meaningful change. Update on edit. |
| `tags` | Keywords for search and routing — keep to 3–6 specific terms |
| `artifact_type` | Fine-grained classification — what role this file plays in the doctrine |

## Team Variant — files under `team/`

Files in `team/` (and copies of `templates/member-template.md` / `templates/lane-template.md`) use the standard
schema with two changes: `audience: team`, and `owner:` is `team` for shared files or a member slug for a member
file or a lane (where it names the lane's driver). Member and lane files add machine-read fields that
`bin/tenet-lane` validates:

| File | Extra fields |
|------|--------------|
| `team/members/{slug}.md` | `member` (= filename slug), `member_status` (`active` \| `away` \| `alumni`), `role` |
| `team/lanes/{slug}.md` | `lane` (= filename slug), `backup` (member slug or `none`), `lane_status` (`active` \| `blocked` \| `paused` \| `closed`), `scope` (list of repo paths: `dir/` or glob), `work_note` |

## Skills Schema — vendor-portable minimal

Skills (`skills/<name>/SKILL.md`) use the Anthropic-style minimal frontmatter so a `SKILL.md` drops into Codex, Claude Code, or any other coding-assistant CLI without modification:

```yaml
---
name: <skill-name>
description: "One sentence — what this skill does, when to invoke, NOT FOR list."
---
```

**Field definitions:**

| Field | Purpose |
|-------|---------|
| `name` | Skill identifier — matches the directory name (`skills/<name>/`); becomes the argument to `bin/tenet-skill show <name>` |
| `description` | Single sentence describing what the skill does, when to invoke it, and what it's NOT for. This is what `bin/tenet-skill list` displays and what most CLIs surface for skill selection. |

## Why Two Schemas

The standard schema is rich enough that tooling (and you) can filter, route, and audit files by metadata. The skills schema is minimal enough that an external CLI can consume it with zero workspace-specific knowledge. Forcing both into one schema either bloats every skill with workspace-specific fields no external CLI uses, or strips workspace files of metadata the tooling needs. Two schemas, two purposes.

## Validation

The pre-commit hook verifies both shapes open with `---` but doesn't enforce field completeness. For richer compliance checks, run `tools/scripts/check_front_matter.py` manually.
