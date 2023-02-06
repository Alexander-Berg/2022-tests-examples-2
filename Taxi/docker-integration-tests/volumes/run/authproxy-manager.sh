#!/usr/bin/env bash

set -e

USERVICES_PATH=/arcadia/taxi/uservices
AUTHPROXY_MANAGER_PATH=$USERVICES_PATH/build-integration/services/authproxy-manager
AUTHPROXY_MANAGER_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/authproxy-manager
AUTHPROXY_MANAGER_DEB_PATH=$USERVICES_PATH/services/authproxy-manager/debian

AUTHPROXY_MANAGER_BINARY_PATH=
if [ -f "$AUTHPROXY_MANAGER_PATH/yandex-taxi-authproxy-manager" ]; then
  AUTHPROXY_MANAGER_BINARY_PATH="$AUTHPROXY_MANAGER_PATH/yandex-taxi-authproxy-manager"
elif [ -f "$AUTHPROXY_MANAGER_ARCADIA_PATH/yandex-taxi-authproxy-manager" ]; then
  AUTHPROXY_MANAGER_BINARY_PATH="$AUTHPROXY_MANAGER_ARCADIA_PATH/yandex-taxi-authproxy-manager"
fi

if [ -f "$AUTHPROXY_MANAGER_BINARY_PATH" ]; then
    echo "authproxy-manager update package"
    mkdir -p /etc/yandex/taxi/authproxy-manager/
    rm -rf /etc/yandex/taxi/authproxy-manager/*

    ln -s $AUTHPROXY_MANAGER_PATH/configs/* /etc/yandex/taxi/authproxy-manager/
    cp $AUTHPROXY_MANAGER_PATH/config.yaml /etc/yandex/taxi/authproxy-manager/
    ln -s $AUTHPROXY_MANAGER_PATH/taxi_config_fallback.json /etc/yandex/taxi/authproxy-manager/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/authproxy-manager/
    ln -s config_vars.production.yaml /etc/yandex/taxi/authproxy-manager/config_vars.yaml

    ln -sf $AUTHPROXY_MANAGER_DEB_PATH/yandex-taxi-authproxy-manager.nginx /etc/nginx/sites-available/yandex-taxi-authproxy-manager
    ln -sf $AUTHPROXY_MANAGER_DEB_PATH/yandex-taxi-authproxy-manager.upstream_list /etc/nginx/conf.d/

    ln -sf $AUTHPROXY_MANAGER_PATH/taxi-authproxy-manager-stats.py /usr/bin/

    echo "using binary: $AUTHPROXY_MANAGER_BINARY_PATH"
    ln -sf $AUTHPROXY_MANAGER_BINARY_PATH /usr/bin/

    mkdir -p /var/lib/yandex/taxi-authproxy-manager/
    ln -s $USERVICES_PATH/services/authproxy-manager/meta_headers /var/lib/yandex/taxi-authproxy-manager/
fi

mkdir -p /var/log/yandex/taxi-authproxy-manager/
mkdir -p /var/lib/yandex/taxi-authproxy-manager/
mkdir -p /var/lib/yandex/taxi-authproxy-manager/private/
mkdir -p /var/cache/yandex/taxi-authproxy-manager/
ln -sf /taxi/logs/application-taxi-authproxy-manager.log /var/log/yandex/taxi-authproxy-manager/server.log

nohup /usr/lib/yandex/taxi-py3-2/bin/python3 /taxi/run/authproxy-manager/import_rules.py \
    --host authproxy-manager.taxi.yandex.net \
    --rules /taxi/run/authproxy-manager/pa-am.json \
    --sleep 1 \
    --timeout 10 &

/usr/lib/yandex/taxi-py3-2/bin/python3 \
    /taxi/tools/run.py \
    --nginx yandex-taxi-authproxy-manager \
    --fix-userver-client-timeout /etc/yandex/taxi/authproxy-manager/config.yaml \
    --wait \
          postgresql:dbauthproxymanager \
    --run /usr/bin/yandex-taxi-authproxy-manager \
        --config /etc/yandex/taxi/authproxy-manager/config.yaml \
        --init-log /var/log/yandex/taxi-authproxy-manager/server.log
