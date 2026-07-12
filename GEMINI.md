# Tenet — Google Gemini CLI Wiring

Google Gemini CLI reads this file at every session start. It loads Tenet's doctrine, your personal context, and the skills catalog before any work begins.

## Session Bootstrap

The synthesized startup context lives in `memory/session-context.md`. That single file catenates the constitution, the 4-phase algorithm, the ISC doctrine, the verification doctrine, effort tiering, your identity, current focus, goals, and the skills catalog.

**Read `memory/session-context.md` at the start of every session.** Regenerate it after any change to its sources with `tools/scripts/build_session_context.sh`.

## What To Follow

For any **non-trivial work** (multi-file, ambiguous, touching `core/`, `memory/`, or `projects/{name}/`):

- Run the 4-phase Algorithm. See `core/ALGORITHM.md`. Phases: OBSERVE → PLAN → EXECUTE → VERIFY.
- Create a WORK note at `memory/work/{slug}.md` (or `projects/{name}/WORK.md` for project work). The WORK note is the system of record.
- Write acceptance criteria per `core/ISC.md`. Every criterion is one binary tool probe. Apply the Splitting Test.
- Hold to the verification doctrine. See `core/verification-doctrine.md`. Tool-verified evidence required before marking any ISC `[x]`.
- Read the constitution. See `core/constitution.md`. The NEVER / ALWAYS / BEFORE rules are non-negotiable defaults.

For **skills**, use the vendor-neutral CLI:

- `bin/tenet-skill list` — one line per skill, name + description
- `bin/tenet-skill show <name>` — print the full `SKILL.md` to stdout
- `bin/tenet-skill path <name>` — print the absolute path

## Gemini-Specific Notes

- **Reasoning budget.** Map Tenet's `reasoning_effort:` field (`low` / `medium` / `high` in the WORK note frontmatter) to Gemini's `thinkingConfig.thinkingBudget`. Recommended: `low` → 0, `medium` → 2048, `high` → 8192. See `core/effort-tiering.md` for the full vendor-mapping table.
- **Parallel tool calls.** Gemini supports parallel function calls in a single response. ISCs tagged `parallel_group:` should be verified by batching the probes in one turn rather than serializing them.
- **Long context window.** Gemini's large context lets the full `memory/session-context.md` fit comfortably. Load it once and keep it active.

## Keep Higher-Priority Instructions in Force

This file adds Tenet scaffolding on top of Gemini CLI's defaults. When in doubt, the active prompt wins; Tenet doctrine wins on anything the active prompt doesn't speak to.

## Verifying the Wiring

Ask:

> What's in `memory/session-context.md`? Summarize what this workspace is and what rules I'm operating under.

If Gemini describes the constitution, the 4-phase algorithm, the ISC doctrine, the verification doctrine, the effort tiering, your identity, and the skills catalog — the wiring works.
