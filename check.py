#!/usr/bin/env python3
"""只读核对:对正在运行的排程进程做断言,任何不一致非零退出,绝不回写基准。"""
import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
EXPECTED = ROOT / "data" / "expected.json"
TZDB_VERSION_FILE = ROOT / "data" / "tzdb.version"


def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            if resp.status != 200:
                raise RuntimeError(f"{url} status={resp.status}")
            return json.loads(resp.read().decode())
    except Exception as exc:
        raise RuntimeError(f"fetch {url} failed: {exc}") from exc


def main():
    port = os.environ.get("PORT", "8763")
    base = os.environ.get("CHECK_BASE", f"http://127.0.0.1:{port}")
    golden = json.loads(EXPECTED.read_text())
    expected_tzdb = TZDB_VERSION_FILE.read_text().strip()

    failures = []

    try:
        health = fetch(base + "/health")
    except RuntimeError as exc:
        print("FAIL", exc, file=sys.stderr)
        return 1
    if health.get("ok") is not True:
        failures.append(f"health ok={health.get('ok')!r}")
    if health.get("zone") != golden["zone"]:
        failures.append(f"health zone={health.get('zone')!r} expected={golden['zone']!r}")
    if health.get("tzdb") != expected_tzdb:
        failures.append(f"health tzdb={health.get('tzdb')!r} expected={expected_tzdb!r}")

    try:
        schedule = fetch(base + "/schedule")
    except RuntimeError as exc:
        print("FAIL", exc, file=sys.stderr)
        return 1
    if schedule.get("zone") != golden["zone"]:
        failures.append(f"schedule zone={schedule.get('zone')!r} expected={golden['zone']!r}")

    actual_rows = schedule.get("rows", [])
    golden_rows = golden["rows"]
    if len(actual_rows) != len(golden_rows):
        failures.append(f"rows count actual={len(actual_rows)} expected={len(golden_rows)}")
    else:
        tz = ZoneInfo(golden["zone"])
        for actual, want in zip(actual_rows, golden_rows):
            if actual.get("name") != want["name"]:
                failures.append(f"name actual={actual.get('name')!r} expected={want['name']!r}")
            if actual.get("at") != want["at"]:
                failures.append(f"at actual={actual.get('at')!r} expected={want['at']!r}")
                continue
            instant = datetime.fromisoformat(want["at"]).replace(tzinfo=tz)
            offset = int(instant.utcoffset().total_seconds())
            if offset != want["offset"]:
                failures.append(
                    f"{want['name']} offset actual={offset} expected={want['offset']} (切换点漂移)"
                )

    if failures:
        for item in failures:
            print("FAIL", item, file=sys.stderr)
        return 1

    print(f"ok {base} zone={golden['zone']} tzdb={expected_tzdb} rows={len(golden_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
