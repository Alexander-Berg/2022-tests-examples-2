#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
ZALOGIN_PATH=$USERVICES_PATH/build-integration/services/zalogin
ZALOGIN_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/zalogin
ZALOGIN_DEB_PATH=$USERVICES_PATH/services/zalogin/debian

ZALOGIN_BINARY_PATH=
if [ -f "$ZALOGIN_PATH/yandex-taxi-zalogin" ]; then
  ZALOGIN_BINARY_PATH="$ZALOGIN_PATH/yandex-taxi-zalogin"
elif [ -f "$ZALOGIN_ARCADIA_PATH/yandex-taxi-zalogin" ]; then
  ZALOGIN_BINARY_PATH="$ZALOGIN_ARCADIA_PATH/yandex-taxi-zalogin"
fi

if [ -f "$ZALOGIN_BINARY_PATH" ]; then
    echo "zalogin update package"
    mkdir -p /etc/yandex/taxi/zalogin/
    rm -rf /etc/yandex/taxi/zalogin/* ||:
    ln -s $ZALOGIN_PATH/configs/* /etc/yandex/taxi/zalogin/
    cp $ZALOGIN_PATH/config.yaml /etc/yandex/taxi/zalogin/
    ln -s $ZALOGIN_PATH/taxi_config_fallback.json /etc/yandex/taxi/zalogin/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/zalogin/
    ln -s config_vars.production.yaml /etc/yandex/taxi/zalogin/config_vars.yaml

    ln -sf $ZALOGIN_DEB_PATH/yandex-taxi-zalogin.nginx /etc/nginx/sites-available/yandex-taxi-zalogin
    ln -sf $ZALOGIN_DEB_PATH/yandex-taxi-zalogin.upstream_list /etc/nginx/conf.d/

    echo "using binary: $ZALOGIN_BINARY_PATH"
    ln -sf $ZALOGIN_BINARY_PATH /usr/bin/
    ln -sf $ZALOGIN_PATH/taxi-zalogin-stats.py /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-zalogin/
mkdir -p /var/log/yandex/taxi-zalogin/
ln -sf /taxi/logs/application-taxi-zalogin.log /var/log/yandex/taxi-zalogin/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-zalogin \
    --fix-userver-client-timeout /etc/yandex/taxi/zalogin/config.yaml \
    --syslog \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-zalogin \
        --config /etc/yandex/taxi/zalogin/config.yaml \
        --init-log /var/log/yandex/taxi-zalogin/server.log

