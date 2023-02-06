#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_FAV_GOODS_PATH=$USERVICES_PATH/build-integration/services/grocery-fav-goods
GROCERY_FAV_GOODS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-fav-goods
GROCERY_FAV_GOODS_DEB_PATH=$USERVICES_PATH/services/grocery-fav-goods/debian

GROCERY_FAV_GOODS_BINARY_PATH=
if [ -f "$GROCERY_FAV_GOODS_PATH/yandex-taxi-grocery-fav-goods" ]; then
  GROCERY_FAV_GOODS_BINARY_PATH="$GROCERY_FAV_GOODS_PATH/yandex-taxi-grocery-fav-goods"
elif [ -f "$GROCERY_FAV_GOODS_ARCADIA_PATH/yandex-taxi-grocery-fav-goods" ]; then
  GROCERY_FAV_GOODS_BINARY_PATH="$GROCERY_FAV_GOODS_ARCADIA_PATH/yandex-taxi-grocery-fav-goods"
fi

if [ -f "$GROCERY_FAV_GOODS_BINARY_PATH" ]; then
    echo "grocery-fav-goods update package"
    mkdir -p /etc/yandex/taxi/grocery-fav-goods/
    rm -rf /etc/yandex/taxi/grocery-fav-goods/*

    ln -s $GROCERY_FAV_GOODS_PATH/configs/* /etc/yandex/taxi/grocery-fav-goods/
    cp $GROCERY_FAV_GOODS_PATH/config.yaml /etc/yandex/taxi/grocery-fav-goods/
    ln -s $GROCERY_FAV_GOODS_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-fav-goods/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-fav-goods/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-fav-goods/config_vars.yaml

    ln -sf $GROCERY_FAV_GOODS_DEB_PATH/yandex-taxi-grocery-fav-goods.nginx /etc/nginx/sites-available/yandex-taxi-grocery-fav-goods
    ln -sf $GROCERY_FAV_GOODS_DEB_PATH/yandex-taxi-grocery-fav-goods.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_FAV_GOODS_PATH/taxi-grocery-fav-goods-stats.py /usr/bin/
    echo "using binary: $GROCERY_FAV_GOODS_BINARY_PATH"
    ln -sf $GROCERY_FAV_GOODS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-fav-goods/
mkdir -p /var/lib/yandex/taxi-grocery-fav-goods/
mkdir -p /var/lib/yandex/taxi-grocery-fav-goods/private/
mkdir -p /var/cache/yandex/taxi-grocery-fav-goods/
ln -sf /taxi/logs/application-taxi-grocery-fav-goods.log /var/log/yandex/taxi-grocery-fav-goods/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-fav-goods \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-fav-goods/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-fav-goods \
        --config /etc/yandex/taxi/grocery-fav-goods/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-fav-goods/server.log
