#!/usr/bin/env bash

mkdir -p /var/run/yandex/tariff-editor
chown www-data /var/run/yandex/tariff-editor

/taxi/tools/run.py \
    --nginx 90-taxi-tariff-editor.conf \
    --https-hosts \
        tariff-editor.taxi.yandex-team.ru \
        tariff-editor.yandex.nonexistent \
    --stdout-to-log \
    --run \
        sudo -E -u www-data /opt/nodejs/8/bin/node /usr/lib/yandex/tariff-editor/server/src
