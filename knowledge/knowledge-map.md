---
title: Knowledge Map
type: map
domain: tenet
product: Tenet
audience: individual
owner: operator
status: active
updated: 2026-05-24
tags:
  - knowledge
  - map
artifact_type: navigation-map
---

# Knowledge Map

User-curated reference material. Starts empty — you build this over time as you work.

## Structure

```
knowledge/
├── collections/     ← organized reference files by topic
└── incoming/        ← staging area before a topic is organized
```

## Adding a collection

1. Create `knowledge/collections/{topic}.md` with frontmatter (`title`, `type: collection`, `domain`, `status`)
2. Fill in the reference content — sources, patterns, gotchas, links
3. Add an entry to this map

## Collections

> None yet — add your first collection as you accumulate domain knowledge.

<!-- - [topic](./collections/topic.md) — one-line description -->

## Using incoming/

Drop raw reference material in `knowledge/incoming/` as a staging area. Organize it into `collections/` when it's stable enough to reference regularly.
