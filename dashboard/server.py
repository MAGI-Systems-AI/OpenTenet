#!/usr/bin/env python3
"""Tenet local dashboard — tiny HTTP server.

Usage:
    python3 dashboard/server.py          # port 3131
    python3 dashboard/server.py 8080     # custom port

Security (Attestor finding T5 — the dashboard writes AI doctrine files):
    * Binds 127.0.0.1 only.
    * Host-header allowlist (localhost / 127.0.0.1) — defeats DNS-rebinding,
      where a malicious page resolves its own name to 127.0.0.1 to reach us.
    * No wildcard CORS. Cross-origin pages cannot read our responses.
    * Write endpoints (POST) require a per-run token. The token is minted at
      startup, injected into the served page, and required on every write, so a
      cross-origin/CSRF POST that doesn't know it is rejected.
    * Every write is appended to memory/audit/dashboard-log.jsonl (T6). The
      audit entry is written FIRST; if it cannot be written, the change is
      refused (fail closed).
    * Request bodies are capped (MAX_BODY) and schema-checked; a stuck
      context rebuild is killed after REBUILD_TIMEOUT seconds.
"""

import hmac
import json
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

DASH_DIR = Path(__file__).parent
ROOT = DASH_DIR.parent

# Per-run write token — unguessable, regenerated every start.
WRITE_TOKEN = secrets.token_urlsafe(24)
ALLOWED_HOSTNAMES = {"127.0.0.1", "localhost"}
MAX_BODY = 1024 * 1024  # 1 MiB — focus/identity files are a few KB
REBUILD_TIMEOUT = 120


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def audit(event: str, detail: dict) -> bool:
    """Append one JSON line for a state-changing dashboard action (T6).
    Returns False if the entry could not be written, so callers fail closed."""
    record = {
        "ts": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "event": event,
        **detail,
    }
    try:
        log = ROOT / "memory" / "audit" / "dashboard-log.jsonl"
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return True
    except OSError as e:
        print(f"  [audit] FAILED to write audit entry for {event}: {e}", file=sys.stderr)
        return False


def scan_skills() -> list:
    skills = []
    skills_dir = ROOT / "skills"
    if not skills_dir.exists():
        return skills
    for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        name, description = "", ""
        in_front = False
        for line in text.splitlines():
            if line.strip() == "---":
                in_front = not in_front
                continue
            if in_front:
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip()
                elif line.startswith("description:"):
                    description = line.split(":", 1)[1].strip()
        if name:
            skills.append({"name": name, "description": description})
    return skills


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Only log errors, not every request
        if args and str(args[1]) not in ("200", "204"):
            super().log_message(fmt, *args)

    # ----- security helpers -------------------------------------------------
    def _host_ok(self) -> bool:
        """Reject requests whose Host header isn't a loopback name (anti-rebind)."""
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0]
        return host in ALLOWED_HOSTNAMES

    def _token_ok(self) -> bool:
        """Constant-time check of the per-run write token on state changes."""
        supplied = self.headers.get("X-Tenet-Token", "")
        return hmac.compare_digest(supplied, WRITE_TOKEN)

    def _read_body(self):
        """Return (raw_bytes, None) or (None, (status, message))."""
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            return None, (400, "invalid Content-Length")
        if length < 0:
            return None, (400, "invalid Content-Length")
        if length > MAX_BODY:
            return None, (413, f"body exceeds {MAX_BODY} bytes")
        return self.rfile.read(length), None

    @staticmethod
    def _parse_content(raw: bytes):
        """Return (content_str, None) or (None, error message) for {"content": str}."""
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            return None, "malformed JSON"
        if not isinstance(data, dict) or not isinstance(data.get("content"), str):
            return None, "body must be an object with a string 'content'"
        return data["content"], None

    def _write_doc(self, rel: str, raw: bytes):
        content, err = self._parse_content(raw)
        if err:
            self._deny(400, err)
            return
        if not audit("write", {"target": rel, "bytes": len(raw)}):
            self._deny(500, "audit log unavailable; change refused")
            return
        write_file(ROOT / rel, content)
        self.send_json({"ok": True})

    def _deny(self, status: int, message: str):
        self.send_json({"ok": False, "error": message}, status=status)

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        # No CORS: this is a same-origin, single-user local tool.
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, path: Path):
        # Inject the per-run write token so the page's own POSTs can authenticate.
        html = path.read_text(encoding="utf-8")
        inject = f'<script>window.TENET_TOKEN={json.dumps(WRITE_TOKEN)};</script>'
        if "</head>" in html:
            html = html.replace("</head>", inject + "</head>", 1)
        else:
            html = inject + html
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        # No cross-origin support; answer preflights with no CORS grant.
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if not self._host_ok():
            self._deny(403, "forbidden host")
            return
        p = self.path.split("?")[0]
        if p in ("/", "/index.html"):
            self.send_html(DASH_DIR / "index.html")
        elif p == "/api/focus":
            self.send_json({"content": read_file(ROOT / "memory" / "current-focus.md")})
        elif p == "/api/identity":
            self.send_json({"content": read_file(ROOT / "memory" / "identity.md")})
        elif p == "/api/skills":
            self.send_json({"skills": scan_skills()})
        elif p == "/api/status":
            self.send_json({
                "root": str(ROOT),
                "context_built": (ROOT / "memory" / "session-context.md").exists(),
            })
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        # Every write path is gated on loopback Host + the per-run token.
        if not self._host_ok():
            self._deny(403, "forbidden host")
            return
        if not self._token_ok():
            self._deny(403, "missing or invalid write token")
            return

        raw, err = self._read_body()
        if err:
            self._deny(*err)
            return
        p = self.path.split("?")[0]

        if p == "/api/focus":
            self._write_doc("memory/current-focus.md", raw)

        elif p == "/api/identity":
            self._write_doc("memory/identity.md", raw)

        elif p == "/api/rebuild":
            script = ROOT / "tools" / "scripts" / "build_session_context.sh"
            if not script.exists():
                self.send_json({"ok": False, "error": "build script not found"})
                return
            if not audit("rebuild", {"script": "tools/scripts/build_session_context.sh"}):
                self._deny(500, "audit log unavailable; rebuild refused")
                return
            try:
                result = subprocess.run(
                    ["bash", str(script)],
                    capture_output=True,
                    text=True,
                    cwd=str(ROOT),
                    timeout=REBUILD_TIMEOUT,
                )
            except subprocess.TimeoutExpired:
                self._deny(504, f"rebuild timed out after {REBUILD_TIMEOUT}s")
                return
            self.send_json({
                "ok": result.returncode == 0,
                "stdout": result.stdout[-2000:],
                "stderr": result.stderr[-2000:],
            })

        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3131
    server = HTTPServer(("127.0.0.1", port), Handler)
    url = f"http://localhost:{port}"
    print(f"\n  Tenet Dashboard  →  {url}\n")
    print(f"  Write token (for direct API calls): {WRITE_TOKEN}")
    print("  The web page authenticates automatically. Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
