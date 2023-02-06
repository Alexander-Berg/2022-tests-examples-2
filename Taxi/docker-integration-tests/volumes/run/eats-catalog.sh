#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
EATS_CATALOG_PATH=$USERVICES_PATH/build-integration/services/eats-catalog
EATS_CATALOG_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/eats-catalog
EATS_CATALOG_DEB_PATH=$USERVICES_PATH/services/eats-catalog/debian

EATS_CATALOG_BINARY_PATH=
if [ -f "$EATS_CATALOG_PATH/yandex-taxi-eats-catalog" ]; then
  EATS_CATALOG_BINARY_PATH="$EATS_CATALOG_PATH/yandex-taxi-eats-catalog"
elif [ -f "$EATS_CATALOG_ARCADIA_PATH/yandex-taxi-eats-catalog" ]; then
  EATS_CATALOG_BINARY_PATH="$EATS_CATALOG_ARCADIA_PATH/yandex-taxi-eats-catalog"
fi

if [ -f "$EATS_CATALOG_BINARY_PATH" ]; then
    echo "eats-catalog update package"
    mkdir -p /etc/yandex/taxi/eats-catalog/
    rm -rf /etc/yandex/taxi/eats-catalog/*

    ln -s $EATS_CATALOG_PATH/units/eats-catalog/configs/* /etc/yandex/taxi/eats-catalog/
    cp $EATS_CATALOG_PATH/units/eats-catalog/config.yaml /etc/yandex/taxi/eats-catalog/
    ln -s $EATS_CATALOG_PATH/taxi_config_fallback.json /etc/yandex/taxi/eats-catalog/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/eats-catalog/
    ln -s config_vars.production.yaml /etc/yandex/taxi/eats-catalog/config_vars.yaml

    ln -sf $EATS_CATALOG_DEB_PATH/yandex-taxi-eats-catalog.nginx /etc/nginx/sites-available/yandex-taxi-eats-catalog
    ln -sf $EATS_CATALOG_DEB_PATH/yandex-taxi-eats-catalog.upstream_list /etc/nginx/conf.d/

    ln -sf $EATS_CATALOG_PATH/taxi-eats-catalog-stats.py /usr/bin/
    echo "using binary: $EATS_CATALOG_BINARY_PATH"
    ln -sf $EATS_CATALOG_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-eats-catalog/
mkdir -p /var/lib/yandex/taxi-eats-catalog/
mkdir -p /var/lib/yandex/taxi-eats-catalog/private/
mkdir -p /var/cache/yandex/taxi-eats-catalog/
ln -sf /taxi/logs/application-taxi-eats-catalog.log /var/log/yandex/taxi-eats-catalog/server.log

/taxi/update_service_config_by_key.py \
    --config /etc/yandex/taxi/eats-catalog/config.yaml \
    --path components_manager.components.eats-catalog-storage-places-cache.update-interval \
    --value 1s

/taxi/update_service_config_by_key.py \
    --config /etc/yandex/taxi/eats-catalog/config.yaml \
    --path components_manager.components.eats-catalog-storage-zones-cache.update-interval \
    --value 1s

/taxi/tools/run.py \
    --nginx yandex-taxi-eats-catalog \
    --fix-userver-client-timeout /etc/yandex/taxi/eats-catalog/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-eats-catalog \
        --config /etc/yandex/taxi/eats-catalog/config.yaml \
        --init-log /var/log/yandex/taxi-eats-catalog/server.log
