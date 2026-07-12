---
title: Skills Map
type: map
domain: tenet
product: Tenet
audience: individual
owner: operator
status: active
updated: 2026-05-24
tags:
  - skills
  - map
  - navigation
artifact_type: navigation-map
---

# Skills Map

Human-browsable index of available skills. The `bin/tenet-skill` CLI auto-discovers skills from their `SKILL.md` frontmatter — no registration needed.

## Available Skills

| Skill | When to use |
|-------|-------------|
| [code-review](./code-review/SKILL.md) | Reviewing changes for bugs, regressions, edge cases, missing tests, risky assumptions, or maintainability issues. |
| [Convert](./Convert/SKILL.md) | Convert URL, PDF, DOCX, PPTX, or EPUB to markdown. |
| [planning](./planning/SKILL.md) | Decomposing a broad goal or task into phases, checkpoints, risks, and implementation order. |
| [research-synthesizer](./research-synthesizer/SKILL.md) | Gathering information from multiple sources and converting it into a concise, decision-ready synthesis. |

## Skill discovery CLI

```sh
bin/tenet-skill list              # one line per skill (cheap)
bin/tenet-skill show <name>       # full SKILL.md on demand
bin/tenet-skill path <name>       # absolute path (for @-mention)
```

## Adding a new skill

1. Create `skills/{name}/SKILL.md` with `name:` and `description:` frontmatter
2. Run `tools/scripts/skills_index.sh` to regenerate `memory/skills-catalog.md`
3. Run `tools/scripts/build_session_context.sh` to update the session context
4. Add an entry to this map

See `CONTRIBUTING.md` for the full convention.
