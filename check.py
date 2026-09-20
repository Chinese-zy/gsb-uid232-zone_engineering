#!/usr/bin/env python3
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BATCH = ROOT / "data" / "batch.json"
EXPECT = ROOT / "data" / "expect.json"

# 默认打容器里那个进程(compose 映射到宿主的 8764),不是本机直接跑的 8763。
TARGET = "http://127.0.0.1:8764"


def get_json(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=2) as resp:
        if resp.status != 200:
            raise RuntimeError(f"{url} status {resp.status}")
        return json.loads(resp.read().decode())


def main():
    expect = json.loads(EXPECT.read_text())
    json.loads(BATCH.read_text())  # 只读取样例时刻,不再回写基准

    health = get_json(TARGET + "/health")
    if not health.get("ok"):
        print("health body not ok:", health)
        return 1
    if health.get("zone") != expect["zone"]:
        print(f"health zone mismatch: got={health.get('zone')!r} "
              f"expect={expect['zone']!r}")
        return 1
    if health.get("tzdata") != expect["tzdata"]:
        print(f"tzdata version mismatch: loaded={health.get('tzdata')!r} "
              f"expect={expect['tzdata']!r}")
        return 1

    schedule = get_json(TARGET + "/schedule")
    if schedule.get("zone") != expect["zone"]:
        print(f"schedule zone mismatch: got={schedule.get('zone')!r} "
              f"expect={expect['zone']!r}")
        return 1

    rows = schedule.get("rows", [])
    expected_rows = expect["rows"]
    if len(rows) != len(expected_rows):
        print(f"row count mismatch: got={len(rows)} expect={len(expected_rows)}")
        return 1
    for actual, wanted in zip(rows, expected_rows):
        if actual.get("name") != wanted["name"]:
            print(f"name mismatch: got={actual.get('name')!r} "
                  f"expect={wanted['name']!r}")
            return 1
        if actual.get("at") != wanted["at"]:
            print(f"switch point drift: {actual.get('name')} "
                  f"got={actual.get('at')!r} expect={wanted['at']!r}")
            return 1

    print("checked", TARGET, "zone", schedule.get("zone"),
          "tzdata", health.get("tzdata"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, urllib.error.URLError, ValueError, KeyError) as exc:
        print("check failed:", exc)
        raise SystemExit(1)
