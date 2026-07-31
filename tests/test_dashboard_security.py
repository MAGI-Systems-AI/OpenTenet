"""Tests for the dashboard write-path controls (T5): Host allowlist,
per-run write token, and no wildcard CORS."""

import pathlib
import sys

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
