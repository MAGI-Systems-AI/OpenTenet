#!/usr/bin/env python3
"""Check shared markdown files for missing YAML front matter."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


DEFAULT_TARGETS = [
    "knowledge",
    "memory",
    "projects",
    "team",
    "core",
    "templates",
]

EXCLUDED_PATH_PARTS = {
    "documents/raw-chunks",
}

EXCLUDED_FILENAMES = {
    "README.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Tenet markdown files for YAML front matter.")
    parser.add_argument(
        "paths",
        nargs="*",
        default=DEFAULT_TARGETS,
        help="Repo-relative paths to scan. Defaults to shared durable folders.",
    )
    return parser.parse_args()


def has_front_matter(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8") as handle:
            first = handle.readline().strip()
        return first == "---"
    except Exception:
        return False


def should_skip(path: Path) -> bool:
    as_posix = path.as_posix()
    if any(part in as_posix for part in EXCLUDED_PATH_PARTS):
        return True
    if path.name in EXCLUDED_FILENAMES:
        return True
    return False


def iter_markdown_files(root: Path, targets: list[str]) -> list[Path]:
    files: list[Path] = []
    for target in targets:
        base = (root / target).resolve()
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            if should_skip(path.relative_to(root)):
                continue
            files.append(path)
    return files


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[2]
    files = iter_markdown_files(root, args.paths)
    missing = [path.relative_to(root) for path in files if not has_front_matter(path)]

    if not missing:
        print("All checked markdown files have front matter.")
        return 0

    print("Files missing front matter:")
    for path in missing:
        print(path.as_posix())
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
