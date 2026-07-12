#!/usr/bin/env python3
"""
install-codex-config.py — TOML-aware Codex config wiring.

Inserts `developer_instructions` (as a top-level key, before any [section]
header) and a `[projects."<workspace>"]` block with `trust_level = "trusted"`
into ~/.codex/config.toml.

Designed to be safe-by-default:
  • Refuses to clobber an existing developer_instructions (use --force).
  • Writes a timestamped backup of the current config before any change.
  • Round-trip parses the result with tomllib; aborts on parse failure.
  • Long arrays in the existing config are preserved verbatim (we only
    prepend the new keys + section; we do not rewrite existing content).

Why this script exists:
  Line-based Edit tools append keys at end-of-file. In TOML, end-of-file
  is almost always inside a [section], which means an inserted top-level
  key gets scoped to that section and fails the schema. That is the
  exact failure mode that caused Codex to refuse to launch on a real
  install. See core/CODEX_INTEGRATION.md Step 2.5.

Usage:
  tools/scripts/install-codex-config.py [--workspace PATH] [--config PATH]
                                        [--dry-run] [--force]
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import time
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # pip install tomli  (Python 3.10 backport)
    except ModuleNotFoundError:
        sys.exit(
            "ERROR: tomllib not available. Requires Python 3.11+, or Python 3.10 with tomli:\n"
            "       pip install tomli\n"
            "       Or wire config.toml manually: core/CODEX_INTEGRATION.md Step 2.5."
        )


DEFAULT_CONFIG = Path.home() / ".codex" / "config.toml"


def workspace_root_from_script() -> Path:
    # Script lives at <repo>/tools/scripts/install-codex-config.py
    return Path(__file__).resolve().parent.parent.parent


def render_block(workspace: Path) -> str:
    ws = str(workspace)
    return f'''developer_instructions = """
This workspace is at {ws}.

At the start of every session, read {ws}/memory/session-context.md.
That file is the synthesized startup context: constitution, algorithm, ISC
doctrine, identity, current focus, decision rules, and the skills catalog.

For any non-trivial work (multi-file, ambiguous, or touching core/, memory/,
or projects/{{name}}/), follow core/ALGORITHM.md — create a WORK note at
memory/work/{{slug}}.md and run the six phases (Observe, Think, Plan,
Execute, Verify, Learn).

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

[projects."{ws}"]
trust_level = "trusted"
'''


DEV_INSTR_RE = re.compile(r'^\s*developer_instructions\s*=', re.MULTILINE)


def find_first_section_index(lines: list[str]) -> int:
    """Index of the first [section] header line, or len(lines) if none."""
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("[") and not stripped.startswith("[["):
            # Skip if it's clearly inside a multi-line string — best-effort.
            return i
    return len(lines)


def has_workspace_project(text: str, workspace: Path) -> bool:
    needle = f'[projects."{workspace}"]'
    return needle in text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workspace", type=Path, default=workspace_root_from_script(),
                        help="Workspace root to wire (default: this repo)")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG,
                        help=f"Codex config to edit (default: {DEFAULT_CONFIG})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print proposed new content to stdout; do not write")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite an existing developer_instructions block")
    args = parser.parse_args(argv)

    workspace: Path = args.workspace.resolve()
    config: Path = args.config

    if not workspace.is_dir():
        sys.exit(f"ERROR: workspace not found or not a directory: {workspace}")
    if not (workspace / "core" / "ALGORITHM.md").is_file():
        sys.exit(f"ERROR: {workspace} does not look like a Tenet workspace (no core/ALGORITHM.md).")

    # Read current config (or treat as empty if absent)
    existing = config.read_text() if config.is_file() else ""

    # Refuse to clobber unless --force
    if DEV_INSTR_RE.search(existing) and not args.force:
        sys.exit(
            "ERROR: ~/.codex/config.toml already contains a developer_instructions block.\n"
            "       Re-run with --force to overwrite, or edit manually following\n"
            "       core/CODEX_INTEGRATION.md Step 2.5.\n"
            f"       Target file: {config}"
        )

    # Strip any existing developer_instructions block (only fires under --force)
    if args.force and DEV_INSTR_RE.search(existing):
        existing = strip_dev_instructions(existing)

    new_block = render_block(workspace)

    # Compose: top-level keys (including the new block) above the first [section] header.
    existing_lines = existing.splitlines(keepends=True) if existing else []
    first_section = find_first_section_index(existing_lines)
    top = "".join(existing_lines[:first_section])
    sections = "".join(existing_lines[first_section:])

    # Ensure top ends with exactly one blank line before the new block
    if top and not top.endswith("\n"):
        top += "\n"
    if top and not top.endswith("\n\n"):
        top += "\n"

    composed = top + new_block

    # If the workspace's [projects."..."] entry is missing, append it; if present
    # in the existing sections we leave it alone (idempotent).
    if not has_workspace_project(existing, workspace):
        if sections and not sections.startswith("\n"):
            composed += "\n"
        composed += sections
    else:
        composed += sections

    # Round-trip validate
    try:
        tomllib.loads(composed)
    except tomllib.TOMLDecodeError as e:
        sys.exit(f"ERROR: round-trip TOML parse failed; refusing to write.\n  {e}")

    if args.dry_run:
        sys.stdout.write(composed)
        return 0

    # Backup + write
    config.parent.mkdir(parents=True, exist_ok=True)
    if config.is_file():
        backup = config.with_suffix(config.suffix + f".bak.{int(time.time())}")
        shutil.copy2(config, backup)
        print(f"Backup: {backup}")
    config.write_text(composed)
    print(f"Wrote:  {config}")
    print(f"Workspace wired: {workspace}")
    return 0


def strip_dev_instructions(text: str) -> str:
    """Remove an existing developer_instructions = \"\"\"...\"\"\" block. Best-effort."""
    pattern = re.compile(
        r'\n?developer_instructions\s*=\s*"""[\s\S]*?"""\s*\n',
        re.MULTILINE,
    )
    return pattern.sub("\n", text, count=1)


if __name__ == "__main__":
    raise SystemExit(main())
