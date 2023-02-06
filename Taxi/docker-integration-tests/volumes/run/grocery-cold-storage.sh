#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_COLD_STORAGE_PATH=$USERVICES_PATH/build-integration/services/grocery-cold-storage
GROCERY_COLD_STORAGE_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-cold-storage
GROCERY_COLD_STORAGE_DEB_PATH=$USERVICES_PATH/services/grocery-cold-storage/debian

GROCERY_COLD_STORAGE_BINARY_PATH=
if [ -f "$GROCERY_COLD_STORAGE_PATH/yandex-taxi-grocery-cold-storage" ]; then
  GROCERY_COLD_STORAGE_BINARY_PATH="$GROCERY_COLD_STORAGE_PATH/yandex-taxi-grocery-cold-storage"
elif [ -f "$GROCERY_COLD_STORAGE_ARCADIA_PATH/yandex-taxi-grocery-cold-storage" ]; then
  GROCERY_COLD_STORAGE_BINARY_PATH="$GROCERY_COLD_STORAGE_ARCADIA_PATH/yandex-taxi-grocery-cold-storage"
fi

if [ -f "$GROCERY_COLD_STORAGE_BINARY_PATH" ]; then
    echo "grocery-cold-storage update package"
    mkdir -p /etc/yandex/taxi/grocery-cold-storage/
    rm -rf /etc/yandex/taxi/grocery-cold-storage/*

    ln -s $GROCERY_COLD_STORAGE_PATH/configs/* /etc/yandex/taxi/grocery-cold-storage/
    cp $GROCERY_COLD_STORAGE_PATH/config.yaml /etc/yandex/taxi/grocery-cold-storage/
    ln -s $GROCERY_COLD_STORAGE_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-cold-storage/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-cold-storage/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-cold-storage/config_vars.yaml

    ln -sf $GROCERY_COLD_STORAGE_DEB_PATH/yandex-taxi-grocery-cold-storage.nginx /etc/nginx/sites-available/yandex-taxi-grocery-cold-storage
    ln -sf $GROCERY_COLD_STORAGE_DEB_PATH/yandex-taxi-grocery-cold-storage.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_COLD_STORAGE_PATH/taxi-grocery-cold-storage-stats.py /usr/bin/
    echo "using binary: $GROCERY_COLD_STORAGE_BINARY_PATH"
    ln -sf $GROCERY_COLD_STORAGE_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-cold-storage/
mkdir -p /var/lib/yandex/taxi-grocery-cold-storage/
mkdir -p /var/lib/yandex/taxi-grocery-cold-storage/private/
mkdir -p /var/cache/yandex/taxi-grocery-cold-storage/
ln -sf /taxi/logs/application-taxi-grocery-cold-storage.log /var/log/yandex/taxi-grocery-cold-storage/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-cold-storage \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-cold-storage/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-cold-storage \
        --config /etc/yandex/taxi/grocery-cold-storage/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-cold-storage/server.log
