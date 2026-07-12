---
title: Effort Tiering
type: rule
domain: tenet
product: Tenet
audience: team
owner: team
status: active
updated: 2026-05-14
version: v1.0
tags:
  - effort
  - tiering
  - algorithm
  - doctrine
artifact_type: operating-rule
---

# Effort Tiering

> **Three tiers. Quick, Standard, Deep.** They determine whether the Algorithm runs, how much ceremony to apply, and the ISC count floor that must be met. Tiering is a budget — not a quality signal. Quick is not "lazy"; it is "matched to a small task." Deep is not "thorough"; it is "matched to a task that earns the ceremony."

## The Three Tiers

| Tier | Time budget | ISC floor | Algorithm? | WORK note? | Reasoning effort | When |
|------|-------------|-----------|-----------|------------|------------------|------|
| **Quick** | < 90 seconds | none | No — go straight to execution | No | `low` — no extended thinking | One-file edit, one command, one fact lookup, one URL probe. No new artifact created. No multi-step plan. |
| **Standard** | < 10 minutes | ≥ 4 (incl. ≥1 anti) | Yes — full six phases | Yes | `medium` — extended thinking on THINK + VERIFY | Multi-file work. Anything ambiguous. Anything touching `core/`, `memory/`, or `projects/{name}/` doctrine. New skill. New template. |
| **Deep** | < 60 minutes | ≥ 12 (incl. ≥2 anti, ≥1 antecedent if experiential) | Yes — full six phases + explicit Decisions log | Yes (with `## Decisions` populated) | `high` — extended thinking on THINK + PLAN + VERIFY | Architecture decisions. Cross-project changes. Governance updates. Anything that will be referenced again. Anything externally visible. |

**Bias toward Standard when in doubt.** Under-scoping is the failure mode this tiering was built to prevent. The cost of running the Algorithm on something that turns out to be Quick is small (you produce a 4-ISC WORK note and ship the answer). The cost of *not* running it on something that turns out to be Deep is large (silent doctrine violations, missed deliverables, regressions).

## Why Codex Needs Tiering

Claude Code's Algorithm has five tiers (E1–E5) because Anthropic's models follow long imperative rule sets reliably and benefit from finer-grained ceremony control. Codex follows three tiers because the marginal benefit of finer distinctions does not survive in the model's behavior — Codex treats E2 and E3 about the same. Three tiers is the granularity Codex actually responds to.

If you find yourself wishing for a fourth tier ("Standard but lighter"), the fix is almost always: run a Quick task and skip the ceremony entirely, OR run a Standard task and accept the 5-minute floor. Don't invent intermediate tiers — the doctrine breaks down when there are too many.

## Override Mechanism

The user may name the tier explicitly in the active prompt:

- `quick:` prefix → force Quick
- `standard:` prefix → force Standard
- `deep:` prefix → force Deep

Explicit override beats the executor's judgment. If the user prefixes `quick:` on a request that looks Deep-shaped, run it Quick and surface the mismatch in the response — don't silently escalate.

## Auto-Detection Rules (Executor Side)

If the user does not name a tier:

1. **Default to Quick** if the request is a single fact lookup, a single one-line edit on a named file, or a single command to run.
2. **Escalate to Standard** if any of: multiple files touched, multiple steps required, ambiguity in the request, an artifact is being created, a new file is being added, a config is being changed.
3. **Escalate to Deep** if any of: doctrine files (`core/`, `memory/effectus/`) being modified, cross-project changes, an externally-visible action (push, PR, message), an architecture decision, a governance update.

Document the chosen tier in the WORK note's frontmatter (`tier: standard` or `tier: deep`) along with the matching `reasoning_effort:` per the table above. For Quick tasks no WORK note is created, so document the tier choice inline if the response would benefit from it.

## Reasoning Effort — Vendor-Neutral Budget Signal

The WORK note's `reasoning_effort:` field is a vendor-neutral budget signal that each LLM harness maps to native controls:

| Tenet signal | OpenAI GPT family | Anthropic Claude | Google Gemini |
|------------|-------------------|------------------|---------------|
| `low` | `reasoning_effort: low` | extended-thinking budget = 0 | `thinkingConfig.thinkingBudget = 0` |
| `medium` | `reasoning_effort: medium` | extended-thinking budget ≈ 8K tokens | `thinkingBudget ≈ 2048` |
| `high` | `reasoning_effort: high` | extended-thinking budget ≈ 24K+ tokens | `thinkingBudget ≈ 8192` |

The doctrine produces the *signal*; the harness produces the *behavior*. If a vendor's model lacks a reasoning-budget control, the harness ignores the field — the doctrine remains valid.

**Why this matters:** Quick tasks waste tokens on extended thinking; Deep tasks underperform without it. Mapping tier directly to reasoning effort is free quality on every modern LLM.

## Escalation Mid-Task

If a Quick task starts revealing Deep-shaped complexity (e.g. "edit one line" turns into "refactor a module"), STOP and re-tier. Surface the escalation:

> "This is now Standard scope — the change touches three files and needs verification probes. Re-running with the Algorithm."

Then create the WORK note and run OBSERVE → THINK → PLAN.

The opposite — Deep → Standard de-escalation — is rarer but legitimate. If THINK reveals the work is simpler than OBSERVE suggested, document the de-escalation in `## Decisions` and proceed at the lower tier.

## ISC Floors Per Tier

The floors come from `core/ISC.md`. They are **soft minima**, not targets:

- Quick: no floor; the Splitting Test still applies to anything that needs verification
- Standard: ≥ 4 ISCs, including ≥ 1 anti-criterion
- Deep: ≥ 12 ISCs, including ≥ 2 anti-criteria; ≥ 1 antecedent if the goal is experiential

If the Splitting Test naturally produces more ISCs than the floor, write them all. Padding the count to hit a floor is a doctrine violation — the floor catches *under*-articulation, not adequate articulation.

## Examples

- "What's the path to the constitution?" → **Quick** (single fact lookup)
- "Add a line to identity.md" → **Quick** (single one-line edit)
- "Wire the new skill into the catalog" → **Standard** (multi-file: SKILL.md + skills-map + skills-catalog regen)
- "Rewrite the constitution as hard imperatives" → **Standard** (single file but doctrine; needs ISCs)
- "Port EFFECTUS schema and update memory-map and synthesizer" → **Deep** (multi-file doctrine + scripts + cross-link updates)
- "Plan the v1.0 upgrade across three tiers" → **Deep** (architecture decision, multiple deliverables, externally-visible artifact)

## Why This Is a Doctrine File, Not a Prompt Hint

Tiering encoded in a doctrine file under `core/` survives every reset, every new teammate, every new Codex session. Tiering encoded only in a prompt evaporates the moment the conversation ends. The whole point of v1.0 is that discipline lives in the *file*, not in the *model* or the *moment*. Effort tiering is one of those disciplines.

## Related

- `core/ALGORITHM.md` — the six-phase loop these tiers gate
- `core/ISC.md` — the binary-tool-probe doctrine that produces the count floor
- `core/constitution.md` — the imperatives that say "ALWAYS run the Algorithm on Standard or Deep work"
