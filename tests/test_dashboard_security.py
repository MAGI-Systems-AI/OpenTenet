"""Tests for the dashboard write-path controls (T5): Host allowlist,
per-run write token, and no wildcard CORS."""

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dashboard"))

import server  # noqa: E402


def _handler(headers: dict):
    """A Handler instance without running BaseHTTPRequestHandler.__init__
    (which would need a live socket). The security helpers only read
    self.headers."""
    h = server.Handler.__new__(server.Handler)
    h.headers = headers
    return h


def test_host_ok_accepts_loopback():
    assert _handler({"Host": "localhost:3131"})._host_ok() is True
    assert _handler({"Host": "127.0.0.1:3131"})._host_ok() is True
    assert _handler({"Host": "127.0.0.1"})._host_ok() is True


def test_host_ok_rejects_foreign_host():
    # DNS-rebinding defense: a foreign Host header is refused.
    assert _handler({"Host": "evil.example.com"})._host_ok() is False
    assert _handler({"Host": "attacker.test:3131"})._host_ok() is False
    assert _handler({})._host_ok() is False


def test_token_required_and_constant_time():
    assert _handler({"X-Tenet-Token": server.WRITE_TOKEN})._token_ok() is True
    assert _handler({"X-Tenet-Token": "wrong"})._token_ok() is False
    assert _handler({})._token_ok() is False


def test_token_is_unguessable():
    # secrets.token_urlsafe(24) → ~32 chars of URL-safe entropy
    assert len(server.WRITE_TOKEN) >= 24


def test_no_wildcard_cors_in_source():
    src = (ROOT / "dashboard" / "server.py").read_text(encoding="utf-8")
    assert "Access-Control-Allow-Origin" not in src


# --- POST body validation, audit fail-closed, rebuild timeout ---------------

import io  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402


def _post(path: str, body: bytes, length=None, monkeypatch=None):
    """Drive do_POST without a socket; return (status, json_body)."""
    headers = {"Host": "127.0.0.1:3131", "X-Tenet-Token": server.WRITE_TOKEN,
               "Content-Length": str(len(body) if length is None else length)}
    h = _handler(headers)
    h.path = path
    h.rfile = io.BytesIO(body)
    sent = {}

    def send_json(data, status=200):
        sent["status"], sent["body"] = status, data

    h.send_json = send_json
    h.do_POST()
    return sent["status"], sent["body"]


@pytest.fixture
def tmp_root(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "ROOT", tmp_path)
    return tmp_path


def test_post_rejects_oversized_body(tmp_root):
    status, _ = _post("/api/focus", b"{}", length=server.MAX_BODY + 1)
    assert status == 413


@pytest.mark.parametrize("length", ["-1", "abc"])
def test_post_rejects_bad_content_length(tmp_root, length):
    status, _ = _post("/api/focus", b"{}", length=length)
    assert status == 400


@pytest.mark.parametrize("body", [b"not json", b"[]", b'{"content": 5}', b"{}"])
def test_post_rejects_bad_schema(tmp_root, body):
    status, _ = _post("/api/focus", body)
    assert status == 400
    assert not (tmp_root / "memory" / "current-focus.md").exists()


def test_post_valid_write_is_audited(tmp_root):
    status, data = _post("/api/focus", json.dumps({"content": "hello"}).encode())
    assert (status, data) == (200, {"ok": True})
    assert (tmp_root / "memory" / "current-focus.md").read_text() == "hello"
    log = (tmp_root / "memory" / "audit" / "dashboard-log.jsonl").read_text()
    assert '"target": "memory/current-focus.md"' in log


def test_write_refused_when_audit_fails(tmp_root, monkeypatch):
    monkeypatch.setattr(server, "audit", lambda *a, **k: False)
    status, _ = _post("/api/identity", json.dumps({"content": "x"}).encode())
    assert status == 500
    assert not (tmp_root / "memory" / "identity.md").exists()


def test_rebuild_timeout_returns_504(tmp_root, monkeypatch):
    script = tmp_root / "tools" / "scripts" / "build_session_context.sh"
    script.parent.mkdir(parents=True)
    script.write_text("true\n")

    def hang(*a, **k):
        assert k.get("timeout") == server.REBUILD_TIMEOUT
        raise subprocess.TimeoutExpired(a[0], k["timeout"])

    monkeypatch.setattr(server.subprocess, "run", hang)
    status, _ = _post("/api/rebuild", b"")
    assert status == 504
