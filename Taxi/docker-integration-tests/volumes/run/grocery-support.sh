#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_SUPPORT_PATH=$USERVICES_PATH/build-integration/services/grocery-support
GROCERY_SUPPORT_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-support
GROCERY_SUPPORT_DEB_PATH=$USERVICES_PATH/services/grocery-support/debian

GROCERY_SUPPORT_BINARY_PATH=
if [ -f "$GROCERY_SUPPORT_PATH/yandex-taxi-grocery-support" ]; then
  GROCERY_SUPPORT_BINARY_PATH="$GROCERY_SUPPORT_PATH/yandex-taxi-grocery-support"
elif [ -f "$GROCERY_SUPPORT_ARCADIA_PATH/yandex-taxi-grocery-support" ]; then
  GROCERY_SUPPORT_BINARY_PATH="$GROCERY_SUPPORT_ARCADIA_PATH/yandex-taxi-grocery-support"
fi

if [ -f "$GROCERY_SUPPORT_BINARY_PATH" ]; then
    echo "grocery-support update package"
    mkdir -p /etc/yandex/taxi/grocery-support/
    rm -rf /etc/yandex/taxi/grocery-support/*

    ln -s $GROCERY_SUPPORT_PATH/configs/* /etc/yandex/taxi/grocery-support/
    cp $GROCERY_SUPPORT_PATH/config.yaml /etc/yandex/taxi/grocery-support/
    ln -s $GROCERY_SUPPORT_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-support/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-support/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-support/config_vars.yaml

    ln -sf $GROCERY_SUPPORT_DEB_PATH/yandex-taxi-grocery-support.nginx /etc/nginx/sites-available/yandex-taxi-grocery-support
    ln -sf $GROCERY_SUPPORT_DEB_PATH/yandex-taxi-grocery-support.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_SUPPORT_PATH/taxi-grocery-support-stats.py /usr/bin/
    echo "using binary: $GROCERY_SUPPORT_BINARY_PATH"
    ln -sf $GROCERY_SUPPORT_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-support/
mkdir -p /var/lib/yandex/taxi-grocery-support/
mkdir -p /var/lib/yandex/taxi-grocery-support/private/
mkdir -p /var/cache/yandex/taxi-grocery-support/
ln -sf /taxi/logs/application-taxi-grocery-support.log /var/log/yandex/taxi-grocery-support/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-support \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-support/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-support \
        --config /etc/yandex/taxi/grocery-support/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-support/server.log
