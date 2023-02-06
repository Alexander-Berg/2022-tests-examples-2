#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_INVOICES_PATH=$USERVICES_PATH/build-integration/services/grocery-invoices
GROCERY_INVOICES_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-invoices
GROCERY_INVOICES_DEB_PATH=$USERVICES_PATH/services/grocery-invoices/debian

GROCERY_INVOICES_BINARY_PATH=
if [ -f "$GROCERY_INVOICES_PATH/yandex-taxi-grocery-invoices" ]; then
  GROCERY_INVOICES_BINARY_PATH="$GROCERY_INVOICES_PATH/yandex-taxi-grocery-invoices"
elif [ -f "$GROCERY_INVOICES_ARCADIA_PATH/yandex-taxi-grocery-invoices" ]; then
  GROCERY_INVOICES_BINARY_PATH="$GROCERY_INVOICES_ARCADIA_PATH/yandex-taxi-grocery-invoices"
fi

if [ -f "$GROCERY_INVOICES_BINARY_PATH" ]; then
    echo "grocery-invoices update package"
    mkdir -p /etc/yandex/taxi/grocery-invoices/
    rm -rf /etc/yandex/taxi/grocery-invoices/*

    ln -s $GROCERY_INVOICES_PATH/configs/* /etc/yandex/taxi/grocery-invoices/
    cp $GROCERY_INVOICES_PATH/config.yaml /etc/yandex/taxi/grocery-invoices/
    ln -s $GROCERY_INVOICES_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-invoices/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-invoices/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-invoices/config_vars.yaml

    ln -sf $GROCERY_INVOICES_DEB_PATH/yandex-taxi-grocery-invoices.nginx /etc/nginx/sites-available/yandex-taxi-grocery-invoices
    ln -sf $GROCERY_INVOICES_DEB_PATH/yandex-taxi-grocery-invoices.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_INVOICES_PATH/taxi-grocery-invoices-stats.py /usr/bin/
    echo "using binary: $GROCERY_INVOICES_BINARY_PATH"
    ln -sf $GROCERY_INVOICES_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-invoices/
mkdir -p /var/lib/yandex/taxi-grocery-invoices/
mkdir -p /var/lib/yandex/taxi-grocery-invoices/private/
mkdir -p /var/cache/yandex/taxi-grocery-invoices/
ln -sf /taxi/logs/application-taxi-grocery-invoices.log /var/log/yandex/taxi-grocery-invoices/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-invoices \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-invoices/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-invoices \
        --config /etc/yandex/taxi/grocery-invoices/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-invoices/server.log
