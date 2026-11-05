# Changelog

All notable changes to Tenet are documented here.

## [Unreleased]

### Added — one-command install

- `install.sh`: `curl -fsSL https://raw.githubusercontent.com/MAGI-Systems-AI/OpenTenet/main/install.sh | sh` creates a new workspace with its own fresh git history (no remote pointing back at OpenTenet), runs bootstrap, and makes an initial commit. Refuses non-empty folders, never prompts, cleans up after a failed run.
- CI `install-smoke` job on Ubuntu and macOS: installs from the commit under test and asserts no remote, clean tree, hook installed, and that re-running bootstrap leaves the tree clean.

### Fixed

- Re-running `./bootstrap.sh` no longer dirties git: generated files are only rewritten when content other than the `updated:` / `generated_at:` stamps changed.
- Generated files are byte-identical on macOS and Linux (generators now sort with `LC_ALL=C`; the skills order used to follow the locale).
- Bootstrap builds the skills catalog before the session context that embeds it, so one run is enough after adding a skill.
- Wiring files and onboarding docs described a 4-phase loop; they now match the 6-phase Algorithm (OBSERVE → THINK → PLAN → EXECUTE → VERIFY → LEARN), including the "verify it loaded" expected answer. Doctrine manifest re-baselined.
- README and bootstrap said 3 built-in skills; 4 ship.

### Added — optional team mode

- Team layer under `team/`: roster, conventions (branches, review, generated files, handoff contract), team discoveries, member files, and member morning/close session prompts.
- Operational lanes: `team/lanes/{slug}.md` charters with owner, backup, path scope and status, plus a lanes map.
- `bin/tenet-lane` (stdlib): `list`, `whose <path>`, `show`, `members`, `check` — ownership lookup and validation (owners on the roster, valid statuses, no overlapping held scopes, every lane mapped). Runs in CI.
- `core/team-operations.md` doctrine; constitution v1.2 adds the check-before-editing-another-lane rule and team LEARN routing; WORK notes gain `owner:` / `lane:` in team mode.
- Templates: `member-template.md`, `lane-template.md`. Session context includes the roster and lanes map in team mode.
- Solo workspaces are unaffected: with no member files every team rule is inert and `tenet-lane` reports solo mode.

## [1.0.0] — 2026-05-24

### Initial release

- 4-phase algorithm: OBSERVE → PLAN → EXECUTE → VERIFY
- Hard-imperative constitution (10 NEVER + 9 ALWAYS + 8 BEFORE)
- ISC doctrine with Splitting Test and Parallel Groups (optional for solo use)
- Verification doctrine with required-probe table per artifact type
- Quick / Standard / Deep effort tiering with vendor-neutral reasoning-effort mapping
- 3 general-purpose skills: planning, research-synthesizer, code-review
- Individual memory system: identity, current-focus, goals, work notes, learnings, decisions
- LLM-agnostic vendor wiring: Claude Code, Gemini CLI, Cursor, Aider, Codex, Copilot Chat
- 16-pattern pre-commit secret scanner
- Frontmatter validation on staged markdown
- One-command bootstrap: `./bootstrap.sh`
- Vendor-neutral skill discovery CLI: `bin/tenet-skill`
