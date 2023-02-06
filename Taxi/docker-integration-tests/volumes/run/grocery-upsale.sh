#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_UPSALE_PATH=$USERVICES_PATH/build-integration/services/grocery-upsale
GROCERY_UPSALE_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-upsale
GROCERY_UPSALE_DEB_PATH=$USERVICES_PATH/services/grocery-upsale/debian

GROCERY_UPSALE_BINARY_PATH=
if [ -f "$GROCERY_UPSALE_PATH/yandex-taxi-grocery-upsale" ]; then
  GROCERY_UPSALE_BINARY_PATH="$GROCERY_UPSALE_PATH/yandex-taxi-grocery-upsale"
elif [ -f "$GROCERY_UPSALE_ARCADIA_PATH/yandex-taxi-grocery-upsale" ]; then
  GROCERY_UPSALE_BINARY_PATH="$GROCERY_UPSALE_ARCADIA_PATH/yandex-taxi-grocery-upsale"
fi

if [ -f "$GROCERY_UPSALE_BINARY_PATH" ]; then
    echo "grocery-upsale update package"
    mkdir -p /etc/yandex/taxi/grocery-upsale/
    rm -rf /etc/yandex/taxi/grocery-upsale/*

    ln -s $GROCERY_UPSALE_PATH/configs/* /etc/yandex/taxi/grocery-upsale/
    cp $GROCERY_UPSALE_PATH/config.yaml /etc/yandex/taxi/grocery-upsale/
    ln -s $GROCERY_UPSALE_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-upsale/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-upsale/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-upsale/config_vars.yaml

    ln -sf $GROCERY_UPSALE_DEB_PATH/yandex-taxi-grocery-upsale.nginx /etc/nginx/sites-available/yandex-taxi-grocery-upsale
    ln -sf $GROCERY_UPSALE_DEB_PATH/yandex-taxi-grocery-upsale.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_UPSALE_PATH/taxi-grocery-upsale-stats.py /usr/bin/
    echo "using binary: $GROCERY_UPSALE_BINARY_PATH"
    ln -sf $GROCERY_UPSALE_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-upsale/
mkdir -p /var/lib/yandex/taxi-grocery-upsale/
mkdir -p /var/lib/yandex/taxi-grocery-upsale/private/
mkdir -p /var/cache/yandex/taxi-grocery-upsale/
ln -sf /taxi/logs/application-taxi-grocery-upsale.log /var/log/yandex/taxi-grocery-upsale/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-upsale \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-upsale/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-upsale \
        --config /etc/yandex/taxi/grocery-upsale/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-upsale/server.log
