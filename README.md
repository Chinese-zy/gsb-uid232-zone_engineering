docker compose up --build

页面从 http://127.0.0.1:8764 进。对外入口是 / 、/schedule 、/health ，不要换。

本机另开一个口看页面：python app.py ，它听 8763。
核对容器里那个进程用 python check.py （默认打 8764，非零退出即不通过）。
基础镜像按摘要钉死，tzdata 钉在 2026b-0+deb13u1 并随基础层打入；
启动即核对加载的 tzdata 版本、Asia/Shanghai 区域文件与区域名，对不上直接非零退出。
探活不只看返回成功，还校验正文里的 zone。
时刻样例在 data/batch.json ；期望基准单独放 data/expect.json ，check 只读不写。
