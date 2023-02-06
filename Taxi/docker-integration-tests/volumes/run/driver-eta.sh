#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
DRIVER_ETA_PATH=$USERVICES_PATH/build-integration/services/driver-eta
DRIVER_ETA_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/driver-eta
DRIVER_ETA_DEB_PATH=$USERVICES_PATH/services/driver-eta/debian

DRIVER_ETA_BINARY_PATH=
if [ -f "$DRIVER_ETA_PATH/yandex-taxi-driver-eta" ]; then
  DRIVER_ETA_BINARY_PATH="$DRIVER_ETA_PATH/yandex-taxi-driver-eta"
elif [ -f "$DRIVER_ETA_ARCADIA_PATH/yandex-taxi-driver-eta" ]; then
  DRIVER_ETA_BINARY_PATH="$DRIVER_ETA_ARCADIA_PATH/yandex-taxi-driver-eta"
fi

if [ -f "$DRIVER_ETA_BINARY_PATH" ]; then
    echo "driver-eta update package"
    mkdir -p /etc/yandex/taxi/driver-eta/
    rm -rf /etc/yandex/taxi/driver-eta/*

    ln -s $DRIVER_ETA_PATH/configs/* /etc/yandex/taxi/driver-eta/
    cp $DRIVER_ETA_PATH/config.yaml /etc/yandex/taxi/driver-eta/
    ln -s $DRIVER_ETA_PATH/taxi_config_fallback.json /etc/yandex/taxi/driver-eta/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/driver-eta/
    ln -s config_vars.production.yaml /etc/yandex/taxi/driver-eta/config_vars.yaml

    ln -sf $DRIVER_ETA_DEB_PATH/yandex-taxi-driver-eta.nginx /etc/nginx/sites-available/yandex-taxi-driver-eta
    ln -sf $DRIVER_ETA_DEB_PATH/yandex-taxi-driver-eta.upstream_list /etc/nginx/conf.d/

    ln -sf $DRIVER_ETA_PATH/taxi-driver-eta-stats.py /usr/bin/

    echo "using binary: $DRIVER_ETA_BINARY_PATH"
    ln -sf $DRIVER_ETA_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-driver-eta/
mkdir -p /var/lib/yandex/taxi-driver-eta/
mkdir -p /var/lib/yandex/taxi-driver-eta/private/
mkdir -p /var/cache/yandex/taxi-driver-eta/
ln -sf /taxi/logs/application-taxi-driver-eta.log /var/log/yandex/taxi-driver-eta/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-driver-eta \
    --fix-userver-client-timeout /etc/yandex/taxi/driver-eta/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-driver-eta \
        --config /etc/yandex/taxi/driver-eta/config.yaml \
        --init-log /var/log/yandex/taxi-driver-eta/server.log
