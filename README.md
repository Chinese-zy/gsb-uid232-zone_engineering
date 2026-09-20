## 运行

```
docker compose up --build
```

页面从 http://127.0.0.1:8764 进。对外入口仍是 `/`、`/schedule`、`/health`,路径和响应结构不动。

## 版本钉死

- 基础镜像按 digest 钉在 `Dockerfile`(`python:3.12`),tzdata 包按完整版本(`2026c-0+deb13u1`)安装。
- 构建期断言:dpkg 版本、`/usr/share/zoneinfo/+VERSION`(tzdb=`2026c`)、`Asia/Shanghai` 文件必须全部在,否则构建失败;版本号另写入镜像内 `/etc/tzdb-version`。
- `data/tzdb.version` 是仓库里钉的 tzdb 基准,与镜像层是同一份。

## 启动核对

- `app.py` 启动先查 `Asia/Shanghai` 数据文件能不能加载,再比对实际加载的 tzdb 版本与 `data/tzdb.version`。
- 对不上或缺区域数据:打印原因并以非零码退出,绝不静默回退到本机时区。
- `/health` 正文返回 `{ok, zone, tzdb, expected_tzdb}`;不对时 HTTP 503。
- 容器探活走 `probe.py`,除了请求成功还校验正文里的时区名和 tzdb 版本,错了探活失败。

## 核对

- 样例时刻在 `data/samples.json`,基准期望在 `data/expected.json`(含 zone 与每条时刻的 UTC offset,用于抓切换点漂移),tzdb 基准在 `data/tzdb.version`。三份都是只读输入。
- `check.py` 只读取与断言,任何不一致以非零码退出,不回写基准。
- 打容器里那个进程(不是宿主机另开的):

```
docker compose exec -e PORT=8080 web python check.py
```

- 本机直跑(读系统 zoneinfo,版本须与 `data/tzdb.version` 一致):

```
python app.py   # 听 8763
python check.py
```
