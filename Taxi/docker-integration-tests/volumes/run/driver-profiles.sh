#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
DRIVER_PROFILES_PATH=$USERVICES_PATH/build-integration/services/driver-profiles
DRIVER_PROFILES_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/driver-profiles
DRIVER_PROFILES_DEB_PATH=$USERVICES_PATH/services/driver-profiles/debian

DRIVER_PROFILES_BINARY_PATH=
if [ -f "$DRIVER_PROFILES_PATH/yandex-taxi-driver-profiles" ]; then
  DRIVER_PROFILES_BINARY_PATH="$DRIVER_PROFILES_PATH/yandex-taxi-driver-profiles"
elif [ -f "$DRIVER_PROFILES_ARCADIA_PATH/yandex-taxi-driver-profiles" ]; then
  DRIVER_PROFILES_BINARY_PATH="$DRIVER_PROFILES_ARCADIA_PATH/yandex-taxi-driver-profiles"
fi

if [ -f "$DRIVER_PROFILES_BINARY_PATH" ]; then
    echo "driver-profiles update package"
    mkdir -p /etc/yandex/taxi/driver-profiles/
    mkdir -p /var/cache/yandex/taxi-driver-profiles/
    rm -rf /etc/yandex/taxi/driver-profiles/*
    ln -s $DRIVER_PROFILES_PATH/configs/* /etc/yandex/taxi/driver-profiles/
    cp $DRIVER_PROFILES_PATH/config.yaml /etc/yandex/taxi/driver-profiles/
    ln -s $DRIVER_PROFILES_PATH/taxi_config_fallback.json /etc/yandex/taxi/driver-profiles/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/driver-profiles/
    ln -s config_vars.production.yaml /etc/yandex/taxi/driver-profiles/config_vars.yaml

    ln -sf $DRIVER_PROFILES_DEB_PATH/yandex-taxi-driver-profiles.nginx /etc/nginx/sites-available/yandex-taxi-driver-profiles
    ln -sf $DRIVER_PROFILES_DEB_PATH/yandex-taxi-driver-profiles.upstream_list /etc/nginx/conf.d/

    ln -sf $DRIVER_PROFILES_PATH/taxi-driver-profiles-stats.py /usr/bin/

    echo "using binary: $DRIVER_PROFILES_BINARY_PATH"
    ln -sf $DRIVER_PROFILES_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-driver-profiles/
mkdir -p /var/log/yandex/taxi-driver-profiles/
ln -sf /taxi/logs/application-taxi-driver-profiles.log /var/log/yandex/taxi-driver-profiles/server.log

taxi-python3 /taxi/tools/run.py \
    --stdout-to-log \
    --nginx yandex-taxi-driver-profiles \
    --fix-userver-client-timeout /etc/yandex/taxi/driver-profiles/config.yaml \
    --syslog \
    --wait \
        postgresql:driver_profiles \
        mongo.taxi.yandex:27017 \
        http://configs.taxi.yandex.net/ping \
    --run /usr/bin/yandex-taxi-driver-profiles \
        --config /etc/yandex/taxi/driver-profiles/config.yaml \
        --init-log /taxi/logs/application-taxi-driver-profiles-init.log
