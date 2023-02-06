#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
EATS_PAYMENTS_PATH=$USERVICES_PATH/build-integration/services/eats-payments
EATS_PAYMENTS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/eats-payments
EATS_PAYMENTS_DEB_PATH=$USERVICES_PATH/services/eats-payments/debian

EATS_PAYMENTS_BINARY_PATH=
if [ -f "$EATS_PAYMENTS_PATH/yandex-taxi-eats-payments" ]; then
  EATS_PAYMENTS_BINARY_PATH="$EATS_PAYMENTS_PATH/yandex-taxi-eats-payments"
elif [ -f "$EATS_PAYMENTS_ARCADIA_PATH/yandex-taxi-eats-payments" ]; then
  EATS_PAYMENTS_BINARY_PATH="$EATS_PAYMENTS_ARCADIA_PATH/yandex-taxi-eats-payments"
fi

if [ -f "$EATS_PAYMENTS_BINARY_PATH" ]; then
    echo "eats-payments update package"
    mkdir -p /etc/yandex/taxi/eats-payments/
    rm -rf /etc/yandex/taxi/eats-payments/*

    ln -s $EATS_PAYMENTS_PATH/configs/* /etc/yandex/taxi/eats-payments/
    cp $EATS_PAYMENTS_PATH/config.yaml /etc/yandex/taxi/eats-payments/
    ln -s $EATS_PAYMENTS_PATH/taxi_config_fallback.json /etc/yandex/taxi/eats-payments/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/eats-payments/
    ln -s config_vars.production.yaml /etc/yandex/taxi/eats-payments/config_vars.yaml

    ln -sf $EATS_PAYMENTS_DEB_PATH/yandex-taxi-eats-payments.nginx /etc/nginx/sites-available/yandex-taxi-eats-payments
    ln -sf $EATS_PAYMENTS_DEB_PATH/yandex-taxi-eats-payments.upstream_list /etc/nginx/conf.d/

    ln -sf $EATS_PAYMENTS_PATH/taxi-eats-payments-stats.py /usr/bin/
    echo "using binary: $EATS_PAYMENTS_BINARY_PATH"
    ln -sf $EATS_PAYMENTS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-eats-payments/
mkdir -p /var/lib/yandex/taxi-eats-payments/
mkdir -p /var/lib/yandex/taxi-eats-payments/private/
mkdir -p /var/cache/yandex/taxi-eats-payments/
ln -sf /taxi/logs/application-taxi-eats-payments.log /var/log/yandex/taxi-eats-payments/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-eats-payments \
    --fix-userver-client-timeout /etc/yandex/taxi/eats-payments/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-eats-payments \
        --config /etc/yandex/taxi/eats-payments/config.yaml \
        --init-log /var/log/yandex/taxi-eats-payments/server.log
