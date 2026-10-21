"""Tests for the corporate-profile runtime guard (tools/guard.py, bin/tenet-guard).
Offline. Every scenario in policy/demo-cases.json is also asserted here so the
live demo and CI can never disagree."""

import io
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import guard  # noqa: E402

CASES = json.loads((ROOT / "policy" / "demo-cases.json").read_text())["cases"]


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("TENET_GUARD_LOG", str(tmp_path / "guard-log.jsonl"))
    monkeypatch.setenv("TENET_WORKSPACE", str(ROOT))
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    monkeypatch.delenv("TENET_GUARD_MODE", raising=False)
    return tmp_path


@pytest.fixture
def policy():
    return guard.load_policy()


def run(event):
    out = io.StringIO()
    guard.run_hook(event["hook"], stdin=io.StringIO(json.dumps(event)), stdout=out)
    return json.loads(out.getvalue()) if out.getvalue() else None


def verdict(out):
    if out is None:
        return "allow"
    if out.get("decision") == "block":
        return "block"
    hso = out["hookSpecificOutput"]
    if "additionalContext" in hso:
        return "flag"
    return {"deny": "block", "ask": "ask"}[hso["permissionDecision"]]


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_demo_case(case):
    assert verdict(run(case["event"])) == case["expect"]


# --- DLP validators ---------------------------------------------------------- #

def test_luhn_invalid_card_not_flagged(policy):
    assert not [h for h in guard.scan_text("order 4111 1111 1111 1112", policy) if h[0] == "PCI-PAN"]


def test_iban_checksum(policy):
    assert [h for h in guard.scan_text("pay GB82 WEST 1234 5698 7654 32", policy) if h[0] == "PII-IBAN"]
    assert not [h for h in guard.scan_text("pay GB00 WEST 1234 5698 7654 32", policy) if h[0] == "PII-IBAN"]


def test_invalid_ssn_area_not_flagged(policy):
    assert not guard.scan_text("ref 000-12-3456 and 666-12-3456", policy)


# --- audit log --------------------------------------------------------------- #

def test_audit_never_stores_raw_values(isolated):
    run({"hook": "prompt", "prompt": "SSN 123-45-6789 card 4111111111111111"})
    run({"hook": "pretool", "tool_name": "Bash", "tool_input": {"command": "echo AKIAIOSFODNN7EXAMPLE"}})
    log = (isolated / "guard-log.jsonl").read_text()
    for raw in ("123-45-6789", "4111111111111111", "AKIAIOSFODNN7EXAMPLE"):
        assert raw not in log
    assert "[PII-SSN …6789]" in log


def test_audit_chain_detects_tamper(isolated):
    for cmd in ("ls", "printenv", "git push origin x"):
        run({"hook": "pretool", "tool_name": "Bash", "tool_input": {"command": cmd}})
    path = isolated / "guard-log.jsonl"
    assert guard.verify_chain(path)[0]
    lines = path.read_text().splitlines()
    entry = json.loads(lines[1])
    entry["decision"] = "allow"  # an insider rewrites a block as an allow
    lines[1] = json.dumps(entry, sort_keys=True)
    path.write_text("\n".join(lines) + "\n")
    ok, n, msg = guard.verify_chain(path)
    assert not ok and n == 2


# --- modes + failure behaviour ---------------------------------------------- #

def test_audit_mode_allows_but_records(isolated, monkeypatch):
    pilot = json.loads((ROOT / "policy" / "corporate.json").read_text())
    pilot["allow_mode_override"] = True  # independent of how this workspace's policy is pinned
    (isolated / "pilot.json").write_text(json.dumps(pilot))
    monkeypatch.setenv("TENET_GUARD_POLICY", str(isolated / "pilot.json"))
    monkeypatch.setenv("TENET_GUARD_MODE", "audit")
    assert run({"hook": "pretool", "tool_name": "Read", "tool_input": {"file_path": ".env"}}) is None
    entry = json.loads((isolated / "guard-log.jsonl").read_text().splitlines()[-1])
    assert entry["would_block"] and entry["controls"] == ["PATH-PROTECTED"]


def test_pretool_fails_closed_on_bad_policy(monkeypatch):
    monkeypatch.setattr(guard, "POLICY_PATH", ROOT / "does-not-exist.json")
    out = run({"hook": "pretool", "tool_name": "Read", "tool_input": {"file_path": "README.md"}})
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_prompt_fails_closed_on_bad_policy(monkeypatch):
    monkeypatch.setattr(guard, "POLICY_PATH", ROOT / "does-not-exist.json")
    assert run({"hook": "prompt", "prompt": "hello"})["decision"] == "block"


def test_symlinked_home_still_protected(policy, tmp_path):
    link = tmp_path / "homelink"
    link.symlink_to(pathlib.Path.home())
    found = guard.evaluate_tool("Read", {"file_path": str(link / ".ssh" / "id_rsa")}, None, policy)
    assert [f for f in found if f["control"] == "PATH-PROTECTED"]


def test_cli_demo_exits_zero():
    env = dict(os.environ, NO_COLOR="1")
    r = subprocess.run([sys.executable, str(ROOT / "bin" / "tenet-guard"), "demo"],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr


def test_production_policy_ignores_mode_override(isolated, monkeypatch, policy):
    monkeypatch.setenv("TENET_GUARD_MODE", "audit")
    policy["allow_mode_override"] = False
    assert guard.mode(policy) == "enforce"
