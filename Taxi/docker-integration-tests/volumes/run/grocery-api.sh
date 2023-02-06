#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_API_PATH=$USERVICES_PATH/build-integration/services/grocery-api
GROCERY_API_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-api
GROCERY_API_DEB_PATH=$USERVICES_PATH/services/grocery-api/debian

GROCERY_API_BINARY_PATH=
if [ -f "$GROCERY_API_PATH/yandex-taxi-grocery-api" ]; then
  GROCERY_API_BINARY_PATH="$GROCERY_API_PATH/yandex-taxi-grocery-api"
elif [ -f "$GROCERY_API_ARCADIA_PATH/yandex-taxi-grocery-api" ]; then
  GROCERY_API_BINARY_PATH="$GROCERY_API_ARCADIA_PATH/yandex-taxi-grocery-api"
fi

if [ -f "$GROCERY_API_BINARY_PATH" ]; then
    echo "grocery-api update package"
    mkdir -p /etc/yandex/taxi/grocery-api/
    rm -rf /etc/yandex/taxi/grocery-api/*

    ln -s $GROCERY_API_PATH/configs/* /etc/yandex/taxi/grocery-api/
    cp $GROCERY_API_PATH/config.yaml /etc/yandex/taxi/grocery-api/
    ln -s $GROCERY_API_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-api/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-api/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-api/config_vars.yaml

    ln -sf $GROCERY_API_DEB_PATH/yandex-taxi-grocery-api.nginx /etc/nginx/sites-available/yandex-taxi-grocery-api
    ln -sf $GROCERY_API_DEB_PATH/yandex-taxi-grocery-api.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_API_PATH/taxi-grocery-api-stats.py /usr/bin/
    echo "using binary: $GROCERY_API_BINARY_PATH"
    ln -sf $GROCERY_API_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-api/
mkdir -p /var/lib/yandex/taxi-grocery-api/
mkdir -p /var/lib/yandex/taxi-grocery-api/private/
mkdir -p /var/cache/yandex/taxi-grocery-api/
ln -sf /taxi/logs/application-taxi-grocery-api.log /var/log/yandex/taxi-grocery-api/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-api \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-api/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-api \
        --config /etc/yandex/taxi/grocery-api/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-api/server.log
