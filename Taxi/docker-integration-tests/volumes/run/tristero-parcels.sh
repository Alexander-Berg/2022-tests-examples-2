#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
TRISTERO_PARCELS_PATH=$USERVICES_PATH/build-integration/services/tristero-parcels
TRISTERO_PARCELS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/tristero-parcels
TRISTERO_PARCELS_DEB_PATH=$USERVICES_PATH/services/tristero-parcels/debian

TRISTERO_PARCELS_BINARY_PATH=
if [ -f "$TRISTERO_PARCELS_PATH/yandex-taxi-tristero-parcels" ]; then
  TRISTERO_PARCELS_BINARY_PATH="$TRISTERO_PARCELS_PATH/yandex-taxi-tristero-parcels"
elif [ -f "$TRISTERO_PARCELS_ARCADIA_PATH/yandex-taxi-tristero-parcels" ]; then
  TRISTERO_PARCELS_BINARY_PATH="$TRISTERO_PARCELS_ARCADIA_PATH/yandex-taxi-tristero-parcels"
fi

if [ -f "$TRISTERO_PARCELS_BINARY_PATH" ]; then
    echo "tristero-parcels update package"
    mkdir -p /etc/yandex/taxi/tristero-parcels/
    rm -rf /etc/yandex/taxi/tristero-parcels/*

    ln -s $TRISTERO_PARCELS_PATH/configs/* /etc/yandex/taxi/tristero-parcels/
    cp $TRISTERO_PARCELS_PATH/config.yaml /etc/yandex/taxi/tristero-parcels/
    ln -s $TRISTERO_PARCELS_PATH/taxi_config_fallback.json /etc/yandex/taxi/tristero-parcels/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/tristero-parcels/
    ln -s config_vars.production.yaml /etc/yandex/taxi/tristero-parcels/config_vars.yaml

    ln -sf $TRISTERO_PARCELS_DEB_PATH/yandex-taxi-tristero-parcels.nginx /etc/nginx/sites-available/yandex-taxi-tristero-parcels
    ln -sf $TRISTERO_PARCELS_DEB_PATH/yandex-taxi-tristero-parcels.upstream_list /etc/nginx/conf.d/

    ln -sf $TRISTERO_PARCELS_PATH/taxi-tristero-parcels-stats.py /usr/bin/
    echo "using binary: $TRISTERO_PARCELS_BINARY_PATH"
    ln -sf $TRISTERO_PARCELS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-tristero-parcels/
mkdir -p /var/lib/yandex/taxi-tristero-parcels/
mkdir -p /var/lib/yandex/taxi-tristero-parcels/private/
mkdir -p /var/cache/yandex/taxi-tristero-parcels/
ln -sf /taxi/logs/application-taxi-tristero-parcels.log /var/log/yandex/taxi-tristero-parcels/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-tristero-parcels \
    --fix-userver-client-timeout /etc/yandex/taxi/tristero-parcels/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-tristero-parcels \
        --config /etc/yandex/taxi/tristero-parcels/config.yaml \
        --init-log /var/log/yandex/taxi-tristero-parcels/server.log
