---
title: AI Coding-Assistant CLI Adapters
type: reference
domain: tenet
product: Tenet
audience: individual
owner: operator
status: active
updated: 2026-05-24
version: v1.0
tags:
  - llm-agnostic
  - cli-adapters
  - integration
  - vendor-neutral
artifact_type: integration-guide
---

# AI Coding-Assistant CLI Adapters

> Tenet is vendor-neutral by design. The doctrine never branches per coding-assistant CLI — the constitution's NEVER list, the four-phase Algorithm, ISC granularity, the skills, the templates all run identically across vendors. **Only the startup-wiring file differs.** This document is the table of those wiring conventions plus concrete adapter recipes, and includes the Codex-specific pitfalls that have caused the highest-cost defects in this workspace's history.

## Skill Discovery & Loading — `bin/tenet-skill`

Tenet ships a **vendor-neutral CLI** for skill discovery and on-demand load. Every coding-assistant CLI uses the same convention:

```sh
bin/tenet-skill list           # one line per skill: name + description (cheap discovery)
bin/tenet-skill show <name>    # print the full SKILL.md to stdout (on-demand load)
bin/tenet-skill path <name>    # print the absolute path (for `@`-mention style references)
bin/tenet-skill help           # print full usage
```

The CLI is the universal primitive. It auto-detects the workspace root, reads every `skills/*/SKILL.md` once, and parses the frontmatter `name:` and `description:` fields. No vendor-specific assumptions; Python 3 stdlib only; zero external dependencies.

**Why a CLI instead of per-vendor slash commands.** Slash commands (`/skill ...`) are a Claude Code / Cursor surface that doesn't exist under Codex, Gemini CLI, or Aider. Building the discovery layer once as a CLI gives every CLI the same UX via shell-out, lets you compose with standard tools (`bin/tenet-skill list | grep security`), and keeps the source of truth in the `skills/` tree rather than duplicated across N vendor-specific command directories.

**Why not just eager-load every SKILL.md.** Each `SKILL.md` is ~100-200 lines. Loading all of them into every session burns context for skills that won't be invoked. The CLI's `list` returns ~10 lines (one per skill); `show` only fires when a skill is actually being run.

**Naming convention.** Skill names match the `name:` field in each skill's frontmatter (same as the directory name today). Adding a new skill requires only `skills/<new-name>/SKILL.md` with valid frontmatter — the CLI auto-discovers it; no registration step.

## Shipped Wirings — First-Class

Tenet ships three vendor-specific wiring files in the box:

| Vendor | Wiring file | Auto-installed? |
|--------|-------------|----------------|
| OpenAI Codex (GPT family) | `~/.codex/config.toml` `developer_instructions` block | `bootstrap.sh` prints the block; `tools/scripts/install-codex-config.py` writes it safely |
| Anthropic Claude Code (Claude family) | `CLAUDE.md` at repo root | Already in repo — no install step |
| Google Gemini CLI (Gemini family) | `GEMINI.md` at repo root | Already in repo — no install step |

All three reference `memory/session-context.md` as the actual payload. The synthesized context is the same; the wiring is just a vendor-specific pointer.

## Codex Wiring — Step by Step

### Step 1 — Generate the session context

From the workspace root:

```sh
tools/scripts/build_session_context.sh
```

This writes `memory/session-context.md`. The script is idempotent — run it after any change to `core/`, `memory/identity.md`, `memory/current-focus.md`, or the skills map.

Verify the output:

```sh
wc -l memory/session-context.md
head -40 memory/session-context.md
```

### Step 2 — Wire Codex's `developer_instructions`

**Recommended path (TOML-aware, idempotent):**

```sh
tools/scripts/install-codex-config.py
```

This script reads `~/.codex/config.toml`, refuses to clobber an existing `developer_instructions` (rerun with `--force` to overwrite), writes a timestamped backup, prepends `developer_instructions` at the **top of the file** (as a top-level key — must appear before any `[section]` header), adds a `[projects."<this-workspace>"]` entry with `trust_level = "trusted"`, and round-trip-validates the resulting TOML before saving.

Flags:

- `--dry-run` — print the proposed new file to stdout without writing
- `--workspace PATH` — wire a workspace other than the one the script lives in
- `--config PATH` — target a config file other than `~/.codex/config.toml`
- `--force` — overwrite an existing `developer_instructions` block

The block the script writes is:

