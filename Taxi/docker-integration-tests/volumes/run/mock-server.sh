#!/usr/bin/env bash
set -e

touch /taxi/logs/application-taxi-mock-server.log
chmod 666 /taxi/logs/application-taxi-mock-server.log

ln -sf /taxi/mock/mock-server.nginx /etc/nginx/sites-available/mock-server

/taxi/tools/run.py \
    --https-hosts \
        secured-openapi.business.tinkoff.ru \
        b2b.taxi.yandex.net \
        saturn.mlp.yandex.net \
        stable.leasing-cabinet.carsharing.yandex.net \
        tvm-api.yandex.net \
        checkprovider.edadeal.yandex.net \
    --nginx mock-server \
    --run /taxi/mock/server.py
