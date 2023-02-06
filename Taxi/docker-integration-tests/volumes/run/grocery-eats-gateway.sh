#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_EATS_GATEWAY_PATH=$USERVICES_PATH/build-integration/services/grocery-eats-gateway
GROCERY_EATS_GATEWAY_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-eats-gateway
GROCERY_EATS_GATEWAY_DEB_PATH=$USERVICES_PATH/services/grocery-eats-gateway/debian

GROCERY_EATS_GATEWAY_BINARY_PATH=
if [ -f "$GROCERY_EATS_GATEWAY_PATH/yandex-taxi-grocery-eats-gateway" ]; then
  GROCERY_EATS_GATEWAY_BINARY_PATH="$GROCERY_EATS_GATEWAY_PATH/yandex-taxi-grocery-eats-gateway"
elif [ -f "$GROCERY_EATS_GATEWAY_ARCADIA_PATH/yandex-taxi-grocery-eats-gateway" ]; then
  GROCERY_EATS_GATEWAY_BINARY_PATH="$GROCERY_EATS_GATEWAY_ARCADIA_PATH/yandex-taxi-grocery-eats-gateway"
fi

if [ -f "$GROCERY_EATS_GATEWAY_BINARY_PATH" ]; then
    echo "grocery-eats-gateway update package"
    mkdir -p /etc/yandex/taxi/grocery-eats-gateway/
    rm -rf /etc/yandex/taxi/grocery-eats-gateway/*

    ln -s $GROCERY_EATS_GATEWAY_PATH/configs/* /etc/yandex/taxi/grocery-eats-gateway/
    cp $GROCERY_EATS_GATEWAY_PATH/config.yaml /etc/yandex/taxi/grocery-eats-gateway/
    ln -s $GROCERY_EATS_GATEWAY_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-eats-gateway/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-eats-gateway/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-eats-gateway/config_vars.yaml

    ln -sf $GROCERY_EATS_GATEWAY_DEB_PATH/yandex-taxi-grocery-eats-gateway.nginx /etc/nginx/sites-available/yandex-taxi-grocery-eats-gateway
    ln -sf $GROCERY_EATS_GATEWAY_DEB_PATH/yandex-taxi-grocery-eats-gateway.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_EATS_GATEWAY_PATH/taxi-grocery-eats-gateway-stats.py /usr/bin/
    ln -sf $GROCERY_EATS_GATEWAY_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-eats-gateway/
mkdir -p /var/lib/yandex/taxi-grocery-eats-gateway/
mkdir -p /var/lib/yandex/taxi-grocery-eats-gateway/private/
mkdir -p /var/cache/yandex/taxi-grocery-eats-gateway/
ln -sf /taxi/logs/application-taxi-grocery-eats-gateway.log /var/log/yandex/taxi-grocery-eats-gateway/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-eats-gateway \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-eats-gateway/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-eats-gateway \
        --config /etc/yandex/taxi/grocery-eats-gateway/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-eats-gateway/server.log
