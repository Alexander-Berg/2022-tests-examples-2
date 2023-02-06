#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
DRIVER_TRACKSTORY_PATH=$USERVICES_PATH/build-integration/services/driver-trackstory
DRIVER_TRACKSTORY_PATH_UNIT=$USERVICES_PATH/build-integration/services/driver-trackstory/units/driver-trackstory/
DRIVER_TRACKSTORY_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/driver-trackstory
DRIVER_TRACKSTORY_DEB_PATH=$USERVICES_PATH/services/driver-trackstory/debian

DRIVER_TRACKSTORY_BINARY_PATH=
if [ -f "$DRIVER_TRACKSTORY_PATH/yandex-taxi-driver-trackstory" ]; then
  DRIVER_TRACKSTORY_BINARY_PATH="$DRIVER_TRACKSTORY_PATH/yandex-taxi-driver-trackstory"
elif [ -f "$DRIVER_TRACKSTORY_ARCADIA_PATH/yandex-taxi-driver-trackstory" ]; then
  DRIVER_TRACKSTORY_BINARY_PATH="$DRIVER_TRACKSTORY_ARCADIA_PATH/yandex-taxi-driver-trackstory"
fi

if [ -f "$DRIVER_TRACKSTORY_BINARY_PATH" ]; then
    echo "driver-trackstory update package"
    mkdir -p /etc/yandex/taxi/driver-trackstory/
    rm -rf /etc/yandex/taxi/driver-trackstory/* ||:
    if [ -e $DRIVER_TRACKSTORY_PATH/config.yaml ]; then
        ln -s $DRIVER_TRACKSTORY_PATH/configs/* /etc/yandex/taxi/driver-trackstory/
        cp $DRIVER_TRACKSTORY_PATH/config.yaml /etc/yandex/taxi/driver-trackstory/
    else
        ln -s $DRIVER_TRACKSTORY_PATH_UNIT/configs/* /etc/yandex/taxi/driver-trackstory/
        cp $DRIVER_TRACKSTORY_PATH_UNIT/config.yaml /etc/yandex/taxi/driver-trackstory/
    fi
    ln -s $DRIVER_TRACKSTORY_PATH/taxi_config_fallback.json /etc/yandex/taxi/driver-trackstory/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/driver-trackstory/
    ln -s config_vars.production.yaml /etc/yandex/taxi/driver-trackstory/config_vars.yaml

    ln -sf $DRIVER_TRACKSTORY_DEB_PATH/yandex-taxi-driver-trackstory.nginx /etc/nginx/sites-available/yandex-taxi-driver-trackstory
    ln -sf $DRIVER_TRACKSTORY_DEB_PATH/yandex-taxi-driver-trackstory.upstream_list /etc/nginx/conf.d/

    ln -sf $DRIVER_TRACKSTORY_PATH/taxi-driver-trackstory-stats.py /usr/bin/

    echo "using binary: $DRIVER_TRACKSTORY_BINARY_PATH"
    ln -sf $DRIVER_TRACKSTORY_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-driver-trackstory/
mkdir -p /var/lib/yandex/taxi-driver-trackstory/
mkdir -p /var/lib/yandex/taxi-driver-trackstory/private/
mkdir -p /var/cache/yandex/taxi-driver-trackstory/
ln -sf /taxi/logs/application-taxi-driver-trackstory.log /var/log/yandex/taxi-driver-trackstory/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-driver-trackstory \
    --fix-userver-client-timeout /etc/yandex/taxi/driver-trackstory/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-driver-trackstory \
        --config /etc/yandex/taxi/driver-trackstory/config.yaml \
        --init-log /var/log/yandex/taxi-driver-trackstory/server.log

