#!/usr/bin/env bash
set -e

export ASPNETCORE_URLS=http://localhost:7001
export ASPNETCORE_ENVIRONMENT=integration.testing

/taxi/tools/run.py \
    --https-hosts \
        taximeter-core.taxi.yandex.net \
        taximeter-core.taxi.yandex.nonexistent \
    --nginx yandex-taximeter-core.nginx.production \
    --stdout-to-log \
    --wait \
        mongo.taxi.yandex:27017 \
        redis.taxi.yandex:6379 \
        http://configs.taxi.yandex.net/ping \
    --run /opt/dotnet/dotnet Yandex.Taximeter.Api.dll
