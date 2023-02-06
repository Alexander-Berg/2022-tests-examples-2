#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
EATS_PICKER_ORDERS_PATH=$USERVICES_PATH/build-integration/services/eats-picker-orders
EATS_PICKER_ORDERS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/eats-picker-orders
EATS_PICKER_ORDERS_DEB_PATH=$USERVICES_PATH/services/eats-picker-orders/debian

EATS_PICKER_ORDERS_BINARY_PATH=
if [ -f "$EATS_PICKER_ORDERS_PATH/yandex-taxi-eats-picker-orders" ]; then
  EATS_PICKER_ORDERS_BINARY_PATH="$EATS_PICKER_ORDERS_PATH/yandex-taxi-eats-picker-orders"
elif [ -f "$EATS_PICKER_ORDERS_ARCADIA_PATH/yandex-taxi-eats-picker-orders" ]; then
  EATS_PICKER_ORDERS_BINARY_PATH="$EATS_PICKER_ORDERS_ARCADIA_PATH/yandex-taxi-eats-picker-orders"
fi

if [ -f "$EATS_PICKER_ORDERS_BINARY_PATH" ]; then
    echo "eats-picker-orders update package"
    mkdir -p /etc/yandex/taxi/eats-picker-orders/
    rm -rf /etc/yandex/taxi/eats-picker-orders/*

    ln -s $EATS_PICKER_ORDERS_PATH/configs/* /etc/yandex/taxi/eats-picker-orders/
    cp $EATS_PICKER_ORDERS_PATH/config.yaml /etc/yandex/taxi/eats-picker-orders/
    ln -s $EATS_PICKER_ORDERS_PATH/taxi_config_fallback.json /etc/yandex/taxi/eats-picker-orders/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/eats-picker-orders/
    ln -s config_vars.production.yaml /etc/yandex/taxi/eats-picker-orders/config_vars.yaml

    ln -sf $EATS_PICKER_ORDERS_DEB_PATH/yandex-taxi-eats-picker-orders.nginx /etc/nginx/sites-available/yandex-taxi-eats-picker-orders
    ln -sf $EATS_PICKER_ORDERS_DEB_PATH/yandex-taxi-eats-picker-orders.upstream_list /etc/nginx/conf.d/

    ln -sf $EATS_PICKER_ORDERS_PATH/taxi-eats-picker-orders-stats.py /usr/bin/
    echo "using binary: $EATS_PICKER_ORDERS_BINARY_PATH"
    ln -sf $EATS_PICKER_ORDERS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-eats-picker-orders/
mkdir -p /var/lib/yandex/taxi-eats-picker-orders/
mkdir -p /var/lib/yandex/taxi-eats-picker-orders/private/
mkdir -p /var/cache/yandex/taxi-eats-picker-orders/
ln -sf /taxi/logs/application-taxi-eats-picker-orders.log /var/log/yandex/taxi-eats-picker-orders/server.log

cat > /etc/nginx/conf.d/03-increased-timeout.conf <<EOF
    proxy_read_timeout 300;
EOF

/taxi/tools/run.py \
    --nginx yandex-taxi-eats-picker-orders \
    --fix-userver-client-timeout /etc/yandex/taxi/eats-picker-orders/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-eats-picker-orders \
        --config /etc/yandex/taxi/eats-picker-orders/config.yaml \
        --init-log /var/log/yandex/taxi-eats-picker-orders/server.log
