#!/usr/bin/env bash

ln -sf /etc/nginx/sites-production/* /etc/nginx/sites-available

/taxi/tools/run.py \
    --https-hosts \
        taximeter.yandex.rostaxi.org \
        dev-utils.taxi.yandex.net \
        taximeter-proxy.yandex.nonexistent \
        chat.yandex.rostaxi.org \
        gps.yandex.rostaxi.org \
        app.rostaxi.org \
    --nginx \
        taximeter.yandex.rostaxi.org.conf \
        chat.yandex.rostaxi.org.conf \
        gps.yandex.rostaxi.org.conf \
        app.rostaxi.org.conf \
     --wait \
        taximeter-core.taxi.yandex.net:80 \
        taximeter-api.taxi.yandex.net:80 \
    --run sleep infinity
