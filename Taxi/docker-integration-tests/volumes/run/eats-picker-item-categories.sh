#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
EATS_PICKER_ITEM_CATEGORIES_PATH=$USERVICES_PATH/build-integration/services/eats-picker-item-categories
EATS_PICKER_ITEM_CATEGORIES_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/eats-picker-item-categories
EATS_PICKER_ITEM_CATEGORIES_DEB_PATH=$USERVICES_PATH/services/eats-picker-item-categories/debian

EATS_PICKER_ITEM_CATEGORIES_BINARY_PATH=
if [ -f "$EATS_PICKER_ITEM_CATEGORIES_PATH/yandex-taxi-eats-picker-item-categories" ]; then
  EATS_PICKER_ITEM_CATEGORIES_BINARY_PATH="$EATS_PICKER_ITEM_CATEGORIES_PATH/yandex-taxi-eats-picker-item-categories"
elif [ -f "$EATS_PICKER_ITEM_CATEGORIES_ARCADIA_PATH/yandex-taxi-eats-picker-item-categories" ]; then
  EATS_PICKER_ITEM_CATEGORIES_BINARY_PATH="$EATS_PICKER_ITEM_CATEGORIES_ARCADIA_PATH/yandex-taxi-eats-picker-item-categories"
fi

if [ -f "$EATS_PICKER_ITEM_CATEGORIES_BINARY_PATH" ]; then
    echo "eats-picker-item-categories update package"
    mkdir -p /etc/yandex/taxi/eats-picker-item-categories/
    rm -rf /etc/yandex/taxi/eats-picker-item-categories/*

    ln -s $EATS_PICKER_ITEM_CATEGORIES_PATH/configs/* /etc/yandex/taxi/eats-picker-item-categories/
    cp $EATS_PICKER_ITEM_CATEGORIES_PATH/config.yaml /etc/yandex/taxi/eats-picker-item-categories/
    ln -s $EATS_PICKER_ITEM_CATEGORIES_PATH/taxi_config_fallback.json /etc/yandex/taxi/eats-picker-item-categories/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/eats-picker-item-categories/
    ln -s config_vars.production.yaml /etc/yandex/taxi/eats-picker-item-categories/config_vars.yaml

    ln -sf $EATS_PICKER_ITEM_CATEGORIES_DEB_PATH/yandex-taxi-eats-picker-item-categories.nginx /etc/nginx/sites-available/yandex-taxi-eats-picker-item-categories
    ln -sf $EATS_PICKER_ITEM_CATEGORIES_DEB_PATH/yandex-taxi-eats-picker-item-categories.upstream_list /etc/nginx/conf.d/

    ln -sf $EATS_PICKER_ITEM_CATEGORIES_PATH/taxi-eats-picker-item-categories-stats.py /usr/bin/
    echo "using binary: $EATS_PICKER_ITEM_CATEGORIES_BINARY_PATH"
    ln -sf $EATS_PICKER_ITEM_CATEGORIES_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-eats-picker-item-categories/
mkdir -p /var/lib/yandex/taxi-eats-picker-item-categories/
mkdir -p /var/lib/yandex/taxi-eats-picker-item-categories/private/
mkdir -p /var/cache/yandex/taxi-eats-picker-item-categories/
ln -sf /taxi/logs/application-taxi-eats-picker-item-categories.log /var/log/yandex/taxi-eats-picker-item-categories/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-eats-picker-item-categories \
    --fix-userver-client-timeout /etc/yandex/taxi/eats-picker-item-categories/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-eats-picker-item-categories \
        --config /etc/yandex/taxi/eats-picker-item-categories/config.yaml \
        --init-log /var/log/yandex/taxi-eats-picker-item-categories/server.log
