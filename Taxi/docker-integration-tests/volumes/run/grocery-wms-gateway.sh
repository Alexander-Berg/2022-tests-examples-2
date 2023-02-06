#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_WMS_GATEWAY_PATH=$USERVICES_PATH/build-integration/services/grocery-wms-gateway
GROCERY_WMS_GATEWAY_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-wms-gateway
GROCERY_WMS_GATEWAY_DEB_PATH=$USERVICES_PATH/services/grocery-wms-gateway/debian

GROCERY_WMS_GATEWAY_BINARY_PATH=
if [ -f "$GROCERY_WMS_GATEWAY_PATH/yandex-taxi-grocery-wms-gateway" ]; then
  GROCERY_WMS_GATEWAY_BINARY_PATH="$GROCERY_WMS_GATEWAY_PATH/yandex-taxi-grocery-wms-gateway"
elif [ -f "$GROCERY_WMS_GATEWAY_ARCADIA_PATH/yandex-taxi-grocery-wms-gateway" ]; then
  GROCERY_WMS_GATEWAY_BINARY_PATH="$GROCERY_WMS_GATEWAY_ARCADIA_PATH/yandex-taxi-grocery-wms-gateway"
fi

if [ -f "$GROCERY_WMS_GATEWAY_BINARY_PATH" ]; then
    echo "grocery-wms-gateway update package"
    mkdir -p /etc/yandex/taxi/grocery-wms-gateway/
    rm -rf /etc/yandex/taxi/grocery-wms-gateway/*

    ln -s $GROCERY_WMS_GATEWAY_PATH/configs/* /etc/yandex/taxi/grocery-wms-gateway/
    cp $GROCERY_WMS_GATEWAY_PATH/config.yaml /etc/yandex/taxi/grocery-wms-gateway/
    ln -s $GROCERY_WMS_GATEWAY_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-wms-gateway/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-wms-gateway/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-wms-gateway/config_vars.yaml

    ln -sf $GROCERY_WMS_GATEWAY_DEB_PATH/yandex-taxi-grocery-wms-gateway.nginx /etc/nginx/sites-available/yandex-taxi-grocery-wms-gateway
    ln -sf $GROCERY_WMS_GATEWAY_DEB_PATH/yandex-taxi-grocery-wms-gateway.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_WMS_GATEWAY_PATH/taxi-grocery-wms-gateway-stats.py /usr/bin/
    echo "using binary: $GROCERY_WMS_GATEWAY_BINARY_PATH"
    ln -sf $GROCERY_WMS_GATEWAY_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-wms-gateway/
mkdir -p /var/lib/yandex/taxi-grocery-wms-gateway/
mkdir -p /var/lib/yandex/taxi-grocery-wms-gateway/private/
mkdir -p /var/cache/yandex/taxi-grocery-wms-gateway/
ln -sf /taxi/logs/application-taxi-grocery-wms-gateway.log /var/log/yandex/taxi-grocery-wms-gateway/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-wms-gateway \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-wms-gateway/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-wms-gateway \
        --config /etc/yandex/taxi/grocery-wms-gateway/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-wms-gateway/server.log
