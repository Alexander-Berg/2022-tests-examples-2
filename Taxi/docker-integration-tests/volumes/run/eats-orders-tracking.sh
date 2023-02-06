#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
EATS_ORDERS_TRACKING_PATH=$USERVICES_PATH/build-integration/services/eats-orders-tracking
EATS_ORDERS_TRACKING_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/eats-orders-tracking
EATS_ORDERS_TRACKING_DEB_PATH=$USERVICES_PATH/services/eats-orders-tracking/debian

EATS_ORDERS_TRACKING_BINARY_PATH=
if [ -f "$EATS_ORDERS_TRACKING_PATH/yandex-taxi-eats-orders-tracking" ]; then
  EATS_ORDERS_TRACKING_BINARY_PATH="$EATS_ORDERS_TRACKING_PATH/yandex-taxi-eats-orders-tracking"
elif [ -f "$EATS_ORDERS_TRACKING_ARCADIA_PATH/yandex-taxi-eats-orders-tracking" ]; then
  EATS_ORDERS_TRACKING_BINARY_PATH="$EATS_ORDERS_TRACKING_ARCADIA_PATH/yandex-taxi-eats-orders-tracking"
fi

if [ -f "$EATS_ORDERS_TRACKING_BINARY_PATH" ]; then
    echo "eats-orders-tracking update package"
    mkdir -p /etc/yandex/taxi/eats-orders-tracking/
    rm -rf /etc/yandex/taxi/eats-orders-tracking/*

    ln -s $EATS_ORDERS_TRACKING_PATH/configs/* /etc/yandex/taxi/eats-orders-tracking/
    cp $EATS_ORDERS_TRACKING_PATH/config.yaml /etc/yandex/taxi/eats-orders-tracking/
    ln -s $EATS_ORDERS_TRACKING_PATH/taxi_config_fallback.json /etc/yandex/taxi/eats-orders-tracking/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/eats-orders-tracking/
    ln -s config_vars.production.yaml /etc/yandex/taxi/eats-orders-tracking/config_vars.yaml

    ln -sf $EATS_ORDERS_TRACKING_DEB_PATH/yandex-taxi-eats-orders-tracking.nginx /etc/nginx/sites-available/yandex-taxi-eats-orders-tracking
    ln -sf $EATS_ORDERS_TRACKING_DEB_PATH/yandex-taxi-eats-orders-tracking.upstream_list /etc/nginx/conf.d/

    ln -sf $EATS_ORDERS_TRACKING_PATH/taxi-eats-orders-tracking-stats.py /usr/bin/
    echo "using binary: $EATS_ORDERS_TRACKING_BINARY_PATH"
    ln -sf $EATS_ORDERS_TRACKING_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-eats-orders-tracking/
mkdir -p /var/lib/yandex/taxi-eats-orders-tracking/
mkdir -p /var/lib/yandex/taxi-eats-orders-tracking/private/
mkdir -p /var/cache/yandex/taxi-eats-orders-tracking/
ln -sf /taxi/logs/application-taxi-eats-orders-tracking.log /var/log/yandex/taxi-eats-orders-tracking/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-eats-orders-tracking \
    --fix-userver-client-timeout /etc/yandex/taxi/eats-orders-tracking/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-eats-orders-tracking \
        --config /etc/yandex/taxi/eats-orders-tracking/config.yaml \
        --init-log /var/log/yandex/taxi-eats-orders-tracking/server.log
