#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_SEARCH_PATH=$USERVICES_PATH/build-integration/services/grocery-search
GROCERY_SEARCH_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-search
GROCERY_SEARCH_DEB_PATH=$USERVICES_PATH/services/grocery-search/debian

GROCERY_SEARCH_BINARY_PATH=
if [ -f "$GROCERY_SEARCH_PATH/yandex-taxi-grocery-search" ]; then
  GROCERY_SEARCH_BINARY_PATH="$GROCERY_SEARCH_PATH/yandex-taxi-grocery-search"
elif [ -f "$GROCERY_SEARCH_ARCADIA_PATH/yandex-taxi-grocery-search" ]; then
  GROCERY_SEARCH_BINARY_PATH="$GROCERY_SEARCH_ARCADIA_PATH/yandex-taxi-grocery-search"
fi

if [ -f "$GROCERY_SEARCH_BINARY_PATH" ]; then
    echo "grocery-search update package"
    mkdir -p /etc/yandex/taxi/grocery-search/
    rm -rf /etc/yandex/taxi/grocery-search/*

    ln -s $GROCERY_SEARCH_PATH/configs/* /etc/yandex/taxi/grocery-search/
    cp $GROCERY_SEARCH_PATH/config.yaml /etc/yandex/taxi/grocery-search/
    ln -s $GROCERY_SEARCH_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-search/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-search/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-search/config_vars.yaml

    ln -sf $GROCERY_SEARCH_DEB_PATH/yandex-taxi-grocery-search.nginx /etc/nginx/sites-available/yandex-taxi-grocery-search
    ln -sf $GROCERY_SEARCH_DEB_PATH/yandex-taxi-grocery-search.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_SEARCH_PATH/taxi-grocery-search-stats.py /usr/bin/
    echo "using binary: $GROCERY_SEARCH_BINARY_PATH"
    ln -sf $GROCERY_SEARCH_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-search/
mkdir -p /var/lib/yandex/taxi-grocery-search/
mkdir -p /var/lib/yandex/taxi-grocery-search/private/
mkdir -p /var/cache/yandex/taxi-grocery-search/
ln -sf /taxi/logs/application-taxi-grocery-search.log /var/log/yandex/taxi-grocery-search/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-search \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-search/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-search \
        --config /etc/yandex/taxi/grocery-search/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-search/server.log
