#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_PAYMENTS_BILLING_PATH=$USERVICES_PATH/build-integration/services/grocery-payments-billing
GROCERY_PAYMENTS_BILLING_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-payments-billing
GROCERY_PAYMENTS_BILLING_DEB_PATH=$USERVICES_PATH/services/grocery-payments-billing/debian

GROCERY_PAYMENTS_BILLING_BINARY_PATH=
if [ -f "$GROCERY_PAYMENTS_BILLING_PATH/yandex-taxi-grocery-payments-billing" ]; then
  GROCERY_PAYMENTS_BILLING_BINARY_PATH="$GROCERY_PAYMENTS_BILLING_PATH/yandex-taxi-grocery-payments-billing"
elif [ -f "$GROCERY_PAYMENTS_BILLING_ARCADIA_PATH/yandex-taxi-grocery-payments-billing" ]; then
  GROCERY_PAYMENTS_BILLING_BINARY_PATH="$GROCERY_PAYMENTS_BILLING_ARCADIA_PATH/yandex-taxi-grocery-payments-billing"
fi

if [ -f "$GROCERY_PAYMENTS_BILLING_BINARY_PATH" ]; then
    echo "grocery-payments-billing update package"
    mkdir -p /etc/yandex/taxi/grocery-payments-billing/
    rm -rf /etc/yandex/taxi/grocery-payments-billing/*

    ln -s $GROCERY_PAYMENTS_BILLING_PATH/configs/* /etc/yandex/taxi/grocery-payments-billing/
    cp $GROCERY_PAYMENTS_BILLING_PATH/config.yaml /etc/yandex/taxi/grocery-payments-billing/
    ln -s $GROCERY_PAYMENTS_BILLING_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-payments-billing/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-payments-billing/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-payments-billing/config_vars.yaml

    ln -sf $GROCERY_PAYMENTS_BILLING_DEB_PATH/yandex-taxi-grocery-payments-billing.nginx /etc/nginx/sites-available/yandex-taxi-grocery-payments-billing
    ln -sf $GROCERY_PAYMENTS_BILLING_DEB_PATH/yandex-taxi-grocery-payments-billing.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_PAYMENTS_BILLING_PATH/taxi-grocery-payments-billing-stats.py /usr/bin/
    echo "using binary: $GROCERY_PAYMENTS_BILLING_BINARY_PATH"
    ln -sf $GROCERY_PAYMENTS_BILLING_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-payments-billing/
mkdir -p /var/lib/yandex/taxi-grocery-payments-billing/
mkdir -p /var/lib/yandex/taxi-grocery-payments-billing/private/
mkdir -p /var/cache/yandex/taxi-grocery-payments-billing/
ln -sf /taxi/logs/application-taxi-grocery-payments-billing.log /var/log/yandex/taxi-grocery-payments-billing/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-payments-billing \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-payments-billing/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-payments-billing \
        --config /etc/yandex/taxi/grocery-payments-billing/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-payments-billing/server.log
