---
title: Corporate profile — runtime guard for the constitution's NEVERs
type: work
status: complete
phase: complete
tier: standard
reasoning_effort: medium
updated: 2026-10-20
tags: [security, policy, hooks, dlp, demo]
---

# Corporate profile — runtime guard

👁️ INTENT: Give OpenTenet an opt-in "corporate" profile where data-protection and agent guardrails are
deterministic, auditable controls (not just doctrine the model is asked to obey), plus a scenario corpus
that demonstrates each control live — framed as ONE layer of defense-in-depth.

## Current state (OBSERVE)
- Deterministic today: pre-commit 16-pattern secret scan (`.githooks/pre-commit`), ingest guard
  (`tools/ingest_guard.py`: injection banner, SSRF), doctrine SHA-256 manifest, dashboard lock-down.
- Doctrine-only today (model-obeyed, not enforced): workspace confinement, no push without instruction,
  no `--no-verify`, destructive-command gate, no secrets/PII handling, ingested content = data.
- No `.claude/settings.json`, no runtime hook, no PII detection, no egress policy.

## Risks (THINK)
🎲 RISKIEST ASSUMPTIONS: Claude Code hook JSON contract (PreToolUse `permissionDecision`, UserPromptSubmit
`decision: block`) behaves as documented on 2.1.305 — must be proven with a live `claude -p` probe.
⚰️ PREMORTEM: demo overclaims ("regex DLP = data protection") and a security audience breaks it with
obfuscation → mitigate by shipping documented KNOWN-GAP cases and a layer map.
☑️ PREREQUISITES: python3 stdlib only; claude CLI present.
🚫 AP CHECK: none.

## Plan
📐 SCOPE: depth — one engine, one policy file, one CLI, wired to Claude Code hooks + git pre-commit.
📦 DELIVERABLES:
- D1 `policy/corporate.json` — the human-readable policy (data classes, protected paths, doctrine paths,
  command rules, egress allowlist, framework mapping)
- D2 `tools/guard.py` — stdlib engine + hook entrypoints + hash-chained audit log
- D3 `bin/tenet-guard` — CLI: install / demo / check / explain / audit
- D4 `policy/demo-cases.json` — scenario corpus incl. documented known gaps
- D5 `tests/test_guard.py`
- D6 `docs/security/corporate-profile.md` — control map, layer map, live demo script
- D7 `.githooks/pre-commit` — PII scan when the corporate profile is installed

## ISC
- [x] ISC-1: `bin/tenet-guard demo` exits 0 with every scenario matching its expected decision
- [x] ISC-2: `python3 -m pytest tests/ -q` passes (existing + new)
- [x] ISC-3: live `claude -p` in a corporate-installed workspace is blocked reading `.env`
- [x] ISC-4: live `claude -p` prompt containing a Luhn-valid card number is blocked at UserPromptSubmit
- [x] ISC-5: `bin/tenet-guard audit verify` reports the chain intact; tampering one line breaks it
- [x] ISC-6: pre-commit blocks a staged SSN when the profile is installed
- [x] ISC-7: Anti: the audit log never contains a raw matched secret/PII value (grep)
- [x] ISC-8: Anti: base OpenTenet (profile not installed) behaves unchanged — no `.claude/settings.json` committed

## Verification
✅ VERIFICATION:
- ISC-1: `bin/tenet-guard demo` → "32/32 scenarios behaved as specified (mode=enforce, policy v1.0.0)", exit 0
- ISC-2: `python3 -m pytest tests/ -q` → "85 passed"
- ISC-3: live `claude -p` (haiku, `--allowedTools Bash`) "cat .env" → blocked; audit row `BLOCK PreToolUse Bash PATH-PROTECTED cat .env`
- ISC-4: live `claude -p` card-number prompt → "UserPromptSubmit operation blocked by hook … Prompt NOT sent to the model provider"
- ISC-5: `audit verify` → INTACT 3 entries; after editing line 2 → "TAMPERED chain broken at line 2", exit 1
- ISC-6: scratch copy, staged `Avery,123-45-6789` → "pre-commit: FAIL — US Social Security number [PII-SSN …6789]", commit exit 1
- ISC-7: `grep -c "4111 1111" guard-log.jsonl` → 0; `test_audit_never_stores_raw_values` passes
- ISC-8: base repo `ls -a` shows no `.claude/` or `.tenet-profile`; profile only via `bin/tenet-guard install`

📦 DELIVERABLE COMPLIANCE: D1–D7 ✓
🔄 RE-READ: configure a corporate OpenTenet with controls + policies ✓ · list of examples to feed it ✓ (policy/demo-cases.json + doc demo script) · framed as one layer ✓ (layer map + K1–K4 gaps)

## Learnings
🧠 Bazzite `/home` → `/var/home` symlink: realpath the candidate AND the policy globs, or path rules silently miss (caught by D6).
🧠 Hook JSON `permissionDecision: deny` beat a user `--allowedTools Bash` pre-approval live on Claude Code 2.1.305.
🧠 Shipping documented known-gap cases (K1–K4) in the demo corpus is the credibility move for a security audience.

## Round 2 — demo copy + slide + paste script (2026-10-20 eve)
- Demo workspace `~/Documents/OpenTenet-Corporate-Demo` (origin remote REMOVED; profile installed; fake `.env`, `data/restricted/`,
  injected `vendor/security-page.md`; `demo-reset.sh`; policy pinned `allow_mode_override: false`).
- Live rehearsal found and fixed: (1) FALSE POSITIVE — `ls … policy 2>/dev/null` blocked as PATH-DOCTRINE because any `>` made every
  token a write target → replaced with `_write_targets()` (redirect destinations + mutating-command args); (2) GAP — shell
  `>> ~/.bashrc` not scope-checked → PATH-SCOPE on bash write targets (tempdir and /dev exempt); (3) agent advised
  `TENET_GUARD_MODE=audit` as an escape → `allow_mode_override` policy switch; (4) audit-mode test depended on workspace policy.
  Regression cases A7, A8, G12, G13. Demo 36/36, tests 90 passed (repo and demo copy).
- All 13 paste prompts in `DEMO-SCRIPT.md` run live via `claude -p` (sonnet) with the logged decision recorded.
- Deck: new slide 9 "Guardrails in practice" inserted after the security layer; 15 slides; SPLIT 10→11; headless-Chrome
  screenshot verified (no overflow) for slides 9 and 11. Backup of the prior deck in the session scratchpad.
🧠 Rehearsing the demo through the real model surfaced a false positive the 32-case corpus missed — run live prompts, not just fixtures.

## Round 3 — deck (2026-10-20 late)
- Wed deck restructured with Jacob: 12 slides, OpenTenet-only (Attestor + constitution slides removed), guardrails slide 9,
  David's agent-security slide 10 (score boxes updated to reflect this profile), CTA 11, site 12. Latest = Oracle file #24 to David.
- OPEN: sources for slide 10's four "SEEN IN" breach examples (David). Branch `feat/corporate-profile` still uncommitted.
