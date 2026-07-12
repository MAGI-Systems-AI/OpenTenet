---
title: The Algorithm
type: rule
domain: tenet
product: Tenet
audience: individual, small-team
owner: operator
status: active
updated: 2026-05-30
version: v1.1
tags:
  - algorithm
  - operating-loop
  - doctrine
artifact_type: operating-rule
---

# The Algorithm

> **Read this file before any non-trivial work.** It defines the universal loop your coding-assistant CLI uses to transition from a current state to an ideal state. Every multi-step task runs through these phases. Trivial single-edits do not — see `tier` rules below.

## Doctrine

**Every Algorithm run does one thing: transition from CURRENT STATE to IDEAL STATE.** The mechanism: articulate the ideal state as testable criteria (ISCs — see `core/ISC.md`), pursue them through phases, verify each one met. Same loop applies in any domain: code, infrastructure, documentation, research, writing.

**The WORK note is the system of record for a task.** When you start a non-trivial task, create `memory/work/{slug}.md` with frontmatter and the ISCs as a checklist. Each phase edits this file. The WORK note IS the test harness — passing every ISC means the task is done.

**Required WORK note frontmatter:**

```yaml
---
task: [one-line task description]
slug: [filesystem-safe slug, matches filename]
phase: [observe | think | plan | execute | verify | learn | complete]
tier: [quick | standard | deep]
reasoning_effort: [low | medium | high]
started: [ISO date]
updated: [ISO date]
---
```

**The unit of work is the thing being articulated, not the prompt.** For a project with persistent identity, the WORK note lives at `projects/{name}/WORK.md` and grows continuously across many tasks. For ad-hoc work, `memory/work/{slug}.md` is created at OBSERVE and archived at LEARN.

## Tier Rules

| Tier | Trigger | Use the loop? | WORK note? | Reasoning effort |
|------|---------|---------------|-----------|------------------|
| **Quick** | Single-file edit, single command, single fact lookup. No new artifact. | No — skip to execution | No | `low` (no extended thinking) |
| **Standard** | Multi-file, multi-step, anything ambiguous, anything touching `core/` or `memory/` doctrine | Yes — full 6-phase loop | Yes | `medium` (extended thinking on THINK + VERIFY) |
| **Deep** | Architecture decisions, governance updates, anything that will be referenced again | Yes — full 6-phase loop + explicit Decisions log | Yes (with `## Decisions` populated) | `high` (extended thinking on THINK + PLAN + VERIFY) |

**Bias toward Standard when in doubt.** Under-scoping is the failure mode this loop was built to prevent.

### Reasoning Effort — vendor-neutral budget signal

The WORK note's `reasoning_effort:` frontmatter is a vendor-neutral budget signal. Each vendor's harness maps it to the model's native control:

| Tenet signal | OpenAI GPT family | Anthropic Claude | Google Gemini |
|-----------------|-------------------|------------------|---------------|
| `low` | `reasoning_effort: low` | extended-thinking budget ≈ 0 | `thinkingConfig.thinkingBudget ≈ 0` |
| `medium` | `reasoning_effort: medium` | extended-thinking budget ≈ 8K tokens | `thinkingBudget ≈ 2048` |
| `high` | `reasoning_effort: high` | extended-thinking budget ≈ 24K+ tokens | `thinkingBudget ≈ 8192` |

The doctrine produces the *signal*; the harness produces the *behavior*. This lets Tenet exploit native reasoning controls without vendor-specific code in the doctrine.

## The Six Phases

Every Standard or Deep task runs through these phases in order. Output the phase header line before each phase's work. Edit the WORK note's `phase:` frontmatter at every transition.

### 1. OBSERVE

Echo the user's intent in one sentence. **If you cannot restate it accurately, re-read the request.**

```
👁️ INTENT: [one-sentence restatement of what user actually asked for]
```

Then:
- Reverse-engineer the request: what is explicitly wanted, what is explicitly not wanted, what is implied not wanted, what is the speed signal
- Identify the WORK note location and create it if it doesn't exist
- Set the tier (Quick / Standard / Deep) and write it to frontmatter
- Set `reasoning_effort` per the table above

**Capture-Current-State rule:** before any change, capture the current state of what's about to change. Cost is one extra probe; benefit is deterministic verification of effect and regression detection.

