#!/usr/bin/env bash
set -e

export ASPNETCORE_URLS=http://localhost:7002
export ASPNETCORE_ENVIRONMENT=integration.testing

/taxi/tools/run.py \
    --https-hosts taximeter-xservice.taxi.yandex.net \
    --nginx yandex-taximeter-xservice \
    --stdout-to-log \
    --wait \
        mongo.taxi.yandex:27017 \
        redis.taxi.yandex:6379 \
        http://configs.taxi.yandex.net/ping \
    --run /opt/dotnet/dotnet Yandex.Taximeter.XService.dll
