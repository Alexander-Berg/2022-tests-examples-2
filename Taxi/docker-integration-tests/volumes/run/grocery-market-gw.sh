#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_MARKET_GW_PATH=$USERVICES_PATH/build-integration/services/grocery-market-gw
GROCERY_MARKET_GW_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-market-gw
GROCERY_MARKET_GW_DEB_PATH=$USERVICES_PATH/services/grocery-market-gw/debian

GROCERY_MARKET_GW_BINARY_PATH=
if [ -f "$GROCERY_MARKET_GW_PATH/yandex-taxi-grocery-market-gw" ]; then
  GROCERY_MARKET_GW_BINARY_PATH="$GROCERY_MARKET_GW_PATH/yandex-taxi-grocery-market-gw"
elif [ -f "$GROCERY_MARKET_GW_ARCADIA_PATH/yandex-taxi-grocery-market-gw" ]; then
  GROCERY_MARKET_GW_BINARY_PATH="$GROCERY_MARKET_GW_ARCADIA_PATH/yandex-taxi-grocery-market-gw"
fi

if [ -f "$GROCERY_MARKET_GW_BINARY_PATH" ]; then
    echo "grocery-market-gw update package"
    mkdir -p /etc/yandex/taxi/grocery-market-gw/
    rm -rf /etc/yandex/taxi/grocery-market-gw/*

    ln -s $GROCERY_MARKET_GW_PATH/configs/* /etc/yandex/taxi/grocery-market-gw/
    cp $GROCERY_MARKET_GW_PATH/config.yaml /etc/yandex/taxi/grocery-market-gw/
    ln -s $GROCERY_MARKET_GW_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-market-gw/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-market-gw/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-market-gw/config_vars.yaml

    ln -sf $GROCERY_MARKET_GW_DEB_PATH/yandex-taxi-grocery-market-gw.nginx /etc/nginx/sites-available/yandex-taxi-grocery-market-gw
    ln -sf $GROCERY_MARKET_GW_DEB_PATH/yandex-taxi-grocery-market-gw.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_MARKET_GW_PATH/taxi-grocery-market-gw-stats.py /usr/bin/
    echo "using binary: $GROCERY_MARKET_GW_BINARY_PATH"
    ln -sf $GROCERY_MARKET_GW_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-market-gw/
mkdir -p /var/lib/yandex/taxi-grocery-market-gw/
mkdir -p /var/lib/yandex/taxi-grocery-market-gw/private/
mkdir -p /var/cache/yandex/taxi-grocery-market-gw/
ln -sf /taxi/logs/application-taxi-grocery-market-gw.log /var/log/yandex/taxi-grocery-market-gw/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-market-gw \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-market-gw/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-market-gw \
        --config /etc/yandex/taxi/grocery-market-gw/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-market-gw/server.log