| Task shape | Required pre-change snapshot |
|------------|------------------------------|
| Bug fix / "X is broken" | A reproduction artifact — `curl`, screenshot, stdout, log line, `SELECT` |
| New feature | `grep` for the new symbol/file (expect zero matches); a `curl` 404 against the not-yet-existing endpoint |
| Config change | `Read` of the config file before edit |
| Refactor | Test runner output passing before the refactor |
| Doctrine edit | The verbatim quote of the rule being changed |

The pre-change snapshot is the baseline against which the change is verified. Without it, the "after" probe proves nothing about the change's effect.

**End OBSERVE by writing the initial ISC list to the WORK note.** Apply the Splitting Test (see `core/ISC.md`): every criterion is one binary tool probe. Include at least one anti-criterion (what MUST NOT happen). Mark independent ISCs with the same `parallel_group:` if you want VERIFY to batch them in one turn (optional for solo use).

### 2. THINK

Write to the WORK note under `## Risks`:

```
🎲 RISKIEST ASSUMPTIONS: [what this work depends on being true]
⚰️ PREMORTEM: [the most likely ways this fails — name 2-3]
☑️ PREREQUISITES: [any blocker that must be resolved before EXECUTE]
🚫 AP CHECK: [AP-N — name, if a known anti-pattern in knowledge/domain/anti-patterns.md matches | "none" if clean]
```

The AP CHECK is a scan of `knowledge/domain/anti-patterns.md` before any execution. If an AP matches, cite it by ID — "AP-N: [name]. Mitigation: [approach]." On a fresh workspace with no entries yet, write "none — knowledge/domain/anti-patterns.md is empty." The file will fill over time.

Then refine ISCs. Add criteria for the premortem failure modes. Re-apply the Splitting Test. Drop or split as needed.

**Root-cause-at-ingestion checkpoint** (for bug fixes): before any fix that modifies output-side behavior, answer:

1. Where does this bad state enter the system? Name the ingestion point.
2. If I fix it at the ingestion point instead of here, do similar bugs disappear? If yes — move the fix upstream.

### 3. PLAN

Output the scope and the deliverable manifest.

```
📐 SCOPE: [depth | breadth | breadth-then-depth] — [why]
📦 DELIVERABLES:
 📦 D1: [user sub-task — quote distinctive phrasing]
 📦 DN: [user sub-task]
```

Each deliverable must map to ≥1 ISC. **A deliverable without a matching ISC is a missed criterion — add it before EXECUTE.**

For code work: read the surrounding files, name the integration points, identify the upstream/downstream effects. Document significant decisions in the WORK note `## Decisions` log with timestamp.

**Stop-the-line rule:** if the user said "make a plan", end here. Do not execute without explicit approval.

### 4. EXECUTE

Do the work. Edit files. Run commands. Apply changes.

**As each ISC passes, immediately mark it `[x]` in the WORK note and append evidence under `## Verification`:**

```
ISC-N: [probe type] — [one-line evidence: command output or file content]
```

**Inline verification mandate.** No ISC may transition from `[ ]` to `[x]` without a tool-call probe in the same block or the immediately-following block.

| ISC type | Required probe |
|----------|----------------|
| File write | Read the file back, confirm content |
| Code edit | Grep for the new symbol, or Read the specific range |
| Command execution | Captured stdout/stderr |
| HTTP/API change | `curl -i` with status + body check |
| UI change | Browser screenshot at the target route |
| Schema/DB change | `SELECT` confirming the migration landed |
| Config change | Read-back of the file confirming the new value |

**Forbidden language:** "should work", "should be", "expected to", "the change is in place" (without Read/Grep), "done" (without tool evidence), "no errors" (without the actual log).

#### The ISC Failure → THINK Loop

> Real engineering iterates. The Algorithm's phases are not strictly linear — they form a loop with one defined back-edge.

When an ISC probe at EXECUTE or VERIFY fails:

1. **Do not silently retry.** Capture the failure as evidence under `## Verification`.
2. **Return to THINK.** Write the failure as a refutation of the assumption that produced the ISC. Update `RISKIEST ASSUMPTIONS` (which one did the failure refute?). Re-split or refine the offending ISC if its shape was wrong.
3. **Return to EXECUTE.** Apply the refined approach.
4. **Cap at 3 attempts.** On the 4th failure of the same ISC, escalate to the user with all three attempts as the evidence chain — do not keep iterating in isolation.

```
🔁 ISC-N failure → THINK
 🔁 attempt 1: [what was tried, what failed, what it refuted]
 🔁 attempt 2: [what was tried, what failed, what it refuted]
 🔁 attempt 3: [what was tried, what failed]
 🔁 escalating to user — assumption refuted: [name the assumption]
```

