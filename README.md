docker compose up --build

页面从 http://127.0.0.1:8764 进。对外入口是 / 、/schedule 、/health ，不要换。

本机另开一个口看页面：python app.py ，它听 8763。
核对用 python check.py 。
区域数据没打进镜像。缺了就按本机时区对外，探活只看返回成功。
时刻和期望都在 data/batch.json 。
