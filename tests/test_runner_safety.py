"""Tests for the basic runner's file-tool confinement and tier handling."""

import importlib.machinery
import importlib.util
import os
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture
def tenet(tmp_path, monkeypatch):
    """Load bin/tenet with its workspace pointed at an empty tmp dir."""
    monkeypatch.setenv("TENET_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("TENET_BACKEND", "mock")
    loader = importlib.machinery.SourceFileLoader("tenet_runner", str(ROOT / "bin" / "tenet"))
    spec = importlib.util.spec_from_loader("tenet_runner", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def test_safe_path_allows_workspace_paths(tenet, tmp_path):
    root = os.path.realpath(tmp_path)
    assert tenet._safe_path("memory/work/x.md") == os.path.join(root, "memory", "work", "x.md")
    assert tenet._safe_path(os.path.join(root, "a.txt")) == os.path.join(root, "a.txt")


@pytest.mark.parametrize("path", ["../outside.txt", "a/../../outside.txt", "/etc/passwd"])
def test_safe_path_rejects_escape(tenet, path):
    assert tenet._safe_path(path) is None


def test_safe_path_rejects_symlink_out(tenet, tmp_path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    (tmp_path / "link").symlink_to(outside)
    assert tenet._safe_path("link/secret.txt") is None


def test_file_tools_refuse_outside_workspace(tenet, tmp_path):
    target = tmp_path.parent / f"{tmp_path.name}-escape.txt"
    assert "outside workspace" in tenet.tool_write_file({"path": str(target), "content": "x"})
    assert not target.exists()
    assert "outside workspace" in tenet.tool_read_file({"path": "../../etc/passwd"})


def test_quick_tier_runs_execute_only(tenet):
    note = tenet.TenetAgent().run("quick task", tier="quick")
    body = pathlib.Path(note).read_text(encoding="utf-8")
    assert "## EXECUTE" in body
    for phase in ("OBSERVE", "THINK", "PLAN", "VERIFY", "LEARN"):
        assert f"## {phase}" not in body


def test_standard_tier_runs_all_six_phases(tenet):
    note = tenet.TenetAgent().run("standard task", tier="standard")
    body = pathlib.Path(note).read_text(encoding="utf-8")
    for phase, _ in tenet.PHASES:
        assert f"## {phase}" in body
