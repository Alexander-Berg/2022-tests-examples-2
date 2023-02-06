#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_CASHBACK_PATH=$USERVICES_PATH/build-integration/services/grocery-cashback
GROCERY_CASHBACK_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-cashback
GROCERY_CASHBACK_DEB_PATH=$USERVICES_PATH/services/grocery-cashback/debian

GROCERY_CASHBACK_BINARY_PATH=
if [ -f "$GROCERY_CASHBACK_PATH/yandex-taxi-grocery-cashback" ]; then
  GROCERY_CASHBACK_BINARY_PATH="$GROCERY_CASHBACK_PATH/yandex-taxi-grocery-cashback"
elif [ -f "$GROCERY_CASHBACK_ARCADIA_PATH/yandex-taxi-grocery-cashback" ]; then
  GROCERY_CASHBACK_BINARY_PATH="$GROCERY_CASHBACK_ARCADIA_PATH/yandex-taxi-grocery-cashback"
fi

if [ -f "$GROCERY_CASHBACK_BINARY_PATH" ]; then
    echo "grocery-cashback update package"
    mkdir -p /etc/yandex/taxi/grocery-cashback/
    rm -rf /etc/yandex/taxi/grocery-cashback/*

    ln -s $GROCERY_CASHBACK_PATH/configs/* /etc/yandex/taxi/grocery-cashback/
    cp $GROCERY_CASHBACK_PATH/config.yaml /etc/yandex/taxi/grocery-cashback/
    ln -s $GROCERY_CASHBACK_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-cashback/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-cashback/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-cashback/config_vars.yaml

    ln -sf $GROCERY_CASHBACK_DEB_PATH/yandex-taxi-grocery-cashback.nginx /etc/nginx/sites-available/yandex-taxi-grocery-cashback
    ln -sf $GROCERY_CASHBACK_DEB_PATH/yandex-taxi-grocery-cashback.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_CASHBACK_PATH/taxi-grocery-cashback-stats.py /usr/bin/
    echo "using binary: $GROCERY_CASHBACK_BINARY_PATH"
    ln -sf $GROCERY_CASHBACK_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-cashback/
mkdir -p /var/lib/yandex/taxi-grocery-cashback/
mkdir -p /var/lib/yandex/taxi-grocery-cashback/private/
mkdir -p /var/cache/yandex/taxi-grocery-cashback/
ln -sf /taxi/logs/application-taxi-grocery-cashback.log /var/log/yandex/taxi-grocery-cashback/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-cashback \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-cashback/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-cashback \
        --config /etc/yandex/taxi/grocery-cashback/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-cashback/server.log
