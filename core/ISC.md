---
title: ISC — Ideal State Criteria
type: rule
domain: tenet
product: Tenet
audience: individual
owner: operator
status: active
updated: 2026-05-24
version: v1.0
tags:
  - isc
  - verification
  - acceptance-criteria
  - doctrine
artifact_type: operating-rule
---

# ISC — Ideal State Criteria

> **Read this file alongside `core/ALGORITHM.md`.** ISCs are the primitive that makes the Algorithm verifiable. Without ISCs, "done" is a feeling. With ISCs, "done" is a measurement.

## The Core Rule

> **Every criterion describes one verifiable end-state, testable by a single tool call.**

A criterion is granular enough when one of these returns yes/no on whether it's met:

- `cat`, `bat`, or a file read
- `grep` / `rg`
- `curl -i`
- `Bash` invocation with checked output
- `psql` / `SELECT` with a value check
- a browser screenshot
- `python -c` returning a boolean
- a test runner output

**If you cannot name the probe that would verify it, the criterion is not yet atomic — split it.**

If the criterion needs human judgment ("looks clean", "feels right"), name the tool-verifiable proxy that stands in for the judgment.

## The Splitting Test

Apply to every criterion as you write it:

| Test | Split when... |
|------|--------------|
| **"And" / "with"** | Joins two verifiable things — split into one ISC each |
| **Independent failure** | Part A can pass while B fails — they are two ISCs |
| **Scope words** | "all", "every", "complete" → enumerate them |
| **Domain boundary** | Crosses UI / API / data / logic — one ISC per boundary |
| **No nameable probe** | You cannot say which tool would verify it — split until you can |

**Real example — bad ISC:**

> The user can sign in and see their dashboard with their recent activity.

This is three ISCs in disguise. Split:

- `- [ ] ISC-1: POST /auth/signin returns 200 with valid session cookie`
- `- [ ] ISC-2: GET /dashboard returns 200 for an authenticated user`
- `- [ ] ISC-3: GET /api/activity?user=X returns a non-empty JSON array containing X's last action`

Each one has a `curl` probe. Each one can fail independently.

## ISC Format

In the WORK note `## Criteria` section:

```
- [ ] ISC-N: criterion text
```

- `N` is a sequential integer. **IDs never re-number on edit.**
- If a criterion is split during refinement, the children become `ISC-N.1`, `ISC-N.2`, etc., and the parent is preserved as a header.
- If a criterion is dropped, leave a tombstone: `- [ ] ISC-N: [DROPPED — see Decisions]`

## Status Markers

| Marker | Meaning |
|--------|---------|
| `- [ ]` | Pending — not yet verified |
| `- [x]` | Passed — verified with evidence under `## Verification` |
| `[DEFERRED-VERIFY]` | Passed in code/intent but the live probe is impossible right now. **Requires a follow-up task ID.** Cannot become `[x]` until the deferred probe runs. |

**`- [x]` without `## Verification` evidence is a doctrine violation.** Tool-verified or it didn't happen.

## Two Doctrinal Kinds

Mark these with a prose prefix in the criterion text. They still number as `ISC-N` in the same list.

### Anti-criterion — what MUST NOT happen

Every WORK note has at least one anti-criterion. They prevent regressions and protect against the obvious wrong shape of "done".

```
- [ ] ISC-7: Anti: no plaintext secrets appear in the committed config file
- [ ] ISC-8: Anti: no production data is touched during the test run
```

**The Splitting Test applies to anti-criteria too.** "No bugs and no regressions" splits into separate anti-criteria.

### Antecedent — precondition for the target experience

Required when the goal is experiential (a UI flow, a writing piece, a stakeholder summary). The antecedent is the technical prerequisite for the experience to be possible.

```
- [ ] ISC-2: Antecedent: the new dashboard route exists at /dashboard/v1 and serves 200
- [ ] ISC-3: Antecedent: feature flag dashboard_v2 is on for the test user
```

## Parallel Groups — Exploit Batched Tool Calls

> **Optional for solo use.** Most tasks don't need it — it becomes valuable when you have 10+ independent ISCs to verify at once. Single-digit ISC counts can be verified sequentially without meaningful cost.