```toml
developer_instructions = """
This workspace is at WORKSPACE_PATH.

At the start of every session, read WORKSPACE_PATH/memory/session-context.md.
That file is the synthesized startup context: constitution, algorithm, ISC
doctrine, identity, current focus, decision rules, and the skills catalog.

For any non-trivial work (multi-file, ambiguous, or touching core/ or
memory/), follow core/ALGORITHM.md — create a WORK note at
memory/work/{slug}.md and run the four phases (Observe, Plan, Execute, Verify).

For acceptance criteria, follow core/ISC.md — every criterion is one binary
tool probe; tool-verified evidence required before marking [x].

For skills, use the vendor-neutral CLI at bin/tenet-skill:
  bin/tenet-skill list           list every skill, one line each (cheap discovery)
  bin/tenet-skill show <name>    print the full SKILL.md to stdout (on-demand load)
  bin/tenet-skill path <name>    print the absolute path
This convention is shared by every coding-assistant CLI Tenet supports.
skills/skills-map.md remains as a human-browsable index.

Keep higher-priority system instructions in force. Use this workspace as
added scaffolding, not as a replacement for Codex behavior.
"""

[projects."WORKSPACE_PATH"]
trust_level = "trusted"
```

`WORKSPACE_PATH` is substituted with the workspace's real absolute path.

### Step 3 — Refresh on source changes

Every time you edit one of the files synthesized into `memory/session-context.md`, the synthesized file drifts. Two options for keeping it current:

**Option A — Manual refresh:**

```sh
tools/scripts/build_session_context.sh
git add memory/session-context.md
git commit -m "refresh session context"
```

**Option B — Pre-commit git hook:**

Add this hook to `.git/hooks/pre-commit` (or install via `tools/scripts/install_git_hooks.sh`):

```sh
#!/bin/sh
# Auto-regenerate session-context.md when its source files change.
if git diff --cached --name-only | grep -qE '^(core/|memory/identity\.md|memory/current-focus\.md|skills/skills-map\.md|LAUNCHER\.md|active-work-map\.md)'; then
    tools/scripts/build_session_context.sh
    git add memory/session-context.md
fi
```

### Step 4 — Confirm Codex is reading it

In a fresh Codex session, ask:

> "What's in memory/session-context.md?"

If Codex describes the constitution + Algorithm + ISC + identity + current focus, the wiring works. If Codex says "I don't see that file", the path in `developer_instructions` is wrong or the file wasn't generated.

## Codex Critical Pitfalls

The single highest-cost defect this workspace has ever produced was Codex auto-editing `~/.codex/config.toml` and breaking its own ability to launch. The failure mode is mechanical and reproducible — these are the four pitfalls that combine to cause it. **Read this section before any manual edit of `config.toml`.**

### Pitfall 1 — `developer_instructions` is a TOP-LEVEL key

It must appear in `config.toml` **before any `[section]` header**. TOML scoping is positional: every key after a `[section]` header is owned by that section until the next header. If `developer_instructions = """..."""` lands after `[tui.model_availability_nux]`, the parser tries to validate the string against that section's schema (declared as `u32`-only model availability counts) and refuses the file with:

```
Error loading config.toml: invalid type: string "...", expected u32 in `tui.model_availability_nux`
```

Codex then refuses to launch — no fallback, no defaults, no graceful degradation. One bad key = no app.

Correct (top of file, before any `[section]`):

```toml
model = "gpt-5.4-mini"

developer_instructions = """
...
"""

[projects."/path/to/workspace"]
trust_level = "trusted"
```

Wrong (after a section header):

```toml
[tui.model_availability_nux]
"gpt-5.5" = 4
developer_instructions = """     # ← parser binds this to [tui.model_availability_nux] → schema break
...
"""
```

### Pitfall 2 — Codex must NOT auto-edit `~/.codex/config.toml`

Codex's Edit tool is line-based and TOML-AST-blind. When asked (or implicitly invited by a "check that config has X" test step) to fix a missing `developer_instructions`, Codex will append the key at end-of-file. End-of-file is almost always inside a `[section]` — see Pitfall 1.

The constitution forbids this: `NEVER programmatically modify ~/.codex/config.toml`. If a session asks Codex about config wiring, Codex should surface the change in `## Decisions` for operator-manual application, or recommend `tools/scripts/install-codex-config.py`. **Do not invite Codex to auto-fix the wiring.**

### Pitfall 3 — TextEdit silently corrupts TOML

macOS TextEdit's default mode is rich-text. Opening `config.toml` in TextEdit and saving it converts straight quotes `"` to smart quotes `"` `"` — TOML's parser does not recognize smart quotes as string delimiters, and the file becomes invalid with errors like:

