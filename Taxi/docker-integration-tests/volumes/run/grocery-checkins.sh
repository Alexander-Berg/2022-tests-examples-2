#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_CHECKINS_PATH=$USERVICES_PATH/build-integration/services/grocery-checkins
GROCERY_CHECKINS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-checkins
GROCERY_CHECKINS_DEB_PATH=$USERVICES_PATH/services/grocery-checkins/debian

GROCERY_CHECKINS_BINARY_PATH=
if [ -f "$GROCERY_CHECKINS_PATH/yandex-taxi-grocery-checkins" ]; then
  GROCERY_CHECKINS_BINARY_PATH="$GROCERY_CHECKINS_PATH/yandex-taxi-grocery-checkins"
elif [ -f "$GROCERY_CHECKINS_ARCADIA_PATH/yandex-taxi-grocery-checkins" ]; then
  GROCERY_CHECKINS_BINARY_PATH="$GROCERY_CHECKINS_ARCADIA_PATH/yandex-taxi-grocery-checkins"
fi

if [ -f "$GROCERY_CHECKINS_BINARY_PATH" ]; then
    echo "grocery-checkins update package"
    mkdir -p /etc/yandex/taxi/grocery-checkins/
    rm -rf /etc/yandex/taxi/grocery-checkins/*

    ln -s $GROCERY_CHECKINS_PATH/configs/* /etc/yandex/taxi/grocery-checkins/
    cp $GROCERY_CHECKINS_PATH/config.yaml /etc/yandex/taxi/grocery-checkins/
    ln -s $GROCERY_CHECKINS_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-checkins/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-checkins/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-checkins/config_vars.yaml

    ln -sf $GROCERY_CHECKINS_DEB_PATH/yandex-taxi-grocery-checkins.nginx /etc/nginx/sites-available/yandex-taxi-grocery-checkins
    ln -sf $GROCERY_CHECKINS_DEB_PATH/yandex-taxi-grocery-checkins.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_CHECKINS_PATH/taxi-grocery-checkins-stats.py /usr/bin/
    echo "using binary: $GROCERY_CHECKINS_BINARY_PATH"
    ln -sf $GROCERY_CHECKINS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-checkins/
mkdir -p /var/lib/yandex/taxi-grocery-checkins/
mkdir -p /var/lib/yandex/taxi-grocery-checkins/private/
mkdir -p /var/cache/yandex/taxi-grocery-checkins/
ln -sf /taxi/logs/application-taxi-grocery-checkins.log /var/log/yandex/taxi-grocery-checkins/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-checkins \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-checkins/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-checkins \
        --config /etc/yandex/taxi/grocery-checkins/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-checkins/server.log
