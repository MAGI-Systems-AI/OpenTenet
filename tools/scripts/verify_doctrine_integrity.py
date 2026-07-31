#!/usr/bin/env python3
"""verify_doctrine_integrity.py — detect silent tampering of the session-start
doctrine (Attestor finding T2: persistent memory/doctrine poisoning).

Every AI CLI reads a fixed set of doctrine files at session start. If one of
them changes without review, a poisoned instruction re-fires every session.
This script maintains a checksum manifest of those files:

    tools/scripts/verify_doctrine_integrity.py --update   # re-baseline after a reviewed change
    tools/scripts/verify_doctrine_integrity.py            # verify; exit 1 on drift

CI runs the verify form on every push/PR, so any change to core doctrine that
is not accompanied by a reviewed manifest update fails the build and forces a
human to look at it. Stdlib only.
"""

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "memory" / ".doctrine-manifest.sha256"

# Extra doctrine files outside core/ that are loaded as *rules* at session start.
# Deliberately excludes operational, frequently-edited files (current-focus,
# identity, work notes) — those are meant to change; the target here is the
# stable rule set an attacker would poison.
_EXTRA = (
    "CLAUDE.md",
    "GEMINI.md",
    ".cursorrules",
    "memory/session-context-local.md",
)


def tracked_files() -> list[Path]:
    files = sorted((ROOT / "core").glob("*.md"))
    for rel in _EXTRA:
        p = ROOT / rel
        if p.exists():
            files.append(p)
    return files


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _build() -> str:
    return "".join(
        f"{_sha256(f)}  {f.relative_to(ROOT).as_posix()}\n" for f in tracked_files()
    )


def cmd_update() -> int:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(_build(), encoding="utf-8")
    print(f"doctrine manifest updated: {MANIFEST.relative_to(ROOT)} "
          f"({len(tracked_files())} files)")
    return 0


def cmd_verify() -> int:
    if not MANIFEST.exists():
        print("doctrine manifest missing — run with --update to create it",
              file=sys.stderr)
        return 1
    expected: dict[str, str] = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, rel = line.split("  ", 1)
        expected[rel] = digest
    current = {f.relative_to(ROOT).as_posix(): _sha256(f) for f in tracked_files()}

    drift: list[str] = []
    for rel, dig in expected.items():
        if rel not in current:
            drift.append(f"MISSING   {rel}")
        elif current[rel] != dig:
            drift.append(f"CHANGED   {rel}")
    for rel in current:
        if rel not in expected:
            drift.append(f"UNTRACKED {rel}")

    if drift:
        print("doctrine integrity FAIL — unreviewed changes to session-start doctrine:",
              file=sys.stderr)
        for d in sorted(drift):
            print("  " + d, file=sys.stderr)
        print("\nIf these changes are intended, re-baseline after review:\n"
              "  tools/scripts/verify_doctrine_integrity.py --update", file=sys.stderr)
        return 1
    print(f"doctrine integrity OK — {len(expected)} files match the manifest")
    return 0


def main(argv: list[str]) -> int:
    if "--update" in argv:
        return cmd_update()
    return cmd_verify()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
