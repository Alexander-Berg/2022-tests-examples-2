#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
CARGO_ORDERS_PATH=$USERVICES_PATH/build-integration/services/cargo-orders
CARGO_ORDERS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/cargo-orders
CARGO_ORDERS_DEB_PATH=$USERVICES_PATH/services/cargo-orders/debian

CARGO_ORDERS_BINARY_PATH=
if [ -f "$CARGO_ORDERS_PATH/yandex-taxi-cargo-orders" ]; then
  CARGO_ORDERS_BINARY_PATH="$CARGO_ORDERS_PATH/yandex-taxi-cargo-orders"
elif [ -f "$CARGO_ORDERS_ARCADIA_PATH/yandex-taxi-cargo-orders" ]; then
  CARGO_ORDERS_BINARY_PATH="$CARGO_ORDERS_ARCADIA_PATH/yandex-taxi-cargo-orders"
fi

if [ -f "$CARGO_ORDERS_PATH/yandex-taxi-cargo-orders" ]; then
    echo "cargo-orders update package"
    mkdir -p /etc/yandex/taxi/cargo-orders/
    rm -rf /etc/yandex/taxi/cargo-orders/*

    ln -s $CARGO_ORDERS_PATH/configs/* /etc/yandex/taxi/cargo-orders/
    cp $CARGO_ORDERS_PATH/config.yaml /etc/yandex/taxi/cargo-orders/
    ln -s $CARGO_ORDERS_PATH/taxi_config_fallback.json /etc/yandex/taxi/cargo-orders/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/cargo-orders/
    ln -s config_vars.production.yaml /etc/yandex/taxi/cargo-orders/config_vars.yaml

    ln -sf $CARGO_ORDERS_DEB_PATH/yandex-taxi-cargo-orders.nginx /etc/nginx/sites-available/yandex-taxi-cargo-orders
    ln -sf $CARGO_ORDERS_DEB_PATH/yandex-taxi-cargo-orders.upstream_list /etc/nginx/conf.d/

    ln -sf $CARGO_ORDERS_PATH/taxi-cargo-orders-stats.py /usr/bin/

    echo "using binary: $CARGO_ORDERS_BINARY_PATH"
    ln -sf $CARGO_ORDERS_PATH/yandex-taxi-cargo-orders /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-cargo-orders/
mkdir -p /var/lib/yandex/taxi-cargo-orders/
mkdir -p /var/lib/yandex/taxi-cargo-orders/private/
mkdir -p /var/cache/yandex/taxi-cargo-orders/
ln -sf /taxi/logs/application-taxi-cargo-orders.log /var/log/yandex/taxi-cargo-orders/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-cargo-orders \
    --fix-userver-client-timeout /etc/yandex/taxi/cargo-orders/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-cargo-orders \
        --config /etc/yandex/taxi/cargo-orders/config.yaml \
        --init-log /var/log/yandex/taxi-cargo-orders/server.log
