#!/usr/bin/env bash
set -e

export DOTNET_CLI_TELEMETRY_OPTOUT=1
export ASPNETCORE_URLS=http://localhost:7001
export ASPNETCORE_ENVIRONMENT=integration.testing

/taxi/tools/run.py \
    --https-hosts \
        taximeter-admin.taxi.yandex-team.ru \
        taximeter-admin.taxi.tst.yandex-team.ru \
        taximeter-admin-unstable.taxi.tst.yandex-team.ru \
    --nginx yandex-taximeter-web-admin.nginx.production \
    --stdout-to-log \
    --wait \
        mongo.taxi.yandex:27017 \
        redis.taxi.yandex:6379 \
        http://configs.taxi.yandex.net/ping \
    --run /opt/dotnet/dotnet Yandex.Taximeter.Admin.dll
