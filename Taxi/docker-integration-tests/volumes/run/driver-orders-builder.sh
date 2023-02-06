#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
DRIVER_ORDERS_BUILDER_PATH=$USERVICES_PATH/build-integration/services/driver-orders-builder
DRIVER_ORDERS_BUILDER_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/driver-orders-builder
DRIVER_ORDERS_BUILDER_DEB_PATH=$USERVICES_PATH/services/driver-orders-builder/debian

DRIVER_ORDERS_BUILDER_BINARY_PATH=
if [ -f "$DRIVER_ORDERS_BUILDER_PATH/yandex-taxi-driver-orders-builder" ]; then
  DRIVER_ORDERS_BUILDER_BINARY_PATH="$DRIVER_ORDERS_BUILDER_PATH/yandex-taxi-driver-orders-builder"
elif [ -f "$DRIVER_ORDERS_BUILDER_ARCADIA_PATH/yandex-taxi-driver-orders-builder" ]; then
  DRIVER_ORDERS_BUILDER_BINARY_PATH="$DRIVER_ORDERS_BUILDER_ARCADIA_PATH/yandex-taxi-driver-orders-builder"
fi

if [ -f "$DRIVER_ORDERS_BUILDER_BINARY_PATH" ]; then
    echo "driver-orders-builder update package"
    mkdir -p /etc/yandex/taxi/driver-orders-builder/
    rm -rf /etc/yandex/taxi/driver-orders-builder/*

    ln -s $DRIVER_ORDERS_BUILDER_PATH/configs/* /etc/yandex/taxi/driver-orders-builder/
    cp $DRIVER_ORDERS_BUILDER_PATH/config.yaml /etc/yandex/taxi/driver-orders-builder/
    ln -s $DRIVER_ORDERS_BUILDER_PATH/taxi_config_fallback.json /etc/yandex/taxi/driver-orders-builder/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/driver-orders-builder/
    ln -s config_vars.production.yaml /etc/yandex/taxi/driver-orders-builder/config_vars.yaml

    ln -sf $DRIVER_ORDERS_BUILDER_DEB_PATH/yandex-taxi-driver-orders-builder.nginx /etc/nginx/sites-available/yandex-taxi-driver-orders-builder
    ln -sf $DRIVER_ORDERS_BUILDER_DEB_PATH/yandex-taxi-driver-orders-builder.upstream_list /etc/nginx/conf.d/

    ln -sf $DRIVER_ORDERS_BUILDER_PATH/taxi-driver-orders-builder-stats.py /usr/bin/

    echo "using binary: $DRIVER_ORDERS_BUILDER_BINARY_PATH"
    ln -sf $DRIVER_ORDERS_BUILDER_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-driver-orders-builder/
mkdir -p /var/lib/yandex/taxi-driver-orders-builder/
mkdir -p /var/lib/yandex/taxi-driver-orders-builder/private/
mkdir -p /var/cache/yandex/taxi-driver-orders-builder/
ln -sf /taxi/logs/application-taxi-driver-orders-builder.log /var/log/yandex/taxi-driver-orders-builder/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-driver-orders-builder \
    --fix-userver-client-timeout /etc/yandex/taxi/driver-orders-builder/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-driver-orders-builder \
        --config /etc/yandex/taxi/driver-orders-builder/config.yaml \
        --init-log /var/log/yandex/taxi-driver-orders-builder/server.log
