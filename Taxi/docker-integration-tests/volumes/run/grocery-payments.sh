#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_PAYMENTS_PATH=$USERVICES_PATH/build-integration/services/grocery-payments
GROCERY_PAYMENTS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-payments
GROCERY_PAYMENTS_DEB_PATH=$USERVICES_PATH/services/grocery-payments/debian

GROCERY_PAYMENTS_BINARY_PATH=
if [ -f "$GROCERY_PAYMENTS_PATH/yandex-taxi-grocery-payments" ]; then
  GROCERY_PAYMENTS_BINARY_PATH="$GROCERY_PAYMENTS_PATH/yandex-taxi-grocery-payments"
elif [ -f "$GROCERY_PAYMENTS_ARCADIA_PATH/yandex-taxi-grocery-payments" ]; then
  GROCERY_PAYMENTS_BINARY_PATH="$GROCERY_PAYMENTS_ARCADIA_PATH/yandex-taxi-grocery-payments"
fi

if [ -f "$GROCERY_PAYMENTS_BINARY_PATH" ]; then
    echo "grocery-payments update package"
    mkdir -p /etc/yandex/taxi/grocery-payments/
    rm -rf /etc/yandex/taxi/grocery-payments/*

    ln -s $GROCERY_PAYMENTS_PATH/configs/* /etc/yandex/taxi/grocery-payments/
    cp $GROCERY_PAYMENTS_PATH/config.yaml /etc/yandex/taxi/grocery-payments/
    ln -s $GROCERY_PAYMENTS_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-payments/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-payments/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-payments/config_vars.yaml

    ln -sf $GROCERY_PAYMENTS_DEB_PATH/yandex-taxi-grocery-payments.nginx /etc/nginx/sites-available/yandex-taxi-grocery-payments
    ln -sf $GROCERY_PAYMENTS_DEB_PATH/yandex-taxi-grocery-payments.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_PAYMENTS_PATH/taxi-grocery-payments-stats.py /usr/bin/
    echo "using binary: $GROCERY_PAYMENTS_BINARY_PATH"
    ln -sf $GROCERY_PAYMENTS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-payments/
mkdir -p /var/lib/yandex/taxi-grocery-payments/
mkdir -p /var/lib/yandex/taxi-grocery-payments/private/
mkdir -p /var/cache/yandex/taxi-grocery-payments/
ln -sf /taxi/logs/application-taxi-grocery-payments.log /var/log/yandex/taxi-grocery-payments/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-payments \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-payments/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-payments \
        --config /etc/yandex/taxi/grocery-payments/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-payments/server.log
