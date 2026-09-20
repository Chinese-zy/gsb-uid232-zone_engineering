FROM docker.m.daocloud.io/library/python:3.12@sha256:4d1caded1f729ae443eb803f26ffde7b61e696aeaef62f099abb6dd6b14257c7
WORKDIR /app

ARG TZDATA_VERSION=2026c-0+deb13u1
ARG TZDB_VERSION=2026c

RUN set -eux; \
    apt-get update; \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "tzdata=${TZDATA_VERSION}"; \
    installed="$(dpkg-query -W -f='${Version}' tzdata)"; \
    [ "${installed}" = "${TZDATA_VERSION}" ]; \
    test -f /usr/share/zoneinfo/Asia/Shanghai; \
    python3 -c "from zoneinfo import ZoneInfo; ZoneInfo('Asia/Shanghai')"; \
    echo -n "${TZDB_VERSION}" > /etc/tzdb-version; \
    rm -rf /var/lib/apt/lists/*

COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
