#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
EATS_PICKER_PAYMENTS_PATH=$USERVICES_PATH/build-integration/services/eats-picker-payments
EATS_PICKER_PAYMENTS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/eats-picker-payments
EATS_PICKER_PAYMENTS_DEB_PATH=$USERVICES_PATH/services/eats-picker-payments/debian

EATS_PICKER_PAYMENTS_BINARY_PATH=
if [ -f "$EATS_PICKER_PAYMENTS_PATH/yandex-taxi-eats-picker-payments" ]; then
  EATS_PICKER_PAYMENTS_BINARY_PATH="$EATS_PICKER_PAYMENTS_PATH/yandex-taxi-eats-picker-payments"
elif [ -f "$EATS_PICKER_PAYMENTS_ARCADIA_PATH/yandex-taxi-eats-picker-payments" ]; then
  EATS_PICKER_PAYMENTS_BINARY_PATH="$EATS_PICKER_PAYMENTS_ARCADIA_PATH/yandex-taxi-eats-picker-payments"
fi

if [ -f "$EATS_PICKER_PAYMENTS_BINARY_PATH" ]; then
    echo "eats-picker-payments update package"
    mkdir -p /etc/yandex/taxi/eats-picker-payments/
    rm -rf /etc/yandex/taxi/eats-picker-payments/*

    ln -s $EATS_PICKER_PAYMENTS_PATH/configs/* /etc/yandex/taxi/eats-picker-payments/
    cp $EATS_PICKER_PAYMENTS_PATH/config.yaml /etc/yandex/taxi/eats-picker-payments/
    ln -s $EATS_PICKER_PAYMENTS_PATH/taxi_config_fallback.json /etc/yandex/taxi/eats-picker-payments/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/eats-picker-payments/
    ln -s config_vars.production.yaml /etc/yandex/taxi/eats-picker-payments/config_vars.yaml

    ln -sf $EATS_PICKER_PAYMENTS_DEB_PATH/yandex-taxi-eats-picker-payments.nginx /etc/nginx/sites-available/yandex-taxi-eats-picker-payments
    ln -sf $EATS_PICKER_PAYMENTS_DEB_PATH/yandex-taxi-eats-picker-payments.upstream_list /etc/nginx/conf.d/

    ln -sf $EATS_PICKER_PAYMENTS_PATH/taxi-eats-picker-payments-stats.py /usr/bin/
    echo "using binary: $EATS_PICKER_PAYMENTS_BINARY_PATH"
    ln -sf $EATS_PICKER_PAYMENTS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-eats-picker-payments/
mkdir -p /var/lib/yandex/taxi-eats-picker-payments/
mkdir -p /var/lib/yandex/taxi-eats-picker-payments/private/
mkdir -p /var/cache/yandex/taxi-eats-picker-payments/
ln -sf /taxi/logs/application-taxi-eats-picker-payments.log /var/log/yandex/taxi-eats-picker-payments/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-eats-picker-payments \
    --fix-userver-client-timeout /etc/yandex/taxi/eats-picker-payments/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-eats-picker-payments \
        --config /etc/yandex/taxi/eats-picker-payments/config.yaml \
        --init-log /var/log/yandex/taxi-eats-picker-payments/server.log
