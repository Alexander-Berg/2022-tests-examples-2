#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
USER_API_PATH=$USERVICES_PATH/build-integration/services/user-api
USER_API_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/user-api
USER_API_DEB_PATH=$USERVICES_PATH/services/user-api/debian

USER_API_BINARY_PATH=
if [ -f "$USER_API_PATH/yandex-taxi-user-api" ]; then
  USER_API_BINARY_PATH="$USER_API_PATH/yandex-taxi-user-api"
elif [ -f "$USER_API_ARCADIA_PATH/yandex-taxi-user-api" ]; then
  USER_API_BINARY_PATH="$USER_API_ARCADIA_PATH/yandex-taxi-user-api"
fi

if [ -f "$USER_API_BINARY_PATH" ]; then
    echo "user-api update package"
    mkdir -p /etc/yandex/taxi/user-api/
    rm -rf /etc/yandex/taxi/user-api/*
    ln -s $USER_API_PATH/configs/* /etc/yandex/taxi/user-api/
    cp $USER_API_PATH/config.yaml /etc/yandex/taxi/user-api/
    ln -s $USER_API_PATH/taxi_config_fallback.json /etc/yandex/taxi/user-api/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/user-api/
    ln -s config_vars.production.yaml /etc/yandex/taxi/user-api/config_vars.yaml

    ln -sf $USER_API_DEB_PATH/yandex-taxi-user-api.nginx /etc/nginx/sites-available/yandex-taxi-user-api
    ln -sf $USER_API_DEB_PATH/yandex-taxi-user-api.upstream_list /etc/nginx/conf.d/

    ln -sf $USER_API_PATH/taxi-user-api-stats.py /usr/bin/

    echo "using binary: $USER_API_BINARY_PATH"
    ln -sf $USER_API_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-user-api/
mkdir -p /var/log/yandex/taxi-user-api/
ln -sf /taxi/logs/application-taxi-user-api.log /var/log/yandex/taxi-user-api/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-user-api \
    --fix-userver-client-timeout /etc/yandex/taxi/user-api/config.yaml \
    --wait \
       mongo.taxi.yandex:27017 \
       http://configs.taxi.yandex.net/ping \
    --run /usr/bin/yandex-taxi-user-api \
        --config /etc/yandex/taxi/user-api/config.yaml \
        --init-log /var/log/yandex/taxi-user-api/server.log
