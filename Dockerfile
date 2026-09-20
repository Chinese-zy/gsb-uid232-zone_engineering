FROM docker.m.daocloud.io/library/python:3.12.14@sha256:cd7c412d000912f29075a1b8803e43cb2f38bb67f104019df526df5ceaf30569

# 基础层即钉死镜像摘要,其自带 tzdata 2026b-0+deb13u1;
# 在此再显式钉版并 hold,防止后续层升级到隔夜仓库里的新版本。
ARG TZDATA_VERSION=2026b-0+deb13u1
ENV TZDATA_VERSION=${TZDATA_VERSION}
ENV TZ=Asia/Shanghai
RUN apt-mark hold tzdata \
    && test "$(dpkg-query -W -f='${Version}' tzdata)" = "${TZDATA_VERSION}" \
    && test -s /usr/share/zoneinfo/Asia/Shanghai
WORKDIR /app
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
