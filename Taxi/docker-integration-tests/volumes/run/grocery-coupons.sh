#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_COUPONS_PATH=$USERVICES_PATH/build-integration/services/grocery-coupons
GROCERY_COUPONS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-coupons
GROCERY_COUPONS_DEB_PATH=$USERVICES_PATH/services/grocery-coupons/debian

GROCERY_COUPONS_BINARY_PATH=
if [ -f "$GROCERY_COUPONS_PATH/yandex-taxi-grocery-coupons" ]; then
  GROCERY_COUPONS_BINARY_PATH="$GROCERY_COUPONS_PATH/yandex-taxi-grocery-coupons"
elif [ -f "$GROCERY_COUPONS_ARCADIA_PATH/yandex-taxi-grocery-coupons" ]; then
  GROCERY_COUPONS_BINARY_PATH="$GROCERY_COUPONS_ARCADIA_PATH/yandex-taxi-grocery-coupons"
fi

if [ -f "$GROCERY_COUPONS_BINARY_PATH" ]; then
    echo "grocery-coupons update package"
    mkdir -p /etc/yandex/taxi/grocery-coupons/
    rm -rf /etc/yandex/taxi/grocery-coupons/*

    ln -s $GROCERY_COUPONS_PATH/configs/* /etc/yandex/taxi/grocery-coupons/
    cp $GROCERY_COUPONS_PATH/config.yaml /etc/yandex/taxi/grocery-coupons/
    ln -s $GROCERY_COUPONS_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-coupons/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-coupons/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-coupons/config_vars.yaml

    ln -sf $GROCERY_COUPONS_DEB_PATH/yandex-taxi-grocery-coupons.nginx /etc/nginx/sites-available/yandex-taxi-grocery-coupons
    ln -sf $GROCERY_COUPONS_DEB_PATH/yandex-taxi-grocery-coupons.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_COUPONS_PATH/taxi-grocery-coupons-stats.py /usr/bin/
    echo "using binary: $GROCERY_COUPONS_BINARY_PATH"
    ln -sf $GROCERY_COUPONS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-coupons/
mkdir -p /var/lib/yandex/taxi-grocery-coupons/
mkdir -p /var/lib/yandex/taxi-grocery-coupons/private/
mkdir -p /var/cache/yandex/taxi-grocery-coupons/
ln -sf /taxi/logs/application-taxi-grocery-coupons.log /var/log/yandex/taxi-grocery-coupons/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-coupons \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-coupons/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-coupons \
        --config /etc/yandex/taxi/grocery-coupons/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-coupons/server.log