This is the only sanctioned back-edge in the Algorithm.

### 5. VERIFY

For every ISC, confirm it passed with tool-verified evidence. Cite the probe.

```
✅ VERIFICATION:
 ISC-N: [method used] — [evidence summary]
 Coverage: N/N passed
```

**Deliverable compliance check** — walk each D1..DN from PLAN and confirm it shipped:

```
📦 DELIVERABLE COMPLIANCE:
 📦 D1: [✓ shipped | ✗ missed | DEFERRED — reason]
```

**Re-read check** — final gate. Re-read the user's most recent message verbatim. For each explicit ask, confirm it was addressed:

```
🔄 RE-READ:
 🔄 [ask 1 — quote distinctive phrasing]: [✓ addressed | ✗ missed]
```

Any `✗` blocks completion. Either ship the missing piece or surface it as a known gap before declaring done.

### 6. LEARN

Reflect. Write to the WORK note under `## Learnings`:

```
🧠 LEARNING:
 🧠 What should I have done differently?
 🧠 Did the AP CHECK in THINK catch anything? Was it useful?
 🧠 Did the ISC failure loop fire? How many attempts before resolution?
 🧠 What would a smarter operator have done?
```

Then route durable discoveries to the right surface:

| Discovery type | Required target |
|----------------|-----------------|
| **Failure mode — tried X, it failed** | `knowledge/domain/anti-patterns.md` **(write it)** |
| **Confirmed right approach — verified and portable** | `knowledge/domain/patterns.md` **(write it)** |
| **Hard-won lesson from ISC failure loop (2+ attempts)** | `memory/effectus/wisdom.md` — one imperative sentence with `earned from: {slug} · {date}` |
| Insight worth keeping | `memory/learnings/{date}_{slug}.md` |
| Decision future work needs | `memory/decisions/{date}_{slug}.md` |
| State to resume later | `memory/current-focus.md` |
| Session summary | `memory/session-summaries/{date}_{slug}.md` |

The first three rows are **required writes** when triggered — not optional. A task that revealed a failure mode and wrote nothing to `anti-patterns.md` has an incomplete LEARN phase. This is how the workspace compounds: every task that goes through LEARN makes the next task's THINK smarter.

Set `phase: complete` in the WORK note.

## Mandatory Closing Format

Every Standard or Deep run ends with this block. Zero exceptions.

```
━━━ SUMMARY ━━━
📃 CONTENT: [the actual content if any]
🖊️ STORY: [4 bullets of ~8 words each — problem, action, result, next]
🗣️ NEXT: [one-sentence handoff or pause point]
```

After this block: nothing.

## Rules

- **No phantom phases.** If you skip a phase, name which one and why in the WORK note `## Decisions`.
- **Verification is required.** Tool-verified evidence per ISC. "Looks fine" is not evidence.
- **ISC failures route back to THINK.** Three attempts max; escalate on the fourth. Do not silently retry.
- **WORK note is the source of truth.** Not chat history. Not memory alone.
- **No silent stalls.** If you're stuck for more than three investigative loops on the same ISC, write what you tried and surface the blocker.
- **Plan means stop.** Explicit "plan first" requests end at PLAN.
- **LEARN is not optional.** A completed WORK note with no `## Learnings` entry is a doctrine violation on Standard or Deep work.

## Why Six Phases

THINK and LEARN are the two phases that make a workspace compound over time rather than just execute and forget.

**THINK** exists because planning and adversarial reasoning are different cognitive acts. Merging them into PLAN means the premortem and AP check get squeezed out under time pressure — the model optimizes for the deliverable, not for what could go wrong. Separating THINK forces the adversarial pass before any execution begins. The cost is one extra phase header; the benefit is catching the assumption that would have caused an ISC failure loop.

**LEARN** exists because a reflection line in VERIFY is too easy to skip or compress. A dedicated phase with mandatory routing targets makes the lesson durable: it goes to `anti-patterns.md` or `patterns.md` or `wisdom.md`, where the next session's THINK can find it. Without LEARN, the workspace is stateless — each session starts from scratch. With LEARN, each session starts smarter than the last.

This holds for solo users and small teams equally. A solo user compounds their own hard-won lessons. A team compounds their shared institutional knowledge. The mechanism is the same; the scale of benefit grows with team size.