```
key with no value, expected '='
```

Use `nano`, `vim`, `micro`, VS Code, or any plain-text editor. Verify after edit with:

```sh
file ~/.codex/config.toml      # should say: ASCII text  or  UTF-8 Unicode text
```

If it says `RTF` or anything else, TextEdit (or another rich-text editor) corrupted it.

### Pitfall 4 — Terminal paste can break long array lines

The `notify = [...]` line in a typical Codex config is ~200+ chars. Pasting into Terminal occasionally inserts a soft-wrap newline into the middle of the array, producing:

```
toml 4:3: missing comma between array elements, expected ','
```

When writing long arrays via heredoc, **break them across lines manually**:

```toml
notify = [
    "/path/with spaces/to/some/long/binary",
    "turn-ended",
]
```

The `install-codex-config.py` helper handles this automatically — multi-line array form for any value >80 chars.

### Recovery — if config.toml is already broken

```sh
ls -t ~/.codex/config.toml.bak.* | head -1 | xargs -I{} cp {} ~/.codex/config.toml
codex
```

Restores the most recent timestamped backup (created by `install-codex-config.py` or any previous safe-wiring run).

## Adapter Recipes — Other CLIs

### Cursor

Cursor reads instruction files from either `.cursorrules` (legacy single-file) or `.cursor/rules/*.md` (newer multi-file structured rules). Both are at the repo root.

**Minimal adapter:**

```
# .cursorrules
This workspace is Tenet. See memory/session-context.md at the start of
every session — it catenates the constitution, the four-phase Algorithm,
ISC doctrine, verification doctrine, effort tiering, identity, current
focus, and the skills catalog.

For non-trivial work, follow core/ALGORITHM.md (OBSERVE → PLAN → EXECUTE →
VERIFY, with ISC failure routing back to PLAN, max 3 attempts before
escalation).

For acceptance criteria, follow core/ISC.md — every criterion is one binary
tool probe. Tag independent ISCs with parallel_group: to batch verification.

For the constitution's NEVER list, see core/constitution.md.
```

Map Tenet's `reasoning_effort:` field to Cursor's model-selection (Cursor uses different model tiers; high → top-tier model, low → fast model).

### Aider

Aider reads `.aider.conf.yml` at the repo root. The doctrine wiring goes in the `read` field (files Aider auto-loads as read-only context):

```yaml
# .aider.conf.yml
read:
  - memory/session-context.md
  - core/constitution.md
  - core/ALGORITHM.md
  - core/ISC.md
  - core/verification-doctrine.md
```

Aider auto-includes these in every session's context.

### GitHub Copilot Chat (repo-level instructions)

GitHub Copilot Chat (in VS Code, JetBrains, etc.) reads `.github/copilot-instructions.md` for repo-level instructions:

```markdown
# .github/copilot-instructions.md
This workspace is Tenet. When working in this repo, follow the doctrine
in `memory/session-context.md` — it carries the constitution, the four-phase
Algorithm, ISC granularity discipline, and the verification doctrine.

For non-trivial work: create a WORK note at memory/work/{slug}.md, run the
Algorithm, mark ISCs [x] only with tool-verified evidence.

NEVER claim a criterion passed without showing the probe output.
NEVER edit files outside this workspace without an explicit instruction.
NEVER bypass safety checks (--no-verify, hook disabling, etc.).
```

### Continue.dev

Continue uses `.continuerc.json` or `config.json` at the user level. For repo-specific instructions, set `systemMessage` to reference the workspace:

```json
{
  "systemMessage": "When working in this repository, read memory/session-context.md for the operating context. Follow the four-phase Algorithm in core/ALGORITHM.md for non-trivial work. Use one-binary-tool-probe ISCs per core/ISC.md. Tool-verified evidence required before marking any ISC complete."
}
```

### Cody (Sourcegraph)

Cody reads `.sourcegraph/codycontext.md` or `.cody/instructions.md` depending on version:

```markdown
# .sourcegraph/codycontext.md
Tenet workspace. Operating context at memory/session-context.md.
Four-phase Algorithm at core/ALGORITHM.md. Constitution at
core/constitution.md. ISC doctrine at core/ISC.md. Verification doctrine
at core/verification-doctrine.md.

Follow the doctrine on any non-trivial task.
```

## Per-Vendor Reasoning-Effort Mapping

Tenet's WORK note carries `reasoning_effort: low | medium | high`. Each vendor's harness maps it to native controls:

