#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_ORDERS_PATH=$USERVICES_PATH/build-integration/services/grocery-orders
GROCERY_ORDERS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-orders
GROCERY_ORDERS_DEB_PATH=$USERVICES_PATH/services/grocery-orders/debian

GROCERY_ORDERS_BINARY_PATH=
if [ -f "$GROCERY_ORDERS_PATH/yandex-taxi-grocery-orders" ]; then
  GROCERY_ORDERS_BINARY_PATH="$GROCERY_ORDERS_PATH/yandex-taxi-grocery-orders"
elif [ -f "$GROCERY_ORDERS_ARCADIA_PATH/yandex-taxi-grocery-orders" ]; then
  GROCERY_ORDERS_BINARY_PATH="$GROCERY_ORDERS_ARCADIA_PATH/yandex-taxi-grocery-orders"
fi

if [ -f "$GROCERY_ORDERS_BINARY_PATH" ]; then
    echo "grocery-orders update package"
    mkdir -p /etc/yandex/taxi/grocery-orders/
    rm -rf /etc/yandex/taxi/grocery-orders/*

    ln -s $GROCERY_ORDERS_PATH/configs/* /etc/yandex/taxi/grocery-orders/
    cp $GROCERY_ORDERS_PATH/config.yaml /etc/yandex/taxi/grocery-orders/
    ln -s $GROCERY_ORDERS_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-orders/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-orders/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-orders/config_vars.yaml

    ln -sf $GROCERY_ORDERS_DEB_PATH/yandex-taxi-grocery-orders.nginx /etc/nginx/sites-available/yandex-taxi-grocery-orders
    ln -sf $GROCERY_ORDERS_DEB_PATH/yandex-taxi-grocery-orders.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_ORDERS_PATH/taxi-grocery-orders-stats.py /usr/bin/
    echo "using binary: $GROCERY_ORDERS_BINARY_PATH"
    ln -sf $GROCERY_ORDERS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-orders/
mkdir -p /var/lib/yandex/taxi-grocery-orders/
mkdir -p /var/lib/yandex/taxi-grocery-orders/private/
mkdir -p /var/cache/yandex/taxi-grocery-orders/
ln -sf /taxi/logs/application-taxi-grocery-orders.log /var/log/yandex/taxi-grocery-orders/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-orders \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-orders/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-orders \
        --config /etc/yandex/taxi/grocery-orders/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-orders/server.log
