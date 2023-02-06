#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
DRIVER_CATEGORIES_API_PATH=$USERVICES_PATH/build-integration/services/driver-categories-api
DRIVER_CATEGORIES_API_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/driver-categories-api
DRIVER_CATEGORIES_API_DEB_PATH=$USERVICES_PATH/services/driver-categories-api/debian

DRIVER_CATEGORIES_API_BINARY_PATH=
if [ -f "$DRIVER_CATEGORIES_API_PATH/yandex-taxi-driver-categories-api" ]; then
  DRIVER_CATEGORIES_API_BINARY_PATH="$DRIVER_CATEGORIES_API_PATH/yandex-taxi-driver-categories-api"
elif [ -f "$DRIVER_CATEGORIES_API_ARCADIA_PATH/yandex-taxi-driver-categories-api" ]; then
  DRIVER_CATEGORIES_API_BINARY_PATH="$DRIVER_CATEGORIES_API_ARCADIA_PATH/yandex-taxi-driver-categories-api"
fi

if [ -f "$DRIVER_CATEGORIES_API_BINARY_PATH" ]; then
    echo "driver-categories-api update package"
    mkdir -p /etc/yandex/taxi/driver-categories-api/
    mkdir -p /var/cache/yandex/taxi-driver-categories-api/
    rm -rf /etc/yandex/taxi/driver-categories-api/*
    ln -s $DRIVER_CATEGORIES_API_PATH/configs/* /etc/yandex/taxi/driver-categories-api/
    cp $DRIVER_CATEGORIES_API_PATH/config.yaml /etc/yandex/taxi/driver-categories-api/
    ln -s $DRIVER_CATEGORIES_API_PATH/taxi_config_fallback.json /etc/yandex/taxi/driver-categories-api/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/driver-categories-api/
    ln -s config_vars.production.yaml /etc/yandex/taxi/driver-categories-api/config_vars.yaml

    ln -sf $DRIVER_CATEGORIES_API_DEB_PATH/yandex-taxi-driver-categories-api.nginx /etc/nginx/sites-available/yandex-taxi-driver-categories-api
    ln -sf $DRIVER_CATEGORIES_API_DEB_PATH/yandex-taxi-driver-categories-api.upstream_list /etc/nginx/conf.d/

    ln -sf $DRIVER_CATEGORIES_API_PATH/taxi-driver-categories-api-stats.py /usr/bin/

    echo "using binary: $DRIVER_CATEGORIES_API_BINARY_PATH"
    ln -sf $DRIVER_CATEGORIES_API_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-driver-categories-api/
mkdir -p /var/log/yandex/taxi-driver-categories-api/
ln -sf /taxi/logs/application-taxi-driver-categories-api.log /var/log/yandex/taxi-driver-categories-api/server.log

taxi-python3 /taxi/tools/run.py \
    --stdout-to-log \
    --nginx yandex-taxi-driver-categories-api \
    --fix-userver-client-timeout /etc/yandex/taxi/driver-categories-api/config.yaml \
    --syslog \
    --wait \
        mongo.taxi.yandex:27017 \
        redis.taxi.yandex:6379 \
        postgresql:driver-categories-api \
        http://configs.taxi.yandex.net/ping \
    --run /usr/bin/yandex-taxi-driver-categories-api \
        --config /etc/yandex/taxi/driver-categories-api/config.yaml \
        --init-log /taxi/logs/application-taxi-driver-categories-api-init.log
