#!/usr/bin/env python3
"""Tenet local dashboard — tiny HTTP server.

Usage:
    python3 dashboard/server.py          # port 3131
    python3 dashboard/server.py 8080     # custom port
"""

import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

DASH_DIR = Path(__file__).parent
ROOT = DASH_DIR.parent


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, path: Path):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
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
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)

        p = self.path.split("?")[0]
        if p == "/api/focus":
            data = json.loads(raw)
            write_file(ROOT / "memory" / "current-focus.md", data["content"])
            self.send_json({"ok": True})

        elif p == "/api/identity":
            data = json.loads(raw)
            write_file(ROOT / "memory" / "identity.md", data["content"])
            self.send_json({"ok": True})

        elif p == "/api/rebuild":
            script = ROOT / "tools" / "scripts" / "build_session_context.sh"
            if not script.exists():
                self.send_json({"ok": False, "error": "build script not found"})
                return
            result = subprocess.run(
                ["bash", str(script)],
                capture_output=True,
                text=True,
                cwd=str(ROOT),
            )
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
    print("  Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
