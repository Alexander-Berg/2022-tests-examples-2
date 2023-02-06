#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_DEPOTS_PATH=$USERVICES_PATH/build-integration/services/grocery-depots
GROCERY_DEPOTS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-depots
GROCERY_DEPOTS_DEB_PATH=$USERVICES_PATH/services/grocery-depots/debian

GROCERY_DEPOTS_BINARY_PATH=
if [ -f "$GROCERY_DEPOTS_PATH/yandex-taxi-grocery-depots" ]; then
  GROCERY_DEPOTS_BINARY_PATH="$GROCERY_DEPOTS_PATH/yandex-taxi-grocery-depots"
elif [ -f "$GROCERY_DEPOTS_ARCADIA_PATH/yandex-taxi-grocery-depots" ]; then
  GROCERY_DEPOTS_BINARY_PATH="$GROCERY_DEPOTS_ARCADIA_PATH/yandex-taxi-grocery-depots"
fi

if [ -f "$GROCERY_DEPOTS_BINARY_PATH" ]; then
    echo "grocery-depots update package"
    mkdir -p /etc/yandex/taxi/grocery-depots/
    rm -rf /etc/yandex/taxi/grocery-depots/*

    ln -s $GROCERY_DEPOTS_PATH/configs/* /etc/yandex/taxi/grocery-depots/
    cp $GROCERY_DEPOTS_PATH/config.yaml /etc/yandex/taxi/grocery-depots/
    ln -s $GROCERY_DEPOTS_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-depots/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-depots/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-depots/config_vars.yaml

    ln -sf $GROCERY_DEPOTS_DEB_PATH/yandex-taxi-grocery-depots.nginx /etc/nginx/sites-available/yandex-taxi-grocery-depots
    ln -sf $GROCERY_DEPOTS_DEB_PATH/yandex-taxi-grocery-depots.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_DEPOTS_PATH/taxi-grocery-depots-stats.py /usr/bin/
    echo "using binary: $GROCERY_DEPOTS_BINARY_PATH"
    ln -sf $GROCERY_DEPOTS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-depots/
mkdir -p /var/lib/yandex/taxi-grocery-depots/
mkdir -p /var/lib/yandex/taxi-grocery-depots/private/
mkdir -p /var/cache/yandex/taxi-grocery-depots/
ln -sf /taxi/logs/application-taxi-grocery-depots.log /var/log/yandex/taxi-grocery-depots/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-depots \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-depots/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-depots \
        --config /etc/yandex/taxi/grocery-depots/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-depots/server.log
