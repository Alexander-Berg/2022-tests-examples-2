#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
API_PROXY_PATH=$USERVICES_PATH/build-integration/services/api-proxy
API_PROXY_PATH_UNIT=$USERVICES_PATH/build-integration/services/api-proxy/units/api-proxy/
API_PROXY_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/api-proxy
API_PROXY_DEB_PATH=$USERVICES_PATH/services/api-proxy/debian

API_PROXY_BINARY_PATH=
if [ -f "$API_PROXY_PATH/yandex-taxi-api-proxy" ]; then
  API_PROXY_BINARY_PATH="$API_PROXY_PATH/yandex-taxi-api-proxy"
elif [ -f "$API_PROXY_ARCADIA_PATH/yandex-taxi-api-proxy" ]; then
  API_PROXY_BINARY_PATH="$API_PROXY_ARCADIA_PATH/yandex-taxi-api-proxy"
fi

if [ -f "$API_PROXY_BINARY_PATH" ]; then
    echo "api-proxy update package"
    mkdir -p /etc/yandex/taxi/api-proxy/
    rm -rf /etc/yandex/taxi/api-proxy/*
    if [ -e $API_PROXY_PATH/config.yaml ]; then
        ln -s $API_PROXY_PATH/configs/* /etc/yandex/taxi/api-proxy/
        cp $API_PROXY_PATH/config.yaml /etc/yandex/taxi/api-proxy/
    else
        ln -s $API_PROXY_PATH_UNIT/configs/* /etc/yandex/taxi/api-proxy/
        cp $API_PROXY_PATH_UNIT/config.yaml /etc/yandex/taxi/api-proxy/
    fi
    ln -s $API_PROXY_PATH/taxi_config_fallback.json /etc/yandex/taxi/api-proxy/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/api-proxy/
    ln -s config_vars.production.yaml /etc/yandex/taxi/api-proxy/config_vars.yaml

    ln -sf $API_PROXY_DEB_PATH/yandex-taxi-api-proxy.nginx /etc/nginx/sites-available/yandex-taxi-api-proxy
    ln -sf $API_PROXY_DEB_PATH/yandex-taxi-api-proxy.upstream_list /etc/nginx/conf.d/

    ln -sf $API_PROXY_PATH/taxi-api-proxy-stats.py /usr/bin/

    echo "using binary: $API_PROXY_BINARY_PATH"
    ln -sf $API_PROXY_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-api-proxy/
mkdir -p /var/log/yandex/taxi-api-proxy/
ln -sf /taxi/logs/application-taxi-api-proxy.log /var/log/yandex/taxi-api-proxy/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-api-proxy \
    --fix-userver-client-timeout /etc/yandex/taxi/api-proxy/config.yaml \
    --run /usr/bin/yandex-taxi-api-proxy \
    --config /etc/yandex/taxi/api-proxy/config.yaml \
    --init-log /var/log/yandex/taxi-api-proxy/server.log
