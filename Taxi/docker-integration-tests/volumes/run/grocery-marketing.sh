#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_MARKETING_PATH=$USERVICES_PATH/build-integration/services/grocery-marketing
GROCERY_MARKETING_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-marketing
GROCERY_MARKETING_DEB_PATH=$USERVICES_PATH/services/grocery-marketing/debian

GROCERY_MARKETING_BINARY_PATH=
if [ -f "$GROCERY_MARKETING_PATH/yandex-taxi-grocery-marketing" ]; then
  GROCERY_MARKETING_BINARY_PATH="$GROCERY_MARKETING_PATH/yandex-taxi-grocery-marketing"
elif [ -f "$GROCERY_MARKETING_ARCADIA_PATH/yandex-taxi-grocery-marketing" ]; then
  GROCERY_MARKETING_BINARY_PATH="$GROCERY_MARKETING_ARCADIA_PATH/yandex-taxi-grocery-marketing"
fi

if [ -f "$GROCERY_MARKETING_BINARY_PATH" ]; then
    echo "grocery-marketing update package"
    mkdir -p /etc/yandex/taxi/grocery-marketing/
    rm -rf /etc/yandex/taxi/grocery-marketing/*

    ln -s $GROCERY_MARKETING_PATH/configs/* /etc/yandex/taxi/grocery-marketing/
    cp $GROCERY_MARKETING_PATH/config.yaml /etc/yandex/taxi/grocery-marketing/
    ln -s $GROCERY_MARKETING_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-marketing/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-marketing/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-marketing/config_vars.yaml

    ln -sf $GROCERY_MARKETING_DEB_PATH/yandex-taxi-grocery-marketing.nginx /etc/nginx/sites-available/yandex-taxi-grocery-marketing
    ln -sf $GROCERY_MARKETING_DEB_PATH/yandex-taxi-grocery-marketing.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_MARKETING_PATH/taxi-grocery-marketing-stats.py /usr/bin/
    echo "using binary: $GROCERY_MARKETING_BINARY_PATH"
    ln -sf $GROCERY_MARKETING_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-marketing/
mkdir -p /var/lib/yandex/taxi-grocery-marketing/
mkdir -p /var/lib/yandex/taxi-grocery-marketing/private/
mkdir -p /var/cache/yandex/taxi-grocery-marketing/
ln -sf /taxi/logs/application-taxi-grocery-marketing.log /var/log/yandex/taxi-grocery-marketing/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-marketing \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-marketing/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-marketing \
        --config /etc/yandex/taxi/grocery-marketing/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-marketing/server.log
