---
title: Security hardening — raise Attestor grade D- → B+
slug: 20260730-000001_security-hardening-b-plus
task: Implement compensating controls for the 7 Attestor findings so a re-grade is an honest B+
type: work-note
status: complete
phase: complete
tier: deep
reasoning_effort: high
created: 2026-07-30
tags: [security, ai-governance, attestor, prompt-injection, ssrf, supply-chain]
---

# Security hardening — Attestor D- → B+

## 👁️ INTENT
An Attestor assessment (ISO/IEC 42001 + NIST AI RMF) graded OpenTenet **D-**.
Implement real, tested compensating controls for all 7 findings so an honest
re-grade via `attestor grade` computes **B+**.

## Why D- (from the report + engine rubric)
- Grade keys on **worst residual**. T1 (indirect prompt injection) was **High**
  → letter D. The `-` fired because the top risk was flagged `inherent`
  (category risk) → MINUS wins over any plus. Everything UNVERIFIABLE → Low
  confidence.
- To reach **B+**: drive every residual ≤ Low-Medium (no High, no Moderate-High,
  ≤1 Moderate); keep the worst-residual tier from being *all* `inherent`; set
  `remediation_started`/`mitigation_verified` truthfully; evidence findings so
  confidence ≥ Medium. Then `_base_letter`→B and `_modifier`→`+`.

## Threat → control map
| ID | Threat | Was | Control(s) | Target residual |
|----|--------|-----|-----------|-----------------|
| T1 | Indirect prompt injection via ingest | High | untrusted banner + injection screen on every converted file; constitution trust-boundary rule; loader never loads ingest output; gitignore output | Low-Medium |
| T2 | Persistent memory poisoning | Mod-High | doctrine integrity manifest + verifier (CI + on demand); constitution no-auto-promote rule | Low-Medium |
| T3 | Unpinned ingest deps | Moderate | pin pdf-to-markdown reqs; `pip-audit` CI job over both reqs | Low-Medium |
| T4 | Exfil via poisoned AI + outbound fetch | Mod-High | SSRF guard in web2md (scheme allowlist + DNS-resolved IP class check, blocks loopback/RFC1918/link-local/metadata; per-redirect) | Low-Medium |
| T5 | Dashboard unauth writes to doctrine | Low-Med | drop wildcard CORS; Host allowlist (anti-DNS-rebind); write-token on POST; audit each write | Low |
| T6 | No audit logging of AI actions/ingest | Moderate | append-only JSONL ingest + dashboard audit log | Low |
| T7 | Secret scanner partial/opt-in | Low-Med | hook already auto-installs via bootstrap + CI secret-scan; add pip-audit; document layered coverage | Low |

## ISCs
- [ ] ISC-1: `tools/ingest_guard.py` exists, importable, **stdlib-only**.
- [ ] ISC-2: `scan_injection` flags a known injection string, passes clean text.
- [ ] ISC-3: web2md output starts with the untrusted banner (marker + SHA-256).
- [ ] ISC-4: pdf2md output starts with the untrusted banner.
- [ ] ISC-5: `assert_public_url` blocks loopback/private/link-local/metadata, allows public.
- [ ] ISC-6: web2md refuses `http://127.0.0.1` and `http://169.254.169.254` before any network.
- [ ] ISC-7: each ingest appends a JSONL provenance record to `memory/audit/ingest-log.jsonl`.
- [ ] ISC-8: constitution.md carries the trust-boundary NEVER rules.
- [ ] ISC-9: `tools/scripts/verify_doctrine_integrity.py` builds a manifest and detects drift.
- [ ] ISC-10: pdf-to-markdown reqs pinned; `pip-audit` job in CI.
- [ ] ISC-11: dashboard rejects foreign Host and unauthenticated POST; GET ok.
- [ ] ISC-12: dashboard writes are logged to the audit log.
- [ ] ISC-13: `.gitignore` excludes `projects/*/output/`.
- [ ] ISC-14: offline pytest suite passes; CI runs it.
- [ ] ISC-15: `attestor validate` passes (all control ids real).
- [ ] ISC-16: `attestor grade` on the new assessment returns **B+**, confidence ≥ Medium.
- [ ] Anti-1: no residual is rated below what its implemented+tested control supports.
- [ ] Anti-2: doctrine load path still never includes `projects/*/output/` (test asserts).
- [ ] Anti-3: core repo gains **no** third-party dependency (guard/integrity/dashboard stdlib-only).

