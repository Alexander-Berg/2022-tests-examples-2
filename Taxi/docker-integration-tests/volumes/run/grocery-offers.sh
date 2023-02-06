#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_OFFERS_PATH=$USERVICES_PATH/build-integration/services/grocery-offers
GROCERY_OFFERS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-offers
GROCERY_OFFERS_DEB_PATH=$USERVICES_PATH/services/grocery-offers/debian

GROCERY_OFFERS_BINARY_PATH=
if [ -f "$GROCERY_OFFERS_PATH/yandex-taxi-grocery-offers" ]; then
  GROCERY_OFFERS_BINARY_PATH="$GROCERY_OFFERS_PATH/yandex-taxi-grocery-offers"
elif [ -f "$GROCERY_OFFERS_ARCADIA_PATH/yandex-taxi-grocery-offers" ]; then
  GROCERY_OFFERS_BINARY_PATH="$GROCERY_OFFERS_ARCADIA_PATH/yandex-taxi-grocery-offers"
fi

if [ -f "$GROCERY_OFFERS_BINARY_PATH" ]; then
    echo "grocery-offers update package"
    mkdir -p /etc/yandex/taxi/grocery-offers/
    rm -rf /etc/yandex/taxi/grocery-offers/*

    ln -s $GROCERY_OFFERS_PATH/configs/* /etc/yandex/taxi/grocery-offers/
    cp $GROCERY_OFFERS_PATH/config.yaml /etc/yandex/taxi/grocery-offers/
    ln -s $GROCERY_OFFERS_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-offers/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-offers/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-offers/config_vars.yaml

    ln -sf $GROCERY_OFFERS_DEB_PATH/yandex-taxi-grocery-offers.nginx /etc/nginx/sites-available/yandex-taxi-grocery-offers
    ln -sf $GROCERY_OFFERS_DEB_PATH/yandex-taxi-grocery-offers.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_OFFERS_PATH/taxi-grocery-offers-stats.py /usr/bin/
    echo "using binary: $GROCERY_OFFERS_BINARY_PATH"
    ln -sf $GROCERY_OFFERS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-offers/
mkdir -p /var/lib/yandex/taxi-grocery-offers/
mkdir -p /var/lib/yandex/taxi-grocery-offers/private/
mkdir -p /var/cache/yandex/taxi-grocery-offers/
ln -sf /taxi/logs/application-taxi-grocery-offers.log /var/log/yandex/taxi-grocery-offers/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-offers \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-offers/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-offers \
        --config /etc/yandex/taxi/grocery-offers/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-offers/server.log
