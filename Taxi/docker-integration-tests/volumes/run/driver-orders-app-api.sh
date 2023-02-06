#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
DRIVER_ORDERS_APP_API_PATH=$USERVICES_PATH/build-integration/services/driver-orders-app-api
DRIVER_ORDERS_APP_API_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/driver-orders-app-api
DRIVER_ORDERS_APP_API_DEB_PATH=$USERVICES_PATH/services/driver-orders-app-api/debian

DRIVER_ORDERS_APP_API_BINARY_PATH=
if [ -f "$DRIVER_ORDERS_APP_API_PATH/yandex-taxi-driver-orders-app-api" ]; then
  DRIVER_ORDERS_APP_API_BINARY_PATH="$DRIVER_ORDERS_APP_API_PATH/yandex-taxi-driver-orders-app-api"
elif [ -f "$DRIVER_ORDERS_APP_API_ARCADIA_PATH/yandex-taxi-driver-orders-app-api" ]; then
  DRIVER_ORDERS_APP_API_BINARY_PATH="$DRIVER_ORDERS_APP_API_ARCADIA_PATH/yandex-taxi-driver-orders-app-api"
fi

if [ -f "$DRIVER_ORDERS_APP_API_BINARY_PATH" ]; then
    echo "driver-orders-app-api update package"
    mkdir -p /etc/yandex/taxi/driver-orders-app-api/
    mkdir -p /var/cache/yandex/taxi-driver-orders-app-api/
    rm -rf /etc/yandex/taxi/driver-orders-app-api/*
    ln -s $DRIVER_ORDERS_APP_API_PATH/configs/* /etc/yandex/taxi/driver-orders-app-api/
    cp $DRIVER_ORDERS_APP_API_PATH/config.yaml /etc/yandex/taxi/driver-orders-app-api/
    ln -s $DRIVER_ORDERS_APP_API_PATH/taxi_config_fallback.json /etc/yandex/taxi/driver-orders-app-api/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/driver-orders-app-api/
    ln -s config_vars.production.yaml /etc/yandex/taxi/driver-orders-app-api/config_vars.yaml

    ln -sf $DRIVER_ORDERS_APP_API_DEB_PATH/yandex-taxi-driver-orders-app-api.nginx /etc/nginx/sites-available/yandex-taxi-driver-orders-app-api
    ln -sf $DRIVER_ORDERS_APP_API_DEB_PATH/yandex-taxi-driver-orders-app-api.upstream_list /etc/nginx/conf.d/

    ln -sf $DRIVER_ORDERS_APP_API_PATH/taxi-driver-orders-app-api-stats.py /usr/bin/

    echo "using binary: $DRIVER_ORDERS_APP_API_BINARY_PATH"
    ln -sf $DRIVER_ORDERS_APP_API_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-driver-orders-app-api/
mkdir -p /var/log/yandex/taxi-driver-orders-app-api/
ln -sf /taxi/logs/application-taxi-driver-orders-app-api.log /var/log/yandex/taxi-driver-orders-app-api/server.log

/taxi/tools/run.py \
    --stdout-to-log \
    --nginx yandex-taxi-driver-orders-app-api \
    --fix-userver-client-timeout /etc/yandex/taxi/driver-orders-app-api/config.yaml \
    --syslog \
    --wait \
        redis.taxi.yandex:6379 \
        http://configs.taxi.yandex.net/ping \
    --run /usr/bin/yandex-taxi-driver-orders-app-api \
        --config /etc/yandex/taxi/driver-orders-app-api/config.yaml \
        --init-log /taxi/logs/application-taxi-driver-orders-app-api-init.log
