#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
DRIVER_AUTHORIZER_PATH=$USERVICES_PATH/build-integration/services/driver-authorizer
DRIVER_AUTHORIZER_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/driver-authorizer
DRIVER_AUTHORIZER_DEB_PATH=$USERVICES_PATH/services/driver-authorizer/debian

DRIVER_AUTHORIZER_BINARY_PATH=
if [ -f "$DRIVER_AUTHORIZER_PATH/yandex-taxi-driver-authorizer" ]; then
  DRIVER_AUTHORIZER_BINARY_PATH="$DRIVER_AUTHORIZER_PATH/yandex-taxi-driver-authorizer"
elif [ -f "$DRIVER_AUTHORIZER_ARCADIA_PATH/yandex-taxi-driver-authorizer" ]; then
  DRIVER_AUTHORIZER_BINARY_PATH="$DRIVER_AUTHORIZER_ARCADIA_PATH/yandex-taxi-driver-authorizer"
fi

if [ -f "$DRIVER_AUTHORIZER_BINARY_PATH" ]; then
    echo "driver-authorizer update package"
    mkdir -p /etc/yandex/taxi/driver-authorizer/
    rm -rf /etc/yandex/taxi/driver-authorizer/*
    ln -s $DRIVER_AUTHORIZER_PATH/configs/* /etc/yandex/taxi/driver-authorizer/
    cp $DRIVER_AUTHORIZER_PATH/config.yaml /etc/yandex/taxi/driver-authorizer/
    ln -s $DRIVER_AUTHORIZER_PATH/taxi_config_fallback.json /etc/yandex/taxi/driver-authorizer/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/driver-authorizer/
    ln -s config_vars.production.yaml /etc/yandex/taxi/driver-authorizer/config_vars.yaml

    ln -sf $DRIVER_AUTHORIZER_DEB_PATH/yandex-taxi-driver-authorizer.nginx /etc/nginx/sites-available/yandex-taxi-driver-authorizer
    ln -sf $DRIVER_AUTHORIZER_DEB_PATH/yandex-taxi-driver-authorizer.upstream_list /etc/nginx/conf.d/

    ln -sf $DRIVER_AUTHORIZER_PATH/taxi-driver-authorizer-stats.py /usr/bin/

    echo "using binary: $DRIVER_AUTHORIZER_BINARY_PATH"
    ln -sf $DRIVER_AUTHORIZER_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-driver-authorizer/
mkdir -p /var/log/yandex/taxi-driver-authorizer/
ln -sf /taxi/logs/application-taxi-driver-authorizer.log /var/log/yandex/taxi-driver-authorizer/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-driver-authorizer \
    --fix-userver-client-timeout /etc/yandex/taxi/driver-authorizer/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-driver-authorizer \
        --config /etc/yandex/taxi/driver-authorizer/config.yaml \
        --init-log /taxi/logs/application-taxi-driver-authorizer.log
