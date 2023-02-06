#!/usr/bin/env bash

set -e

USERVICES_PATH=/arcadia/taxi/uservices
DRIVER_AUTHPROXY_PATH=$USERVICES_PATH/build-integration/services/driver-authproxy
DRIVER_AUTHPROXY_PATH_UNIT=$USERVICES_PATH/build-integration/services/driver-authproxy/units/taximeter-proxy/
DRIVER_AUTHPROXY_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/driver-authproxy
DRIVER_AUTHPROXY_DEB_PATH=$USERVICES_PATH/services/driver-authproxy/debian
DRIVER_AUTHPROXY_NGINX_PATH=$USERVICES_PATH/services/driver-authproxy/nginx

DRIVER_AUTHPROXY_BINARY_PATH=
if [ -f "$DRIVER_AUTHPROXY_PATH/yandex-taxi-driver-authproxy" ]; then
  DRIVER_AUTHPROXY_BINARY_PATH="$DRIVER_AUTHPROXY_PATH/yandex-taxi-driver-authproxy"
elif [ -f "$DRIVER_AUTHPROXY_ARCADIA_PATH/yandex-taxi-driver-authproxy" ]; then
  DRIVER_AUTHPROXY_BINARY_PATH="$DRIVER_AUTHPROXY_ARCADIA_PATH/yandex-taxi-driver-authproxy"
fi

if [ -f "$DRIVER_AUTHPROXY_BINARY_PATH" ]; then
    echo "driver-authproxy update package"
    mkdir -p /etc/yandex/taxi/driver-authproxy/
    rm -rf /etc/yandex/taxi/driver-authproxy/* ||:
    if [ -e $DRIVER_AUTHPROXY_PATH/config.yaml ]; then
        ln -s $DRIVER_AUTHPROXY_PATH/configs/* /etc/yandex/taxi/driver-authproxy/
        cp $DRIVER_AUTHPROXY_PATH/config.yaml /etc/yandex/taxi/driver-authproxy/
    else
        ln -s $DRIVER_AUTHPROXY_PATH_UNIT/configs/* /etc/yandex/taxi/driver-authproxy/
        cp $DRIVER_AUTHPROXY_PATH_UNIT/config.yaml /etc/yandex/taxi/driver-authproxy/
    fi
    ln -s $DRIVER_AUTHPROXY_PATH/taxi_config_fallback.json /etc/yandex/taxi/driver-authproxy/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/driver-authproxy/
    ln -s config_vars.production.yaml /etc/yandex/taxi/driver-authproxy/config_vars.yaml

    ln -sf $DRIVER_AUTHPROXY_DEB_PATH/yandex-taxi-driver-authproxy.nginx /etc/nginx/sites-available/yandex-taxi-driver-authproxy
    if [ -e $DRIVER_AUTHPROXY_DEB_PATH/yandex-taxi-driver-authproxy.upstream_list ]; then
        cp $DRIVER_AUTHPROXY_DEB_PATH/yandex-taxi-driver-authproxy.upstream_list /etc/nginx/conf.d/
    else
        ln -sf $DRIVER_AUTHPROXY_NGINX_PATH/sites-testing/yandex-taxi-driver-authproxy /etc/nginx/sites-available/yandex-taxi-driver-authproxy
        cp $DRIVER_AUTHPROXY_NGINX_PATH/yandex-taxi-driver-authproxy.upstream_list /etc/nginx/conf.d/
    fi

    ln -sf $DRIVER_AUTHPROXY_PATH/taxi-driver-authproxy-stats.py /usr/bin/

    echo "using binary: $DRIVER_AUTHPROXY_BINARY_PATH"
    ln -sf $DRIVER_AUTHPROXY_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-driver-authproxy/private
mkdir -p /var/log/yandex/taxi-driver-authproxy/
ln -sf /taxi/logs/application-taxi-driver-authproxy.log /var/log/yandex/taxi-driver-authproxy/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-driver-authproxy \
    --fix-userver-client-timeout /etc/yandex/taxi/driver-authproxy/config.yaml \
    --syslog \
    --run /usr/bin/yandex-taxi-driver-authproxy \
        --config /etc/yandex/taxi/driver-authproxy/config.yaml \
        --init-log /var/log/yandex/taxi-driver-authproxy/server.log
