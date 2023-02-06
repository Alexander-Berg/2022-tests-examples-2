#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
OVERLORD_CATALOG_PATH=$USERVICES_PATH/build-integration/services/overlord-catalog
OVERLORD_CATALOG_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/overlord-catalog
OVERLORD_CATALOG_DEB_PATH=$USERVICES_PATH/services/overlord-catalog/debian

OVERLORD_CATALOG_BINARY_PATH=
if [ -f "$OVERLORD_CATALOG_PATH/yandex-taxi-overlord-catalog" ]; then
  OVERLORD_CATALOG_BINARY_PATH="$OVERLORD_CATALOG_PATH/yandex-taxi-overlord-catalog"
elif [ -f "$OVERLORD_CATALOG_ARCADIA_PATH/yandex-taxi-overlord-catalog" ]; then
  OVERLORD_CATALOG_BINARY_PATH="$OVERLORD_CATALOG_ARCADIA_PATH/yandex-taxi-overlord-catalog"
fi

if [ -f "$OVERLORD_CATALOG_BINARY_PATH" ]; then
    echo "overlord-catalog update package"
    mkdir -p /etc/yandex/taxi/overlord-catalog/
    rm -rf /etc/yandex/taxi/overlord-catalog/*

    ln -s $OVERLORD_CATALOG_PATH/configs/* /etc/yandex/taxi/overlord-catalog/
    ln -s $OVERLORD_CATALOG_PATH/config.yaml /etc/yandex/taxi/overlord-catalog/
    ln -s $OVERLORD_CATALOG_PATH/taxi_config_fallback.json /etc/yandex/taxi/overlord-catalog/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/overlord-catalog/
    ln -s config_vars.production.yaml /etc/yandex/taxi/overlord-catalog/config_vars.yaml

    ln -sf $OVERLORD_CATALOG_DEB_PATH/yandex-taxi-overlord-catalog.nginx /etc/nginx/sites-available/yandex-taxi-overlord-catalog
    ln -sf $OVERLORD_CATALOG_DEB_PATH/yandex-taxi-overlord-catalog.upstream_list /etc/nginx/conf.d/

    ln -sf $OVERLORD_CATALOG_PATH/taxi-overlord-catalog-stats.py /usr/bin/
    echo "using binary: $OVERLORD_CATALOG_BINARY_PATH"
    ln -sf $OVERLORD_CATALOG_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-overlord-catalog/
mkdir -p /var/lib/yandex/taxi-overlord-catalog/
mkdir -p /var/lib/yandex/taxi-overlord-catalog/private/
mkdir -p /var/cache/yandex/taxi-overlord-catalog/
ln -sf /taxi/logs/application-taxi-overlord-catalog.log /var/log/yandex/taxi-overlord-catalog/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-overlord-catalog \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-overlord-catalog \
        --config /etc/yandex/taxi/overlord-catalog/config.yaml \
        --init-log /var/log/yandex/taxi-overlord-catalog/server.log
