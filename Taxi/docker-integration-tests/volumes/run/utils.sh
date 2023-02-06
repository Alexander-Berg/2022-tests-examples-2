#!/usr/bin/env bash
set -e

if [ -f /taxi/backend/debian/changelog ]; then
    mkdir -p /etc/yandex/taxi-utils/
    rm -f /etc/yandex/taxi-utils/*
    ln -s /taxi/backend/debian/settings.*.py /etc/yandex/taxi-utils/
    ln -s /taxi/backend/debian/yandex-taxi-utils.settings.py /etc/yandex/taxi-utils/

    mkdir -p /usr/lib/yandex/taxi-utils/
    rm -rf /usr/lib/yandex/taxi-utils/*
    sed 's/# SERVERS #/    server  127.0.0.1:8580;/' \
        /taxi/backend/debian/yandex-taxi-utils.nginx > \
        /etc/nginx/sites-available/yandex-taxi-utils
    ln -s /taxi/backend/debian/stq_config.py /usr/lib/yandex/taxi-utils/
    ln -s /taxi/backend/taxi /usr/lib/yandex/taxi-utils/
    ln -s /etc/yandex/taxi-utils/settings.production.py \
        /usr/lib/yandex/taxi-utils/taxi_base_settings.py
    ln -s /etc/yandex/taxi-utils/yandex-taxi-utils.settings.py \
        /usr/lib/yandex/taxi-utils/taxi_settings.py
    ln -s /taxi/backend/taxi_stq /usr/lib/yandex/taxi-utils/
    ln -s /taxi/backend/debian/twistedconfig.py /usr/lib/yandex/taxi-utils/
    ln -s /taxi/backend/taxi-utils/* /usr/lib/yandex/taxi-utils/
fi

/taxi/tools/run.py \
    --https-hosts \
        dev-utils.taxi.yandex.net \
        dev-utils.taxi.dev.yandex.net \
        dev-utils.taxi.tst.yandex.net \
        dev-utils.taxi.yandex.net \
        dev-utils.taxi.yandex.nonexistent \
    --nginx yandex-taxi-utils \
    --stdout-to-log \
    --restart-service 9999 \
    --wait \
        mongo.taxi.yandex:27017 \
        http://configs.taxi.yandex.net/ping \
    --run twistd \
        -r epoll \
        -n \
        web \
        --resource-script=/usr/lib/yandex/taxi-utils/utils_server.rpy \
        -p tcp:8580
