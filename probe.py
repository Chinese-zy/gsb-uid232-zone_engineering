#!/usr/bin/env python3
"""容器内探活:不仅要请求成功,还要求正文里 zone 名与 tzdb 版本正确。"""
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_TZDB = (ROOT / "data" / "tzdb.version").read_text().strip()


def main():
    port = os.environ.get("PORT", "8080")
    url = f"http://127.0.0.1:{port}/health"
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            if resp.status != 200:
                return 1
            body = json.loads(resp.read().decode())
    except Exception:
        return 1
    if body.get("ok") is not True:
        return 1
    if body.get("zone") != "Asia/Shanghai":
        return 1
    if body.get("tzdb") != EXPECTED_TZDB:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
