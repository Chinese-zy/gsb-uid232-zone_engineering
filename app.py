#!/usr/bin/env python3
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
ZONE_FILE = Path("/usr/share/zoneinfo/Asia/Shanghai")


def zone_name():
    if ZONE_FILE.exists():
        return "Asia/Shanghai"
    return os.environ.get("TZ", "UTC")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, content_type):
        raw = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/health":
            self._send(200, json.dumps({"ok": True}), "application/json")
            return
        if path == "/schedule":
            body = {"ok": True, "zone": zone_name(), "rows": [{"name": "上海", "at": "2026-03-08T01:30:00"}]}
            self._send(200, json.dumps(body, ensure_ascii=False), "application/json")
            return
        if path == "/":
            path = "/index.html"
        file_path = (WEB / path.lstrip("/")).resolve()
        if not str(file_path).startswith(str(WEB.resolve())) or not file_path.is_file():
            self._send(404, "missing", "text/plain; charset=utf-8")
            return
        kind = "text/html; charset=utf-8" if file_path.suffix == ".html" else "text/javascript; charset=utf-8"
        self._send(200, file_path.read_bytes(), kind)

    def log_message(self, fmt, *args):
        return


def main():
    port = int(os.environ.get("PORT", "8763"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
