#!/usr/bin/env python3
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
SAMPLES = ROOT / "data" / "samples.json"
EXPECTED_TZDB_FILE = ROOT / "data" / "tzdb.version"
ZONE_NAME = "Asia/Shanghai"
ZONE_FILE = Path("/usr/share/zoneinfo") / ZONE_NAME
CONTAINER_TZDB_FILE = Path("/etc/tzdb-version")
SYSTEM_TZDB_FILE = Path("/usr/share/zoneinfo/+VERSION")


def expected_tzdb():
    return EXPECTED_TZDB_FILE.read_text().strip()


def loaded_tzdb_version():
    for candidate in (CONTAINER_TZDB_FILE, SYSTEM_TZDB_FILE):
        if candidate.is_file():
            return candidate.read_text().strip()
    return None


def zone_usable():
    if not ZONE_FILE.is_file():
        return False
    try:
        ZoneInfo(ZONE_NAME)
    except Exception:
        return False
    return True


def status():
    loaded = loaded_tzdb_version()
    expected = expected_tzdb()
    ok = zone_usable() and loaded == expected
    return {
        "ok": ok,
        "zone": ZONE_NAME if zone_usable() else None,
        "tzdb": loaded,
        "expected_tzdb": expected,
    }


def startup_check():
    if not ZONE_FILE.is_file():
        return f"zone data missing: {ZONE_FILE}"
    try:
        ZoneInfo(ZONE_NAME)
    except Exception as exc:
        return f"zone {ZONE_NAME} unusable: {exc}"
    loaded = loaded_tzdb_version()
    expected = expected_tzdb()
    if loaded != expected:
        return f"tzdb mismatch: loaded={loaded!r} expected={expected!r}"
    return None


def schedule_body():
    doc = json.loads(SAMPLES.read_text())
    return {"ok": True, "zone": ZONE_NAME, "rows": doc["samples"]}


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
            state = status()
            self._send(
                200 if state["ok"] else 503,
                json.dumps(state),
                "application/json",
            )
            return
        if path == "/schedule":
            self._send(
                200,
                json.dumps(schedule_body(), ensure_ascii=False),
                "application/json",
            )
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
    problem = startup_check()
    if problem:
        print("startup check failed:", problem, file=sys.stderr)
        raise SystemExit(1)
    state = status()
    print(f"loaded zone={state['zone']} tzdb={state['tzdb']}", flush=True)
    port = int(os.environ.get("PORT", "8763"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