## Verification
- ISC-1: `python3 -m py_compile tools/ingest_guard.py` OK; imported by 28-test suite (stdlib-only, no third-party imports). ✅
- ISC-2: `test_scan_injection_flags_known/_clean` pass — flags "ignore all previous instructions", passes clean report. ✅
- ISC-3/4: `test_guard_and_wrap_prepends_banner_and_logs` passes; web2md + pdf2md call `guard_and_wrap` before every write (wired). ✅
- ISC-5: 13 parametrized SSRF cases pass — loopback/RFC1918/link-local(169.254.169.254)/ULA/scheme blocked; 8.8.8.8/1.1.1.1/93.184.216.34 allowed. ✅
- ISC-6: web2md `_get_guarded` calls `assert_public_url` on initial URL + each redirect (disabled auto-redirects); render_html + sitemap guarded. ✅ (unit-verified; E2E blocked — no venv)
- ISC-7: audit-log test asserts JSONL record with tool/source/event=ingest. ✅
- ISC-8: `grep "UNTRUSTED"` in core/constitution.md (3 NEVER rules) + condensed doctrine → built into session-context.md/-codex.md. ✅
- ISC-9: `verify_doctrine_integrity.py --update` → 13 files; verify exit 0; tamper/untracked/missing all → exit 1 (tests). ✅
- ISC-10: pdf-to-markdown reqs pinned; CI `dependency-audit` runs pip-audit over both reqs. ✅
- ISC-11: `test_dashboard_security.py` — foreign Host rejected, loopback ok, token required, no wildcard CORS. ✅
- ISC-12: dashboard POSTs call `audit(...)` → memory/audit/dashboard-log.jsonl. ✅
- ISC-13: `.gitignore` has `projects/*/output/` + `memory/audit/*.jsonl`. ✅
- ISC-14: `python3 -m pytest tests/ -q` → **28 passed**; CI `security-tests` job runs it. ✅
- ISC-15: `attestor validate` → "all 16 cited control ids resolve". ✅
- ISC-16: `attestor grade` → **B+ · Confidence: High** (7 evidenced / 0 unverifiable). ✅
- Anti-1: every EVIDENCED finding maps to a named artifact/test; injection (T1) honestly kept `inherent` at Low-Medium (not floored to Low). ✅
- Anti-2: poison file in projects/web-to-markdown/output/ → rebuild context → absent from both session-context files. ✅
- Anti-3: ingest_guard, integrity verifier, and dashboard are stdlib-only; no new third-party dep in the core repo. ✅

🧠 LEARNING: the D- was two problems, not one — a High residual AND the `-` modifier (top risk `inherent`). B+ required both driving every residual ≤ Low-Medium AND keeping the worst-residual tier not-all-inherent so `_modifier` returns `+`. Evidence (EVIDENCED + mitigation_verified + remediation_started) lifted confidence Low→High. The near-identical `doc-vault-ai-triage` fixture lands B- only because its remediation is unstarted.

━━━ SUMMARY ━━━
🔄 ITERATION on: OpenTenet Attestor grade D- → B+ via real compensating controls
📃 CONTENT: ingest trust boundary, SSRF guard, dep pinning+pip-audit, dashboard auth, audit logs, doctrine integrity, 28 tests
🖊️ STORY: injection+inherent capped it at D-; built+verified layered controls; engine regraded B+/High; nothing faked
🗣️ NEXT: review the branch; commit + push when you're ready (not pushed).
