#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_PRODUCTS_PATH=$USERVICES_PATH/build-integration/services/grocery-products
GROCERY_PRODUCTS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-products
GROCERY_PRODUCTS_DEB_PATH=$USERVICES_PATH/services/grocery-products/debian

GROCERY_PRODUCTS_BINARY_PATH=
if [ -f "$GROCERY_PRODUCTS_PATH/yandex-taxi-grocery-products" ]; then
  GROCERY_PRODUCTS_BINARY_PATH="$GROCERY_PRODUCTS_PATH/yandex-taxi-grocery-products"
elif [ -f "$GROCERY_PRODUCTS_ARCADIA_PATH/yandex-taxi-grocery-products" ]; then
  GROCERY_PRODUCTS_BINARY_PATH="$GROCERY_PRODUCTS_ARCADIA_PATH/yandex-taxi-grocery-products"
fi

if [ -f "$GROCERY_PRODUCTS_BINARY_PATH" ]; then
    echo "grocery-products update package"
    mkdir -p /etc/yandex/taxi/grocery-products/
    rm -rf /etc/yandex/taxi/grocery-products/*

    ln -s $GROCERY_PRODUCTS_PATH/configs/* /etc/yandex/taxi/grocery-products/
    cp $GROCERY_PRODUCTS_PATH/config.yaml /etc/yandex/taxi/grocery-products/
    ln -s $GROCERY_PRODUCTS_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-products/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-products/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-products/config_vars.yaml

    ln -sf $GROCERY_PRODUCTS_DEB_PATH/yandex-taxi-grocery-products.nginx /etc/nginx/sites-available/yandex-taxi-grocery-products
    ln -sf $GROCERY_PRODUCTS_DEB_PATH/yandex-taxi-grocery-products.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_PRODUCTS_PATH/taxi-grocery-products-stats.py /usr/bin/
    echo "using binary: $GROCERY_PRODUCTS_BINARY_PATH"
    ln -sf $GROCERY_PRODUCTS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-products/
mkdir -p /var/lib/yandex/taxi-grocery-products/
mkdir -p /var/lib/yandex/taxi-grocery-products/private/
mkdir -p /var/cache/yandex/taxi-grocery-products/
ln -sf /taxi/logs/application-taxi-grocery-products.log /var/log/yandex/taxi-grocery-products/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-products \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-products/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-products \
        --config /etc/yandex/taxi/grocery-products/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-products/server.log
