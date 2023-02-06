#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
EATS_CATALOG_STORAGE_PATH=$USERVICES_PATH/build-integration/services/eats-catalog-storage
EATS_CATALOG_STORAGE_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/eats-catalog-storage
EATS_CATALOG_STORAGE_DEB_PATH=$USERVICES_PATH/services/eats-catalog-storage/debian

EATS_CATALOG_STORAGE_BINARY_PATH=
if [ -f "$EATS_CATALOG_STORAGE_PATH/yandex-taxi-eats-catalog-storage" ]; then
  EATS_CATALOG_STORAGE_BINARY_PATH="$EATS_CATALOG_STORAGE_PATH/yandex-taxi-eats-catalog-storage"
elif [ -f "$EATS_CATALOG_STORAGE_ARCADIA_PATH/yandex-taxi-eats-catalog-storage" ]; then
  EATS_CATALOG_STORAGE_BINARY_PATH="$EATS_CATALOG_STORAGE_ARCADIA_PATH/yandex-taxi-eats-catalog-storage"
fi

if [ -f "$EATS_CATALOG_STORAGE_BINARY_PATH" ]; then
    echo "eats-catalog-storage update package"
    mkdir -p /etc/yandex/taxi/eats-catalog-storage/
    rm -rf /etc/yandex/taxi/eats-catalog-storage/*

    ln -s $EATS_CATALOG_STORAGE_PATH/configs/* /etc/yandex/taxi/eats-catalog-storage/
    cp $EATS_CATALOG_STORAGE_PATH/config.yaml /etc/yandex/taxi/eats-catalog-storage/
    ln -s $EATS_CATALOG_STORAGE_PATH/taxi_config_fallback.json /etc/yandex/taxi/eats-catalog-storage/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/eats-catalog-storage/
    ln -s config_vars.production.yaml /etc/yandex/taxi/eats-catalog-storage/config_vars.yaml

    ln -sf $EATS_CATALOG_STORAGE_DEB_PATH/yandex-taxi-eats-catalog-storage.nginx /etc/nginx/sites-available/yandex-taxi-eats-catalog-storage
    ln -sf $EATS_CATALOG_STORAGE_DEB_PATH/yandex-taxi-eats-catalog-storage.upstream_list /etc/nginx/conf.d/

    ln -sf $EATS_CATALOG_STORAGE_PATH/taxi-eats-catalog-storage-stats.py /usr/bin/
    echo "using binary: $EATS_CATALOG_STORAGE_BINARY_PATH"
    ln -sf $EATS_CATALOG_STORAGE_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-eats-catalog-storage/
mkdir -p /var/lib/yandex/taxi-eats-catalog-storage/
mkdir -p /var/lib/yandex/taxi-eats-catalog-storage/private/
mkdir -p /var/cache/yandex/taxi-eats-catalog-storage/
ln -sf /taxi/logs/application-taxi-eats-catalog-storage.log /var/log/yandex/taxi-eats-catalog-storage/server.log

for cache in place-pg-cache delivery-zone-pg-cache; do
    for metric in update-interval full-update-interval update-jitter; do
        /taxi/update_service_config_by_key.py \
	    --config /etc/yandex/taxi/eats-catalog-storage/config.yaml \
	    --path components_manager.components.$cache.$metric \
	    --value 1s
	done
done

/taxi/tools/run.py \
    --nginx yandex-taxi-eats-catalog-storage \
    --fix-userver-client-timeout /etc/yandex/taxi/eats-catalog-storage/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-eats-catalog-storage \
        --config /etc/yandex/taxi/eats-catalog-storage/config.yaml \
        --init-log /var/log/yandex/taxi-eats-catalog-storage/server.log
