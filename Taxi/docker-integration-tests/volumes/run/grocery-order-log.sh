#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_ORDER_LOG_PATH=$USERVICES_PATH/build-integration/services/grocery-order-log
GROCERY_ORDER_LOG_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-order-log
GROCERY_ORDER_LOG_DEB_PATH=$USERVICES_PATH/services/grocery-order-log/debian

GROCERY_ORDER_LOG_BINARY_PATH=
if [ -f "$GROCERY_ORDER_LOG_PATH/yandex-taxi-grocery-order-log" ]; then
  GROCERY_ORDER_LOG_BINARY_PATH="$GROCERY_ORDER_LOG_PATH/yandex-taxi-grocery-order-log"
elif [ -f "$GROCERY_ORDER_LOG_ARCADIA_PATH/yandex-taxi-grocery-order-log" ]; then
  GROCERY_ORDER_LOG_BINARY_PATH="$GROCERY_ORDER_LOG_ARCADIA_PATH/yandex-taxi-grocery-order-log"
fi

if [ -f "$GROCERY_ORDER_LOG_BINARY_PATH" ]; then
    echo "grocery-order-log update package"
    mkdir -p /etc/yandex/taxi/grocery-order-log/
    rm -rf /etc/yandex/taxi/grocery-order-log/*

    ln -s $GROCERY_ORDER_LOG_PATH/configs/* /etc/yandex/taxi/grocery-order-log/
    cp $GROCERY_ORDER_LOG_PATH/config.yaml /etc/yandex/taxi/grocery-order-log/
    ln -s $GROCERY_ORDER_LOG_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-order-log/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-order-log/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-order-log/config_vars.yaml

    ln -sf $GROCERY_ORDER_LOG_DEB_PATH/yandex-taxi-grocery-order-log.nginx /etc/nginx/sites-available/yandex-taxi-grocery-order-log
    ln -sf $GROCERY_ORDER_LOG_DEB_PATH/yandex-taxi-grocery-order-log.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_ORDER_LOG_PATH/taxi-grocery-order-log-stats.py /usr/bin/
    echo "using binary: $GROCERY_ORDER_LOG_BINARY_PATH"
    ln -sf $GROCERY_ORDER_LOG_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-order-log/
mkdir -p /var/lib/yandex/taxi-grocery-order-log/
mkdir -p /var/lib/yandex/taxi-grocery-order-log/private/
mkdir -p /var/cache/yandex/taxi-grocery-order-log/
ln -sf /taxi/logs/application-taxi-grocery-order-log.log /var/log/yandex/taxi-grocery-order-log/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-order-log \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-order-log/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-order-log \
        --config /etc/yandex/taxi/grocery-order-log/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-order-log/server.log
