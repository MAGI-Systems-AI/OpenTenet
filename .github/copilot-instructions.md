# Tenet — GitHub Copilot Chat Instructions

Read `memory/session-context.md` at the start of every session. It contains the constitution, the 4-phase algorithm (OBSERVE → PLAN → EXECUTE → VERIFY), the ISC doctrine, and the skills catalog.

## Non-negotiable defaults (from constitution.md)

- NEVER mark an ISC `[x]` without tool-verified evidence.
- NEVER invent file paths, command names, or APIs. Search first.
- NEVER skip a phase on Standard or Deep work.
- ALWAYS create a WORK note at `memory/work/{slug}.md` for non-trivial tasks.
- ALWAYS include at least one anti-criterion in every WORK note.
- ALWAYS prefer the smallest reversible step that reduces uncertainty.

## On non-trivial work

Run the 6-phase loop: OBSERVE (intent + current state + ISCs) → THINK (risks + premortem + anti-pattern check) → PLAN (scope + deliverables) → EXECUTE (work + inline verification) → VERIFY (evidence per ISC + re-read check) → LEARN (route lessons to knowledge/).

## Skills

`bin/tenet-skill list` — one line per skill. `bin/tenet-skill show <name>` — full SKILL.md.

## Team mode

Only when `team/members/` holds a member file (`core/team-operations.md`): before editing a path, run `bin/tenet-lane whose <path>`; if another member's active or blocked lane owns it, ask that owner instead of editing.
