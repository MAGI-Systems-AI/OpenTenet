#!/usr/bin/env python3
"""Check basic Tenet navigation and governance health."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

ALLOWED_ROOT_FILES = {
    # Tenet workspace conventions
    ".gitignore",
    "active-work-map.md",
    "LAUNCHER.md",
    "START_HERE.md",
    "bootstrap.sh",
    # Standard open-source repository files (belong at the root by convention)
    "LICENSE",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "ROADMAP.md",
    # AI coding assistant wiring (root-level by each vendor's convention)
    "CLAUDE.md",   # Claude Code reads this at session start (@-imports memory/session-context.md)
    "GEMINI.md",   # Google Gemini CLI reads this at session start
    "AGENTS.md",   # OpenAI Codex hierarchical AGENTS.md convention (optional alternative to config.toml)
}

TOP_LEVEL_MAPS = {
    "core": "core/core-map.md",
    "knowledge": "knowledge/knowledge-map.md",
    "memory": "memory/memory-map.md",
    "projects": "projects/projects-map.md",
    "templates": "templates/templates-map.md",
}

NESTED_MAPS = {
    "memory/decisions": "memory/decisions/decisions-index.md",
    "memory/learnings": "memory/learnings/learnings-index.md",
    "memory/session-summaries": "memory/session-summaries/session-summaries-index.md",
}

IGNORED_ROOT_FILENAMES = {
    ".DS_Store",
}

NON_GOVERNED_ROOT_SUFFIXES = {
    ".pdf",
    ".docx",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_root_file_issues() -> list[str]:
    issues: list[str] = []
    for path in sorted(ROOT.iterdir()):
        if not path.is_file():
            continue
        name = path.name
        if name in ALLOWED_ROOT_FILES or name in IGNORED_ROOT_FILENAMES:
            continue
        if path.suffix.lower() in NON_GOVERNED_ROOT_SUFFIXES or path.suffix.lower() == ".md":
            issues.append(
                f"root-level governed file should move under a mapped folder: {name}"
            )
    return issues


def find_map_link_issues(mapping: dict[str, str]) -> list[str]:
    issues: list[str] = []
    for folder, map_rel in mapping.items():
        map_path = ROOT / map_rel
        base = ROOT / folder
        if not map_path.exists() or not base.exists():
            issues.append(f"missing map coverage: {folder} -> {map_rel}")
            continue
        text = read_text(map_path)
        map_name = Path(map_rel).name
        for file_path in sorted(base.glob("*.md")):
            if file_path.name == map_name:
                continue
            if file_path.name not in text:
                issues.append(f"unlinked file in {folder}: {file_path.name} not referenced by {map_rel}")
    return issues


def find_front_matter_backlog() -> list[str]:
    issues: list[str] = []
    scan_roots = [
        "knowledge",
        "memory",
        "projects",
        "core",
        "templates",
    ]
    skip_parts = {"documents/raw-chunks"}
    skip_names = {"README.md"}
    for scan_root in scan_roots:
        base = ROOT / scan_root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            rel = path.relative_to(ROOT).as_posix()
            if any(part in rel for part in skip_parts):
                continue
            if path.name in skip_names:
                continue
            with path.open("r", encoding="utf-8") as handle:
                first = handle.readline().strip()
            if first != "---":
                issues.append(rel)
    return issues


def main() -> int:
    issues: list[str] = []
    issues.extend(find_root_file_issues())
    issues.extend(find_map_link_issues(TOP_LEVEL_MAPS))
    issues.extend(find_map_link_issues(NESTED_MAPS))

    if issues:
        print("Tenet repo health check failed.")
        print("")
        for issue in issues:
            print(f"- {issue}")
        return 1

    front_matter_backlog = find_front_matter_backlog()
    print("Tenet repo health check passed.")
    if front_matter_backlog:
        print("")
        print(
            f"Front matter backlog still exists in {len(front_matter_backlog)} files "
            "(reported as informational only)."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
