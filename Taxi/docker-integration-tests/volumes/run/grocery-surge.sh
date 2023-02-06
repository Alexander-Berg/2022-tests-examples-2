#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_SURGE_PATH=$USERVICES_PATH/build-integration/services/grocery-surge
GROCERY_SURGE_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-surge
GROCERY_SURGE_DEB_PATH=$USERVICES_PATH/services/grocery-surge/debian

GROCERY_SURGE_BINARY_PATH=
if [ -f "$GROCERY_SURGE_PATH/yandex-taxi-grocery-surge" ]; then
  GROCERY_SURGE_BINARY_PATH="$GROCERY_SURGE_PATH/yandex-taxi-grocery-surge"
elif [ -f "$GROCERY_SURGE_ARCADIA_PATH/yandex-taxi-grocery-surge" ]; then
  GROCERY_SURGE_BINARY_PATH="$GROCERY_SURGE_ARCADIA_PATH/yandex-taxi-grocery-surge"
fi

if [ -f "$GROCERY_SURGE_BINARY_PATH" ]; then
    echo "grocery-surge update package"
    mkdir -p /etc/yandex/taxi/grocery-surge/
    rm -rf /etc/yandex/taxi/grocery-surge/*

    ln -s $GROCERY_SURGE_PATH/configs/* /etc/yandex/taxi/grocery-surge/
    cp $GROCERY_SURGE_PATH/config.yaml /etc/yandex/taxi/grocery-surge/
    ln -s $GROCERY_SURGE_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-surge/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-surge/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-surge/config_vars.yaml

    ln -sf $GROCERY_SURGE_DEB_PATH/yandex-taxi-grocery-surge.nginx /etc/nginx/sites-available/yandex-taxi-grocery-surge
    ln -sf $GROCERY_SURGE_DEB_PATH/yandex-taxi-grocery-surge.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_SURGE_PATH/taxi-grocery-surge-stats.py /usr/bin/
    echo "using binary: $GROCERY_SURGE_BINARY_PATH"
    ln -sf $GROCERY_SURGE_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-surge/
mkdir -p /var/lib/yandex/taxi-grocery-surge/
mkdir -p /var/lib/yandex/taxi-grocery-surge/private/
mkdir -p /var/cache/yandex/taxi-grocery-surge/
ln -sf /taxi/logs/application-taxi-grocery-surge.log /var/log/yandex/taxi-grocery-surge/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-surge \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-surge/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-surge \
        --config /etc/yandex/taxi/grocery-surge/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-surge/server.log
