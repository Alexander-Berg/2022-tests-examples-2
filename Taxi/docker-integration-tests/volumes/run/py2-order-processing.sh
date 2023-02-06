#!/usr/bin/env bash
set -e

REPO_DIR=/taxi/backend
PY2_ORDER_PROCESSING_DIR=$REPO_DIR/taxi-order-processing

if [ -d $PY2_ORDER_PROCESSING_DIR ]; then
    echo "py2-order-processing update package"

    mkdir -p /etc/yandex/taxi-order-processing
    mkdir -p /var/cache/yandex/taxi/configs
    mkdir -p /var/cache/yandex/taxi/py2-order-processing/files
    mkdir -p /var/log/yandex/taxi-order-processing
    mkdir -p /usr/lib/yandex/taxi-order-processing

    rm -rf /etc/yandex/taxi-order-processing/*
    rm -rf /usr/lib/yandex/taxi-order-processing/*

    ln -s $REPO_DIR/debian/twistedconfig.py /usr/lib/yandex/taxi-order-processing/
    ln -s $REPO_DIR/debian/settings.*.py /etc/yandex/taxi-order-processing/
    ln -s $REPO_DIR/debian/yandex-taxi-order-processing.settings.py \
        /etc/yandex/taxi-order-processing/

    ln -s /etc/yandex/taxi-order-processing/settings.production.py \
        /usr/lib/yandex/taxi-order-processing/taxi_base_settings.py
    ln -s /etc/yandex/taxi-order-processing/yandex-taxi-order-processing.settings.py \
        /usr/lib/yandex/taxi-order-processing/taxi_settings.py

    ln -s $REPO_DIR/taxi /usr/lib/yandex/taxi-order-processing/
    ln -s $REPO_DIR/taxi_stq /usr/lib/yandex/taxi-order-processing/
    ln -s $REPO_DIR/taxi-order-processing/* /usr/lib/yandex/taxi-order-processing/

    sed 's/# SERVERS #/    server  127.0.0.1:8580;/' \
        $REPO_DIR/debian/yandex-taxi-order-processing.nginx > \
        /etc/nginx/sites-available/yandex-taxi-order-processing
fi

/taxi/tools/run.py \
    --syslog \
    --wait \
      mongo.taxi.yandex:27017 \
      http://configs.taxi.yandex.net/ping \
    --nginx yandex-taxi-order-processing \
    --run twistd \
        -r epoll \
        -n \
        web \
        --resource-script=/usr/lib/yandex/taxi-order-processing/processing_server.rpy \
        -p tcp:8580
        -l /var/log/yandex/taxi-order-processing/twistd.web.8580.log
