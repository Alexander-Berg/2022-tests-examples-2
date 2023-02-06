#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_TAKEOUT_PATH=$USERVICES_PATH/build-integration/services/grocery-takeout
GROCERY_TAKEOUT_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-takeout
GROCERY_TAKEOUT_DEB_PATH=$USERVICES_PATH/services/grocery-takeout/debian

GROCERY_TAKEOUT_BINARY_PATH=
if [ -f "$GROCERY_TAKEOUT_PATH/yandex-taxi-grocery-takeout" ]; then
  GROCERY_TAKEOUT_BINARY_PATH="$GROCERY_TAKEOUT_PATH/yandex-taxi-grocery-takeout"
elif [ -f "$GROCERY_TAKEOUT_ARCADIA_PATH/yandex-taxi-grocery-takeout" ]; then
  GROCERY_TAKEOUT_BINARY_PATH="$GROCERY_TAKEOUT_ARCADIA_PATH/yandex-taxi-grocery-takeout"
fi

if [ -f "$GROCERY_TAKEOUT_BINARY_PATH" ]; then
    echo "grocery-takeout update package"
    mkdir -p /etc/yandex/taxi/grocery-takeout/
    rm -rf /etc/yandex/taxi/grocery-takeout/*

    ln -s $GROCERY_TAKEOUT_PATH/configs/* /etc/yandex/taxi/grocery-takeout/
    cp $GROCERY_TAKEOUT_PATH/config.yaml /etc/yandex/taxi/grocery-takeout/
    ln -s $GROCERY_TAKEOUT_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-takeout/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-takeout/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-takeout/config_vars.yaml

    ln -sf $GROCERY_TAKEOUT_DEB_PATH/yandex-taxi-grocery-takeout.nginx /etc/nginx/sites-available/yandex-taxi-grocery-takeout
    ln -sf $GROCERY_TAKEOUT_DEB_PATH/yandex-taxi-grocery-takeout.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_TAKEOUT_PATH/taxi-grocery-takeout-stats.py /usr/bin/
    echo "using binary: $GROCERY_TAKEOUT_BINARY_PATH"
    ln -sf $GROCERY_TAKEOUT_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-takeout/
mkdir -p /var/lib/yandex/taxi-grocery-takeout/
mkdir -p /var/lib/yandex/taxi-grocery-takeout/private/
mkdir -p /var/cache/yandex/taxi-grocery-takeout/
ln -sf /taxi/logs/application-taxi-grocery-takeout.log /var/log/yandex/taxi-grocery-takeout/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-takeout \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-takeout/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-takeout \
        --config /etc/yandex/taxi/grocery-takeout/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-takeout/server.log
