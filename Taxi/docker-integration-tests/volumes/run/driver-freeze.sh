#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
DRIVER_FREEZE_PATH=$USERVICES_PATH/build-integration/services/driver-freeze
DRIVER_FREEZE_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/driver-freeze
DRIVER_FREEZE_DEB_PATH=$USERVICES_PATH/services/driver-freeze/debian

DRIVER_FREEZE_BINARY_PATH=
if [ -f "$DRIVER_FREEZE_PATH/yandex-taxi-driver-freeze" ]; then
  DRIVER_FREEZE_BINARY_PATH="$DRIVER_FREEZE_PATH/yandex-taxi-driver-freeze"
elif [ -f "$DRIVER_FREEZE_ARCADIA_PATH/yandex-taxi-driver-freeze" ]; then
  DRIVER_FREEZE_BINARY_PATH="$DRIVER_FREEZE_ARCADIA_PATH/yandex-taxi-driver-freeze"
fi

if [ -f "$DRIVER_FREEZE_BINARY_PATH" ]; then
    echo "driver-freeze update package"
    mkdir -p /etc/yandex/taxi/driver-freeze/
    rm -rf /etc/yandex/taxi/driver-freeze/*
    ln -s $DRIVER_FREEZE_PATH/configs/* /etc/yandex/taxi/driver-freeze/
    cp $DRIVER_FREEZE_PATH/config.yaml /etc/yandex/taxi/driver-freeze/
    ln -s $DRIVER_FREEZE_PATH/taxi_config_fallback.json /etc/yandex/taxi/driver-freeze/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/driver-freeze/
    ln -s config_vars.production.yaml /etc/yandex/taxi/driver-freeze/config_vars.yaml

    ln -sf $DRIVER_FREEZE_DEB_PATH/yandex-taxi-driver-freeze.nginx /etc/nginx/sites-available/yandex-taxi-driver-freeze
    ln -sf $DRIVER_FREEZE_DEB_PATH/yandex-taxi-driver-freeze.upstream_list /etc/nginx/conf.d/

    ln -sf $DRIVER_FREEZE_PATH/taxi-driver-freeze-stats.py /usr/bin/

    echo "using binary: $DRIVER_FREEZE_BINARY_PATH"
    ln -sf $DRIVER_FREEZE_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-driver-freeze/
mkdir -p /var/log/yandex/taxi-driver-freeze/
ln -sf /taxi/logs/application-taxi-driver-freeze.log /var/log/yandex/taxi-driver-freeze/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-driver-freeze \
    --fix-userver-client-timeout /etc/yandex/taxi/driver-freeze/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-driver-freeze \
        --config /etc/yandex/taxi/driver-freeze/config.yaml \
        --init-log /var/log/yandex/taxi-driver-freeze/server.log
