#!/usr/bin/env python3
import json
import os
import subprocess
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
ZONE_FILE = Path("/usr/share/zoneinfo/Asia/Shanghai")
EXPECTED_ZONE = "Asia/Shanghai"
EXPECTED_TZDATA_VERSION = os.environ.get("TZDATA_VERSION", "")


def installed_tzdata_version():
    try:
        out = subprocess.run(
            ["dpkg-query", "-W", "-f=${Version}", "tzdata"],
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def verify_zone_data():
    if not ZONE_FILE.is_file() or ZONE_FILE.stat().st_size == 0:
        raise RuntimeError(f"zone data missing: {ZONE_FILE}")
    if EXPECTED_TZDATA_VERSION:
        version = installed_tzdata_version()
        if version != EXPECTED_TZDATA_VERSION:
            raise RuntimeError(
                f"tzdata version mismatch: loaded={version!r} "
                f"expected={EXPECTED_TZDATA_VERSION!r}"
            )
    try:
        zone = ZoneInfo(EXPECTED_ZONE)
    except ZoneInfoNotFoundError as exc:
        raise RuntimeError(f"zone unavailable: {EXPECTED_ZONE}: {exc}") from exc
    if zone.key != EXPECTED_ZONE:
        raise RuntimeError(f"zone name mismatch: loaded={zone.key!r}")
    return zone


ZONE = verify_zone_data()


def zone_name():
    return ZONE.key


def schedule_rows():
    rows = [{"name": "上海", "at": "2026-03-08T01:30:00"}]
    # 切换点用钉死的区域数据解析,数据版本漂了这里就会漂/失败。
    for row in rows:
        datetime.fromisoformat(row["at"]).replace(tzinfo=ZONE)
    return rows


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
            body = {
                "ok": True,
                "zone": zone_name(),
                "tzdata": installed_tzdata_version(),
            }
            self._send(200, json.dumps(body), "application/json")
            return
        if path == "/schedule":
            body = {"ok": True, "zone": zone_name(), "rows": schedule_rows()}
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