Modern LLM tool harnesses (GPT family, Claude, Gemini) make multiple parallel tool calls in a single response when the calls are independent. **The Algorithm's VERIFY phase exploits this when ISCs are tagged with the same `parallel_group:` letter.**

Tag independent ISCs in the criterion line (after the criterion text):

```
- [ ] ISC-1: GET /api/health returns 200          parallel_group: A
- [ ] ISC-2: GET /api/metrics returns 200         parallel_group: A
- [ ] ISC-3: GET /api/version returns build SHA   parallel_group: A
- [ ] ISC-4: DB migration row exists in audit_log parallel_group: B
- [ ] ISC-5: GET /api/audit returns the migration parallel_group: C  (depends on ISC-4)
```

VERIFY runs group A's three `curl`s in one turn, then group B's `SELECT`, then group C's dependent `curl`. Free 2–4× speedup on the VERIFY phase.

**Rules for safe parallel grouping:**

- **Independent reads only by default.** Parallel-grouping reads (`curl GET`, `Read`, `Grep`, `SELECT`) is always safe.
- **Parallel writes require explicit reasoning.** Writes that share state (same file, same DB row, same external resource) are NOT parallel-safe. Document the rationale in `## Decisions` if you mark writes as parallel.
- **Dependencies break grouping.** If ISC-B's probe depends on ISC-A's outcome (a write must precede a read; a deploy must precede the live-URL check), they are sequential — different groups, or ungrouped.
- **No group = run sequentially.** ISCs without a `parallel_group:` tag run one at a time in VERIFY.

The `parallel_group:` tag is the only place in the doctrine where the model is explicitly directed to batch tool calls. Without it, the model defaults to sequential verification — which is correct but slower.

## How Many Criteria?

**The Splitting Test produces the count.** Don't pad and don't compress. That said, the loose floors below catch under-articulation:

| Tier | Loose floor on ISC count |
|------|-------------------------|
| Quick | none — single edit doesn't need ISCs |
| Standard | ≥4 ISCs (including ≥1 anti) |
| Deep | ≥12 ISCs (including ≥2 anti, ≥1 antecedent if experiential) |

For a complex application or governance review, the count runs much higher — sometimes 50+. The full test surface for a complex deliverable includes:

- **Functional** — features work end-to-end
- **API** — endpoints exist, return the expected shape, handle errors
- **Auth** — sign-in/out, token expiry, session lifecycle
- **Authorization** — role X can/cannot reach endpoint Y
- **Performance** — latency budgets, query times
- **Security** — input validation, output encoding, CSRF, rate limits, secret handling
- **Data integrity** — schema invariants, foreign-key consistency
- **Build & deploy** — build succeeds, typecheck clean, deploy version matches
- **Operational** — `/health` returns 200, monitor up

These aren't *in addition to* the WORK note's criteria — they ARE the criteria for the relevant deliverables.

## Verification Evidence

When an ISC transitions to `[x]`, append a line under the WORK note's `## Verification` section in this shape:

```
ISC-7: grep — "no SK_LIVE_ found in config/" (output: 0 matches)
ISC-8: curl -i https://example.test/api/health — 200 OK, body contains "status":"ok"
ISC-12: SELECT — count(*) FROM users WHERE created_at > NOW() - INTERVAL '1 hour' = 0 (anti: no test users leaked into prod)
```

**The evidence is the probe output**, not a description of what the probe would have shown. Paste the actual command and the actual return.

## Anti-patterns to Avoid

- **Vague language**: "the feature is robust", "the code is clean" — name the probe or drop the criterion.
- **Compound criteria**: "X works and Y is logged" — that's two ISCs.
- **Procedural criteria**: "I ran the linter" — what does the linter need to *say*? That's the ISC.
- **Post-hoc ISCs written after the work is done** — they always pass trivially. Write ISCs at OBSERVE before any code is touched, refine at PLAN after the premortem.
- **Anti-criteria that are just restatements**: "Anti: the feature does not break" is meaningless. Name what specifically must not happen: "Anti: signing in does not log the user as admin by default".
