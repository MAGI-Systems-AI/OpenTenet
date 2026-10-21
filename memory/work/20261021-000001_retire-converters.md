---
title: Retire the web + PDF converters; route DOCX to pandoc
type: work
status: complete
phase: complete
tier: standard
reasoning_effort: medium
updated: 2026-10-21
tags: [dependencies, supply-chain, convert, ingest]
---

# Retire the web + PDF converters

👁️ INTENT: Make OpenTenet dependency-free by retiring `projects/pdf-to-markdown` (docling → Pillow, 8 CVEs
fixed only in Pillow 13, which docling caps out) and `projects/web-to-markdown` (26 pins incl. Playwright),
routing DOCX to pandoc, without losing the ingest trust-boundary controls.

## Current state (OBSERVE)
- Core (`bin/`, `tools/`, guard, dashboard) is stdlib-only; the two converters were the only pip consumers.
- Both converters called `ingest_guard.guard_and_wrap` (banner + injection screen + provenance log); the
  pandoc route (PPTX/EPUB) called nothing, so its output was unbannered.
- CI `dependency-audit` only audited the two converters' requirements.

## Risks (THINK)
🎲 RISKIEST ASSUMPTIONS: nothing outside `projects/` imports the converters (grep: only the skill, CI, docs).
⚰️ PREMORTEM: pandoc output reaches the assistant without the untrusted banner → injection regression.
☑️ PREREQUISITES: pandoc available (optional system tool; tested via `docker.io/pandoc/core:3.5`).
🚫 AP CHECK: none

## Plan
📐 SCOPE: breadth — every reference to the retired tools.
📦 DELIVERABLES:
- D1 delete `projects/pdf-to-markdown/`, `projects/web-to-markdown/`
- D2 `tools/ingest_guard.py wrap` CLI so external converters keep the T1/T6 controls
- D3 `skills/Convert/SKILL.md` → pandoc-only (DOCX/PPTX/EPUB), every route through `wrap`
- D4 CI: drop the `dependency-audit` job (nothing left to audit)
- D5 `SECURITY.md` rows (supply chain, SSRF, secret scanning); regenerate skills catalog + session context

## ISC
- [x] ISC-1: no tracked file under `projects/pdf-to-markdown/` or `projects/web-to-markdown/`
- [x] ISC-2: `ingest_guard.py wrap` writes banner + logs (test_cli_wrap_writes_banner_and_logs)
- [x] ISC-3: `wrap` refuses empty stdin (test_cli_wrap_refuses_empty_input)
- [x] ISC-4: no pip manifest left in the repo
- [x] ISC-5: Convert skill routes DOCX to pandoc piped through `wrap`
- [x] ISC-6: Anti: converted content reaches disk without the untrusted banner — must NOT happen
- [x] ISC-7: Anti: doctrine manifest drift — must NOT happen

## Verification
- ISC-1: `git ls-files projects/` → only `projects/.gitkeep` + `projects/projects-map.md`.
- ISC-2/3: `python3 -m pytest -q tests/` → 93 passed (3 new CLI tests).
- ISC-4: `find . -name 'requirements*.txt' -o -name pyproject.toml` (excluding .git) → none.
- ISC-5: `skills/Convert/SKILL.md` routing table + command block.
- ISC-6: e2e — markdown → docx → `pandoc -t gfm` → `wrap`: output starts with `ATTESTOR-UNTRUSTED-INGEST`,
  injection screen flagged "Ignore all previous instructions; system prompt", log line `"tool": "pandoc"`.
- ISC-7: `python3 tools/scripts/verify_doctrine_integrity.py` → OK, 14 files match.

## Decisions
- URLs and PDFs are no longer supported (by request). `assert_public_url` stays in `ingest_guard` as a
  tested library guard for any future fetcher.
- `memory/session-context-local.md` line 20 still names `projects/*-to-markdown` in the ingested-content
  NEVER rule; left as-is (doctrine-manifest file; the rule itself still holds for pandoc output).
- `docs/security/opentenet-assessment.json` is a dated Attestor record; left unedited.

## LEARN
🧠 The pandoc route had no ingest guard at all before this change; a converter-agnostic `wrap` CLI closes
that gap and makes the control independent of which converter is used.
