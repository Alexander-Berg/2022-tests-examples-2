#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
EATS_CART_PATH=$USERVICES_PATH/build-integration/services/eats-cart
EATS_CART_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/eats-cart
EATS_CART_DEB_PATH=$USERVICES_PATH/services/eats-cart/debian

EATS_CART_BINARY_PATH=
if [ -f "$EATS_CART_PATH/yandex-taxi-eats-cart" ]; then
  EATS_CART_BINARY_PATH="$EATS_CART_PATH/yandex-taxi-eats-cart"
elif [ -f "$EATS_CART_ARCADIA_PATH/yandex-taxi-eats-cart" ]; then
  EATS_CART_BINARY_PATH="$EATS_CART_ARCADIA_PATH/yandex-taxi-eats-cart"
fi

if [ -f "$EATS_CART_BINARY_PATH" ]; then
    echo "eats-cart update package"
    mkdir -p /etc/yandex/taxi/eats-cart/
    rm -rf /etc/yandex/taxi/eats-cart/*

    ln -s $EATS_CART_PATH/configs/* /etc/yandex/taxi/eats-cart/
    cp $EATS_CART_PATH/config.yaml /etc/yandex/taxi/eats-cart/
    ln -s $EATS_CART_PATH/taxi_config_fallback.json /etc/yandex/taxi/eats-cart/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/eats-cart/
    ln -s config_vars.production.yaml /etc/yandex/taxi/eats-cart/config_vars.yaml

    ln -sf $EATS_CART_DEB_PATH/yandex-taxi-eats-cart.nginx /etc/nginx/sites-available/yandex-taxi-eats-cart
    ln -sf $EATS_CART_DEB_PATH/yandex-taxi-eats-cart.upstream_list /etc/nginx/conf.d/

    ln -sf $EATS_CART_PATH/taxi-eats-cart-stats.py /usr/bin/
    echo "using binary: $EATS_CART_BINARY_PATH"
    ln -sf $EATS_CART_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-eats-cart/
mkdir -p /var/lib/yandex/taxi-eats-cart/
mkdir -p /var/lib/yandex/taxi-eats-cart/private/
mkdir -p /var/cache/yandex/taxi-eats-cart/
ln -sf /taxi/logs/application-taxi-eats-cart.log /var/log/yandex/taxi-eats-cart/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-eats-cart \
    --fix-userver-client-timeout /etc/yandex/taxi/eats-cart/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-eats-cart \
        --config /etc/yandex/taxi/eats-cart/config.yaml \
        --init-log /var/log/yandex/taxi-eats-cart/server.log