| Tenet signal | OpenAI GPT family | Anthropic Claude | Google Gemini | Cursor | Others |
|-----------------|-------------------|------------------|---------------|--------|--------|
| `low` | `reasoning_effort: low` | extended-thinking budget 0 | `thinkingBudget: 0` | fast model | minimum reasoning |
| `medium` | `reasoning_effort: medium` | ~8K tokens | ~2048 | mid-tier model | balanced reasoning |
| `high` | `reasoning_effort: high` | ~24K+ tokens | ~8192 | top-tier model | maximum reasoning |

The doctrine produces the *signal*; the harness produces the *behavior*. Vendors lacking a reasoning-budget control ignore the field — the doctrine remains valid.

## Per-Vendor Parallel-Tool-Call Support

Tenet's `parallel_group:` ISC tag instructs the VERIFY phase to batch probes in a single response. Vendor support today:

| Vendor | Parallel function/tool calls in one response | Tenet `parallel_group` exploits this? |
|--------|----------------------------------------------|------------------------------------------|
| OpenAI Codex / GPT family | Yes (native) | Fully |
| Anthropic Claude | Yes (native) | Fully |
| Google Gemini | Yes (native) | Fully |
| Cursor | Yes (depends on selected model) | Inherited from underlying model |
| Aider | Sequential by design | No — `parallel_group:` runs serially |
| GitHub Copilot Chat | Variable by version | Best-effort |
| Continue | Yes for supported models | Yes for GPT/Claude/Gemini-backed |

Where parallel-call support exists, Tenet's VERIFY phase compresses N independent probes into one round-trip. Where it doesn't, the same probes run serially but the doctrine remains identical — the `parallel_group:` tag becomes a hint, not a directive.

## What Codex Wiring Does NOT Do

- **No hooks.** Codex does not have `PreToolUse`/`PostToolUse`/`SessionStart` hook events. If you want runtime checks (security inspection, pattern matching), put them in a **git pre-commit hook** instead. The workspace already ships `tools/scripts/install_git_hooks.sh` for that pattern.
- **No subagents.** Codex does not have a native `Agent(subagent_type=...)` primitive. If a skill needs delegation, the skill itself defines the shape of the sub-call (e.g. a CLI it invokes).
- **No voice.** Skip the voice-announcement pattern entirely.

## Adding a New CLI

When a new coding-assistant CLI is adopted:

1. Identify its convention for "load at session start" instruction file (it will have one; every modern CLI does).
2. Create a thin wiring file at the convention's location that references `memory/session-context.md` for the operating context and the relevant `core/*.md` doctrine files.
3. Document the convention in this file's "Adapter Recipes" section.
4. If the CLI supports a reasoning-budget control, add its mapping to the `reasoning_effort:` table above.
5. If the CLI supports parallel tool calls, mark it `Yes` in the parallel-tool-call table.

## Why This Architecture Works

The clean separation between doctrine and wiring is what makes Tenet vendor-neutral. Adopting Tenet on Codex today and switching to Gemini CLI next year changes one wiring file — everything else (the constitution, the Algorithm, the skills, the workflows, the templates, the knowledge collections) stays untouched.

A workspace operated across multiple CLIs runs from the same doctrine, the same workflows, the same skills catalog. Decisions made in one session compose with decisions made in another regardless of which CLI authored them. That's the operational guarantee LLM-agnosticism actually buys.

## Compared Across Vendors

| Concern | Claude Code | Codex | Gemini CLI |
|---------|-------------|-------|------------|
| Startup context load | `@-imports` in `CLAUDE.md` | Synthesized `memory/session-context.md` + `config.toml` `developer_instructions` | `GEMINI.md` pointer to `memory/session-context.md` |
| Phase enforcement | Hooks + model self-discipline | The WORK note format | The WORK note format |
| Runtime tool inspection | Native hooks | Pre-commit git hooks | Pre-commit git hooks |
| Verification | Inline `## Verification` evidence in WORK notes | Inline `## Verification` evidence in WORK notes | Inline `## Verification` evidence in WORK notes |

The architectural finding: **Claude Code lets the harness be light because the model carries discipline. Codex needs the harness to be deterministic because the model won't.** Tenet externalizes the discipline that Claude Code provides intrinsically. That's not a weakness of Codex — it's a different design pressure with the same destination.

## Related

- `core/ALGORITHM.md` — the four-phase loop
- `core/constitution.md` — the NEVER / ALWAYS / BEFORE imperatives
- `core/ISC.md` — the `parallel_group:` ISC primitive
- `core/effort-tiering.md` — reasoning-effort mapping per tier
- `core/verification-doctrine.md` — required probes per artifact type
