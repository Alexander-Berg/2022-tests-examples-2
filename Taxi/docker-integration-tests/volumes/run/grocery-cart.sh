#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_CART_PATH=$USERVICES_PATH/build-integration/services/grocery-cart
GROCERY_CART_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-cart
GROCERY_CART_DEB_PATH=$USERVICES_PATH/services/grocery-cart/debian

GROCERY_CART_BINARY_PATH=
if [ -f "$GROCERY_CART_PATH/yandex-taxi-grocery-cart" ]; then
  GROCERY_CART_BINARY_PATH="$GROCERY_CART_PATH/yandex-taxi-grocery-cart"
elif [ -f "$GROCERY_CART_ARCADIA_PATH/yandex-taxi-grocery-cart" ]; then
  GROCERY_CART_BINARY_PATH="$GROCERY_CART_ARCADIA_PATH/yandex-taxi-grocery-cart"
fi

if [ -f "$GROCERY_CART_BINARY_PATH" ]; then
    echo "grocery-cart update package"
    mkdir -p /etc/yandex/taxi/grocery-cart/
    rm -rf /etc/yandex/taxi/grocery-cart/*

    ln -s $GROCERY_CART_PATH/configs/* /etc/yandex/taxi/grocery-cart/
    cp $GROCERY_CART_PATH/config.yaml /etc/yandex/taxi/grocery-cart/
    ln -s $GROCERY_CART_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-cart/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-cart/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-cart/config_vars.yaml

    ln -sf $GROCERY_CART_DEB_PATH/yandex-taxi-grocery-cart.nginx /etc/nginx/sites-available/yandex-taxi-grocery-cart
    ln -sf $GROCERY_CART_DEB_PATH/yandex-taxi-grocery-cart.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_CART_PATH/taxi-grocery-cart-stats.py /usr/bin/
    echo "using binary: $GROCERY_CART_BINARY_PATH"
    ln -sf $GROCERY_CART_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-cart/
mkdir -p /var/lib/yandex/taxi-grocery-cart/
mkdir -p /var/lib/yandex/taxi-grocery-cart/private/
mkdir -p /var/cache/yandex/taxi-grocery-cart/
ln -sf /taxi/logs/application-taxi-grocery-cart.log /var/log/yandex/taxi-grocery-cart/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-cart \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-cart/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-cart \
        --config /etc/yandex/taxi/grocery-cart/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-cart/server.log
