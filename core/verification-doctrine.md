---
title: Verification Doctrine
type: rule
domain: tenet
product: Tenet
audience: team
owner: team
status: active
updated: 2026-05-14
version: v1.0
tags:
  - verification
  - doctrine
  - probes
  - artifact-checks
artifact_type: operating-rule
---

# Verification Doctrine

> **Read this file alongside `core/ISC.md`.** ISC defines what a criterion looks like. This file defines what *evidence* counts as passing one. The rule is simple: for every artifact type, there is a minimum probe. Anything weaker is not verification.

## The Core Rule

> **No ISC transitions from `[ ]` to `[x]` without a tool-call probe captured in the same response block, or the immediately-following block.**

"Should work", "looks fine", "tests pass" (without showing them), "the change is in place" (without Read/Grep), "no errors" (without the log) — none of these are evidence. They are doctrine violations.

If the probe is genuinely impossible at execution time (e.g., production endpoint exists but you cannot hit it from this environment), mark the criterion `[DEFERRED-VERIFY]` with a follow-up task ID. **Never silently downgrade to `[x]`.**

## Required Probes Per Artifact Type

| Artifact | Required probe | Evidence shape |
|----------|----------------|----------------|
| **File created** | `Read` the file back | First/last 5 lines + line count |
| **File edited** | `Grep` for the new symbol/line OR `Read` the specific range | The matched line(s) with file:line |
| **File deleted** | `ls` showing absence + a `git status` if in a repo | "no such file or directory" + git diff |
| **Code symbol added** | `Grep` for the symbol across the codebase | Match count + file:line of the new definition |
| **Code symbol renamed** | `Grep` for both old and new names | Old count = 0; new count > 0 |
| **Command run** | `Bash` with stdout/stderr captured | The actual output, quoted in the WORK note |
| **HTTP endpoint change** | `curl -i` against the target URL | Status line + relevant response body fields |
| **HTTP endpoint exists** | `curl -i -o /dev/null -w '%{http_code}'` | The status code |
| **API contract** | `curl` + a body-shape check (`jq`, grep, length check) | The matched field |
| **Deploy** | Live-URL probe showing the deployed version string | Version header or known marker in the response |
| **UI render** | Browser screenshot at the target route (headless OK) | Image artifact + the asserted DOM/text snippet |
| **UI interaction** | Headless browser script that clicks/types and asserts post-state | Captured script output + screenshot |
| **Schema/DB change** | `SELECT` confirming the migration landed | Row count, column existence, value check |
| **DB write** | A follow-up `SELECT` returning the written row | The matched row |
| **Config change** | `Read` of the file confirming the new value on disk | The relevant line(s) |
| **Env var set** | `printenv VAR_NAME` or `echo $VAR_NAME` | The (redacted) value or "set" confirmation |
| **Permission change** | `ls -l` showing the new mode | The new permission octet |
| **Package installed** | The tool's own list/freeze command | The package name + version line |
| **Git state** | `git status` + `git log -1 --oneline` | The expected branch/commit info |
| **Auth flow** | A `curl` round-trip showing sign-in → protected-resource access | Both responses with status codes |
| **Authorization (RBAC)** | A `curl` as role X confirming allowed AND a `curl` as role Y confirming denied | Both responses (positive and negative) |
| **Performance** | A measured invocation with timing (`time curl`, query EXPLAIN) | The number + the budget threshold |
| **Logging** | A `grep` against the log file/output for the expected log line | The matched line |
| **Test added** | The test runner output showing the new test name + passing | The runner's pass line for that test |
| **Test fixed** | The test runner output for the previously-failing test now passing | Before/after stdout |
| **Skill activation** | Direct invocation of the skill's entry point | The skill's first-line output |
| **Hook fired** | The hook's logged output OR a synthetic trigger | The logged event |
| **Documentation updated** | `Grep` confirming the new text is in the doc file | The matched line + file:line |
| **Cross-link** | `Grep` for the link from BOTH ends (link source AND target's reverse-mention) | Both matches |

## ENV-ISC Verification Protocol

ENV ISCs (marked `[ENV]` in the WORK note) cannot be verified by the AI — they require a human team member to run a probe in the team's actual environment. The protocol:

**Who verifies:** A named team member with access to the target environment tier.

**Evidence standard:** The same probe-output standard applies — but the human provides the output.

```
ISC-4: [ENV] verified by @sarah in acme-dev on 2026-05-22
  → Opened SN list view for x_acme_requests, new 'priority_override' field visible in columns, label correct
ISC-5: [ENV] verified by @marcus in acme-staging on 2026-05-22
  → Update set committed cleanly, no conflicts, preview showed 3 records updated
```

**What is NOT ENV-ISC evidence:**
- "Sarah says it works" — no specifics.
- "Deployed to staging, looks good" — no field-level observation.
- "Tested in prod" — no named probe, no named observer.

**Handoff discipline:** At EXECUTE close, if any ENV ISCs are pending, output the `ENV ISC HANDOFF` block (see `core/ISC.md`). The WORK note stays at `phase: verify` until all ENV ISCs are resolved. Do not set `phase: complete` with open ENV ISCs.

**Deferred ENV ISCs:** If an ENV ISC cannot be resolved in the current session (environment unavailable, team member offline), create a follow-up task entry in the WORK note under `## Deferred Verification`:

```
## Deferred Verification
- ISC-5: ENV verification pending — acme-staging freeze until 2026-05-25. Assigned: @marcus. Follow-up: memory/work/acme-staging-verify-20260525.md
```

## Anti-Patterns — What Is NOT Verification

- **"I edited the file"** without reading it back.
- **"The function now does X"** without showing the new function body.
- **"The endpoint returns 200"** without `curl -i` output.
- **"The migration ran"** without the resulting `SELECT`.
- **"The build passes"** without the build's terminal output.
- **"The deploy is live"** without hitting the live URL.
- **"The test passes"** without the test runner line.
- **"No regressions"** without naming what regression would have looked like and showing its probe.
- **"The user can now sign in"** without a `curl` of the auth flow.
- **"The dashboard renders"** without a screenshot or DOM probe.

Each of these is a probe-missing failure. Promote the claim to a specific tool probe, then run it, then quote the output.

## The Re-Read Check

After all per-ISC probes pass, before declaring `phase: complete`:

1. Re-read the user's most recent message verbatim.
2. Enumerate every explicit ask as a numbered list.
3. For each ask, mark `✓ addressed` / `✗ missed` / `DEFERRED — reason`.
4. Any `✗` blocks completion. Ship the missing piece OR surface it explicitly as a known gap.

This catches the failure mode where every ISC passes but the *deliverable* still doesn't match what the user asked for. It happens — often. The Re-Read Check is the doctrine that catches it.

## The Capture-Current-State Rule

For **any** non-trivial change (not just bug fixes):

**The current state of what's about to change MUST be captured before the change is applied.**

The pre-change snapshot is the *baseline* against which the post-change probe is verified. Without it, the post-change probe proves only that the new state exists — not that the change had the intended effect.

| Task shape | Required pre-change snapshot |
|------------|------------------------------|
| Bug fix / "X is broken" | A reproduction artifact — `curl`, screenshot, stdout, log line, `SELECT` |
| New feature / new file | `grep` for the symbol or `ls` showing the file does not yet exist; or `curl` returning 404 against the not-yet-existing endpoint |
| Config change | `Read` of the config file or `cat` of the config snapshot before edit |
| Schema / DB change | `SELECT` of the existing schema or the representative rows |
| Refactor | Test runner output passing before the refactor (or the specific failing cases that the refactor will fix) |
| Doctrine edit | The verbatim quote of the rule being changed (so the diff is auditable) |
| UI change | Screenshot of the current UI before the edit |
| Hook / script change | Synthetic invocation showing current behavior before the edit |
| Permission / role change | `ls -l` or role-listing query before the change |

For bug fixes the snapshot is also the reproduction (`X is broken` symptom captured). For new work the snapshot is the *absence* (zero matches, 404). For modifications the snapshot is the *before-state*. The verification probe then compares before-state against after-state to confirm the change had the intended effect *and* did not have unintended effects.

This generalizes the v1.0 Reproduce-First rule: every change benefits from a snapshot, not just bug fixes. The cost is one extra probe; the benefit is deterministic effect-verification plus regression detection.

## Why This Doctrine Exists

Claude Code's Tenet has hooks that fire on every tool call and a `Verification Doctrine` enforced by the Algorithm. Codex does not. **This file is the substitute.** Reading and following it produces the same operational floor by making the verification rules *explicit in the workspace* instead of *implicit in the harness*.

The principle from the v1.0 architectural finding applies here too: Claude Code can be light because the model and harness carry the discipline; Codex needs the discipline to be deterministic and visible — which is exactly what this file makes it.
