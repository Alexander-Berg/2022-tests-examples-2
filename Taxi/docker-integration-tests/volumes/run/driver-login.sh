#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
DRIVER_LOGIN_PATH=$USERVICES_PATH/build-integration/services/driver-login
DRIVER_LOGIN_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/driver-login
DRIVER_LOGIN_DEB_PATH=$USERVICES_PATH/services/driver-login/debian

DRIVER_LOGIN_BINARY_PATH=
if [ -f "$DRIVER_LOGIN_PATH/yandex-taxi-driver-login" ]; then
  DRIVER_LOGIN_BINARY_PATH="$DRIVER_LOGIN_PATH/yandex-taxi-driver-login"
elif [ -f "$DRIVER_LOGIN_ARCADIA_PATH/yandex-taxi-driver-login" ]; then
  DRIVER_LOGIN_BINARY_PATH="$DRIVER_LOGIN_ARCADIA_PATH/yandex-taxi-driver-login"
fi

if [ -f "$DRIVER_LOGIN_BINARY_PATH" ]; then
    echo "driver-login update package"
    mkdir -p /etc/yandex/taxi/driver-login/
    rm -rf /etc/yandex/taxi/driver-login/*

    ln -s $DRIVER_LOGIN_PATH/configs/* /etc/yandex/taxi/driver-login/
    cp $DRIVER_LOGIN_PATH/config.yaml /etc/yandex/taxi/driver-login/
    ln -s $DRIVER_LOGIN_PATH/taxi_config_fallback.json /etc/yandex/taxi/driver-login/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/driver-login/
    ln -s config_vars.production.yaml /etc/yandex/taxi/driver-login/config_vars.yaml

    ln -sf $DRIVER_LOGIN_DEB_PATH/yandex-taxi-driver-login.nginx /etc/nginx/sites-available/yandex-taxi-driver-login
    ln -sf $DRIVER_LOGIN_DEB_PATH/yandex-taxi-driver-login.upstream_list /etc/nginx/conf.d/

    ln -sf $DRIVER_LOGIN_PATH/taxi-driver-login-stats.py /usr/bin/

    echo "using binary: $DRIVER_LOGIN_BINARY_PATH"
    ln -sf $DRIVER_LOGIN_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-driver-login/
mkdir -p /var/log/yandex/taxi-driver-login/
mkdir -p /var/lib/yandex/taxi-driver-login/private/
mkdir -p /var/cache/yandex/taxi-driver-login/
ln -sf /taxi/logs/application-taxi-driver-login.log /var/log/yandex/taxi-driver-login/server.log

taxi-python3 /taxi/tools/run.py \
    --stdout-to-log \
    --nginx yandex-taxi-driver-login \
    --fix-userver-client-timeout /etc/yandex/taxi/driver-login/config.yaml \
    --syslog \
    --wait \
        postgresql:driver-login-db \
        mongo.taxi.yandex:27017 \
        redis.taxi.yandex:6379 \
        http://configs.taxi.yandex.net/ping \
    --run /usr/bin/yandex-taxi-driver-login \
        --config /etc/yandex/taxi/driver-login/config.yaml \
        --init-log /taxi/logs/application-taxi-driver-login-init.log
