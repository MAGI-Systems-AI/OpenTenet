"""Tests for bin/tenet-lane (team layer: roster + operational lanes).

Loads the CLI as a module and runs it against temp workspaces so the solo
default, ownership lookup, and every check failure are exercised without
touching the real repo."""

import importlib.machinery
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
_LOADER = importlib.machinery.SourceFileLoader("tenet_lane", str(ROOT / "bin" / "tenet-lane"))
_SPEC = importlib.util.spec_from_loader("tenet_lane", _LOADER)
tl = importlib.util.module_from_spec(_SPEC)
_LOADER.exec_module(tl)


def _workspace(tmp_path):
    (tmp_path / "LAUNCHER.md").write_text("anchor\n", encoding="utf-8")
    (tmp_path / "core").mkdir()
    (tmp_path / "team" / "members").mkdir(parents=True)
    (tmp_path / "team" / "lanes").mkdir(parents=True)
    (tmp_path / "team" / "lanes" / "lanes-map.md").write_text("---\n---\n# Lanes\n", encoding="utf-8")
    return tmp_path


def _member(root, slug, status="active"):
    (root / "team" / "members" / f"{slug}.md").write_text(
        f"---\ntitle: Member\nowner: {slug}\nmember: {slug}\nmember_status: {status}\nrole: maintainer\n---\n",
        encoding="utf-8",
    )


def _lane(root, slug, owner, scope, status="active", backup="none", listed=True):
    scope_yaml = "".join(f"  - {s}\n" for s in scope)
    (root / "team" / "lanes" / f"{slug}.md").write_text(
        f"---\ntitle: Lane\nowner: {owner}\nlane: {slug}\nbackup: {backup}\n"
        f"lane_status: {status}\nscope:\n{scope_yaml}---\n# Lane\n",
        encoding="utf-8",
    )
    if listed:
        m = root / "team" / "lanes" / "lanes-map.md"
        m.write_text(m.read_text(encoding="utf-8") + f"| [{slug}]({slug}.md) |\n", encoding="utf-8")


def test_solo_workspace_without_team_dir_passes(tmp_path, capsys):
    (tmp_path / "LAUNCHER.md").write_text("anchor\n", encoding="utf-8")
    (tmp_path / "core").mkdir()
    assert tl.main(["--workspace", str(tmp_path), "check"]) == 0
    assert "solo mode" in capsys.readouterr().out


def test_real_repo_check_passes():
    assert tl.main(["--workspace", str(ROOT), "check"]) == 0


def test_frontmatter_parser_reads_scalars_and_lists():
    fm = tl.parse_frontmatter("---\nlane: api\nscope:\n  - projects/api/\n  - 'tools/*.py'\n---\nbody\n")
    assert fm["lane"] == "api"
    assert fm["scope"] == ["projects/api/", "tools/*.py"]


def test_valid_team_passes(tmp_path):
    root = _workspace(tmp_path)
    _member(root, "ana")
    _member(root, "ben")
    _lane(root, "api", "ana", ["projects/api/"], backup="ben")
    _lane(root, "docs", "ben", ["docs/", "README.md"])
    assert tl.check(root) == []


def test_whose_reports_owner(tmp_path, capsys):
    root = _workspace(tmp_path)
    _member(root, "ana")
    _lane(root, "api", "ana", ["projects/api/"])
    tl.main(["--workspace", str(root), "whose", "projects/api/server.py", "README.md"])
    out = capsys.readouterr().out
    assert "projects/api/server.py: lane api — owner ana (active)" in out
    assert "README.md: unowned" in out


def test_whose_paused_lane_does_not_hold(tmp_path, capsys):
    root = _workspace(tmp_path)
    _member(root, "ana")
    _lane(root, "api", "ana", ["projects/api/"], status="paused")
    tl.main(["--workspace", str(root), "whose", "projects/api/x.py"])
    assert "not held" in capsys.readouterr().out


def test_overlapping_active_scopes_fail(tmp_path):
    root = _workspace(tmp_path)
    _member(root, "ana")
    _member(root, "ben")
    _lane(root, "api", "ana", ["projects/"])
    _lane(root, "web", "ben", ["projects/web/"])
    assert any("scope overlap" in p for p in tl.check(root))


def test_broad_glob_overlapping_directory_fails(tmp_path):
    root = _workspace(tmp_path)
    _member(root, "ana")
    _member(root, "ben")
    _lane(root, "api", "ana", ["projects/*"])
    _lane(root, "web", "ben", ["projects/web/"])
    assert any("scope overlap" in p for p in tl.check(root))


def test_overlap_with_closed_lane_is_allowed(tmp_path):
    root = _workspace(tmp_path)
    _member(root, "ana")
    _member(root, "ben")
    _lane(root, "old", "ana", ["projects/api/"], status="closed")
    _lane(root, "api", "ben", ["projects/api/"])
    assert tl.check(root) == []


def test_unknown_owner_fails(tmp_path):
    root = _workspace(tmp_path)
    _member(root, "ana")
    _lane(root, "api", "zed", ["projects/api/"])
    assert any("owner 'zed' is not a member" in p for p in tl.check(root))


def test_alumni_owner_of_active_lane_fails(tmp_path):
    root = _workspace(tmp_path)
    _member(root, "ana", status="alumni")
    _lane(root, "api", "ana", ["projects/api/"])
    assert any("alumni" in p for p in tl.check(root))


def test_bad_status_fails(tmp_path):
    root = _workspace(tmp_path)
    _member(root, "ana")
    _lane(root, "api", "ana", ["projects/api/"], status="done")
    assert any("lane_status 'done'" in p for p in tl.check(root))


def test_empty_scope_fails(tmp_path):
    root = _workspace(tmp_path)
    _member(root, "ana")
    _lane(root, "api", "ana", [])
    assert any("scope is empty" in p for p in tl.check(root))


def test_lane_missing_from_map_fails(tmp_path):
    root = _workspace(tmp_path)
    _member(root, "ana")
    _lane(root, "api", "ana", ["projects/api/"], listed=False)
    assert any("not listed in team/lanes/lanes-map.md" in p for p in tl.check(root))


def test_slug_mismatch_fails(tmp_path):
    root = _workspace(tmp_path)
    _member(root, "ana")
    _lane(root, "api", "ana", ["projects/api/"])
    p = root / "team" / "lanes" / "api.md"
    p.write_text(p.read_text(encoding="utf-8").replace("lane: api", "lane: web"), encoding="utf-8")
    assert any("expected 'api'" in p for p in tl.check(root))
