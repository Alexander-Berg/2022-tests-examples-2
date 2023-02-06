#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_DISCOUNTS_PATH=$USERVICES_PATH/build-integration/services/grocery-discounts
GROCERY_DISCOUNTS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-discounts
GROCERY_DISCOUNTS_DEB_PATH=$USERVICES_PATH/services/grocery-discounts/debian

GROCERY_DISCOUNTS_BINARY_PATH=
if [ -f "$GROCERY_DISCOUNTS_PATH/yandex-taxi-grocery-discounts" ]; then
  GROCERY_DISCOUNTS_BINARY_PATH="$GROCERY_DISCOUNTS_PATH/yandex-taxi-grocery-discounts"
elif [ -f "$GROCERY_DISCOUNTS_ARCADIA_PATH/yandex-taxi-grocery-discounts" ]; then
  GROCERY_DISCOUNTS_BINARY_PATH="$GROCERY_DISCOUNTS_ARCADIA_PATH/yandex-taxi-grocery-discounts"
fi

if [ -f "$GROCERY_DISCOUNTS_BINARY_PATH" ]; then
    echo "grocery-discounts update package"
    mkdir -p /etc/yandex/taxi/grocery-discounts/
    rm -rf /etc/yandex/taxi/grocery-discounts/*

    ln -s $GROCERY_DISCOUNTS_PATH/configs/* /etc/yandex/taxi/grocery-discounts/
    cp $GROCERY_DISCOUNTS_PATH/config.yaml /etc/yandex/taxi/grocery-discounts/
    ln -s $GROCERY_DISCOUNTS_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-discounts/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-discounts/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-discounts/config_vars.yaml

    ln -sf $GROCERY_DISCOUNTS_DEB_PATH/yandex-taxi-grocery-discounts.nginx /etc/nginx/sites-available/yandex-taxi-grocery-discounts
    ln -sf $GROCERY_DISCOUNTS_DEB_PATH/yandex-taxi-grocery-discounts.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_DISCOUNTS_PATH/taxi-grocery-discounts-stats.py /usr/bin/
    echo "using binary: $GROCERY_DISCOUNTS_BINARY_PATH"
    ln -sf $GROCERY_DISCOUNTS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-discounts/
mkdir -p /var/lib/yandex/taxi-grocery-discounts/
mkdir -p /var/lib/yandex/taxi-grocery-discounts/private/
mkdir -p /var/cache/yandex/taxi-grocery-discounts/
ln -sf /taxi/logs/application-taxi-grocery-discounts.log /var/log/yandex/taxi-grocery-discounts/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-discounts \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-discounts/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-discounts \
        --config /etc/yandex/taxi/grocery-discounts/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-discounts/server.log
