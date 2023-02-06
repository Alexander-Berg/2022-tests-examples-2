#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_PICS_PATH=$USERVICES_PATH/build-integration/services/grocery-pics
GROCERY_PICS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-pics
GROCERY_PICS_DEB_PATH=$USERVICES_PATH/services/grocery-pics/debian

GROCERY_PICS_BINARY_PATH=
if [ -f "$GROCERY_PICS_PATH/yandex-taxi-grocery-pics" ]; then
  GROCERY_PICS_BINARY_PATH="$GROCERY_PICS_PATH/yandex-taxi-grocery-pics"
elif [ -f "$GROCERY_PICS_ARCADIA_PATH/yandex-taxi-grocery-pics" ]; then
  GROCERY_PICS_BINARY_PATH="$GROCERY_PICS_ARCADIA_PATH/yandex-taxi-grocery-pics"
fi

if [ -f "$GROCERY_PICS_BINARY_PATH" ]; then
    echo "grocery-pics update package"
    mkdir -p /etc/yandex/taxi/grocery-pics/
    rm -rf /etc/yandex/taxi/grocery-pics/*

    ln -s $GROCERY_PICS_PATH/configs/* /etc/yandex/taxi/grocery-pics/
    cp $GROCERY_PICS_PATH/config.yaml /etc/yandex/taxi/grocery-pics/
    ln -s $GROCERY_PICS_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-pics/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-pics/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-pics/config_vars.yaml

    ln -sf $GROCERY_PICS_DEB_PATH/yandex-taxi-grocery-pics.nginx /etc/nginx/sites-available/yandex-taxi-grocery-pics
    ln -sf $GROCERY_PICS_DEB_PATH/yandex-taxi-grocery-pics.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_PICS_PATH/taxi-grocery-pics-stats.py /usr/bin/
    echo "using binary: $GROCERY_PICS_BINARY_PATH"
    ln -sf $GROCERY_PICS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-pics/
mkdir -p /var/lib/yandex/taxi-grocery-pics/
mkdir -p /var/lib/yandex/taxi-grocery-pics/private/
mkdir -p /var/cache/yandex/taxi-grocery-pics/
ln -sf /taxi/logs/application-taxi-grocery-pics.log /var/log/yandex/taxi-grocery-pics/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-pics \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-pics/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-pics \
        --config /etc/yandex/taxi/grocery-pics/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-pics/server.log
