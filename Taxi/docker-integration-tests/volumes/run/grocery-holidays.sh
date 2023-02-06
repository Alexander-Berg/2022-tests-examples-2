#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_HOLIDAYS_PATH=$USERVICES_PATH/build-integration/services/grocery-holidays
GROCERY_HOLIDAYS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-holidays
GROCERY_HOLIDAYS_DEB_PATH=$USERVICES_PATH/services/grocery-holidays/debian

GROCERY_HOLIDAYS_BINARY_PATH=
if [ -f "$GROCERY_HOLIDAYS_PATH/yandex-taxi-grocery-holidays" ]; then
  GROCERY_HOLIDAYS_BINARY_PATH="$GROCERY_HOLIDAYS_PATH/yandex-taxi-grocery-holidays"
elif [ -f "$GROCERY_HOLIDAYS_ARCADIA_PATH/yandex-taxi-grocery-holidays" ]; then
  GROCERY_HOLIDAYS_BINARY_PATH="$GROCERY_HOLIDAYS_ARCADIA_PATH/yandex-taxi-grocery-holidays"
fi

if [ -f "$GROCERY_HOLIDAYS_BINARY_PATH" ]; then
    echo "grocery-holidays update package"
    mkdir -p /etc/yandex/taxi/grocery-holidays/
    rm -rf /etc/yandex/taxi/grocery-holidays/*

    ln -s $GROCERY_HOLIDAYS_PATH/configs/* /etc/yandex/taxi/grocery-holidays/
    cp $GROCERY_HOLIDAYS_PATH/config.yaml /etc/yandex/taxi/grocery-holidays/
    ln -s $GROCERY_HOLIDAYS_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-holidays/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-holidays/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-holidays/config_vars.yaml

    ln -sf $GROCERY_HOLIDAYS_DEB_PATH/yandex-taxi-grocery-holidays.nginx /etc/nginx/sites-available/yandex-taxi-grocery-holidays
    ln -sf $GROCERY_HOLIDAYS_DEB_PATH/yandex-taxi-grocery-holidays.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_HOLIDAYS_PATH/taxi-grocery-holidays-stats.py /usr/bin/
    echo "using binary: $GROCERY_HOLIDAYS_BINARY_PATH"
    ln -sf $GROCERY_HOLIDAYS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-holidays/
mkdir -p /var/lib/yandex/taxi-grocery-holidays/
mkdir -p /var/lib/yandex/taxi-grocery-holidays/private/
mkdir -p /var/cache/yandex/taxi-grocery-holidays/
ln -sf /taxi/logs/application-taxi-grocery-holidays.log /var/log/yandex/taxi-grocery-holidays/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-holidays \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-holidays/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-holidays \
        --config /etc/yandex/taxi/grocery-holidays/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-holidays/server.log
