#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
UNIQUE_DRIVERS_PATH=$USERVICES_PATH/build-integration/services/unique-drivers
UNIQUE_DRIVERS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/unique-drivers
UNIQUE_DRIVERS_DEB_PATH=$USERVICES_PATH/services/unique-drivers/debian

UNIQUE_DRIVERS_BINARY_PATH=
if [ -f "$UNIQUE_DRIVERS_PATH/yandex-taxi-unique-drivers" ]; then
  UNIQUE_DRIVERS_BINARY_PATH="$UNIQUE_DRIVERS_PATH/yandex-taxi-unique-drivers"
elif [ -f "$UNIQUE_DRIVERS_ARCADIA_PATH/yandex-taxi-unique-drivers" ]; then
  UNIQUE_DRIVERS_BINARY_PATH="$UNIQUE_DRIVERS_ARCADIA_PATH/yandex-taxi-unique-drivers"
fi

if [ -f "$UNIQUE_DRIVERS_BINARY_PATH" ]; then
    echo "unique-drivers update package"
    mkdir -p /etc/yandex/taxi/unique-drivers/
    mkdir -p /var/cache/yandex/taxi-unique-drivers/
    rm -rf /etc/yandex/taxi/unique-drivers/*
    ln -s $UNIQUE_DRIVERS_PATH/configs/* /etc/yandex/taxi/unique-drivers/
    cp $UNIQUE_DRIVERS_PATH/config.yaml /etc/yandex/taxi/unique-drivers/
    ln -s $UNIQUE_DRIVERS_PATH/taxi_config_fallback.json /etc/yandex/taxi/unique-drivers/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/unique-drivers/
    ln -s config_vars.production.yaml /etc/yandex/taxi/unique-drivers/config_vars.yaml

    ln -sf $UNIQUE_DRIVERS_DEB_PATH/yandex-taxi-unique-drivers.nginx /etc/nginx/sites-available/yandex-taxi-unique-drivers
    ln -sf $UNIQUE_DRIVERS_DEB_PATH/yandex-taxi-unique-drivers.upstream_list /etc/nginx/conf.d/

    ln -sf $UNIQUE_DRIVERS_PATH/taxi-unique-drivers-stats.py /usr/bin/

    echo "using binary: $UNIQUE_DRIVERS_BINARY_PATH"
    ln -sf $UNIQUE_DRIVERS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-unique-drivers/
mkdir -p /var/log/yandex/taxi-unique-drivers/
ln -sf /taxi/logs/application-taxi-unique-drivers.log /var/log/yandex/taxi-unique-drivers/server.log

/usr/lib/yandex/taxi-py3-2/bin/python3.7 /taxi/tools/run.py \
    --stdout-to-log \
    --nginx yandex-taxi-unique-drivers \
    --fix-userver-client-timeout /etc/yandex/taxi/unique-drivers/config.yaml \
    --syslog \
    --wait \
        postgresql:unique_drivers \
        mongo.taxi.yandex:27017 \
        http://configs.taxi.yandex.net/ping \
        http://personal.taxi.yandex.net/ping \
        http://driver-profiles.taxi.yandex.net/ping \
    --run /usr/bin/yandex-taxi-unique-drivers \
        --config /etc/yandex/taxi/unique-drivers/config.yaml \
        --init-log /taxi/logs/application-taxi-unique-drivers-init.log
