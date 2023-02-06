#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
PARKS_ACTIVATION_PATH=$USERVICES_PATH/build-integration/services/parks-activation
PARKS_ACTIVATION_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/parks-activation
PARKS_ACTIVATION_DEB_PATH=$USERVICES_PATH/services/parks-activation/debian

PARKS_ACTIVATION_BINARY_PATH=
if [ -f "$PARKS_ACTIVATION_PATH/yandex-taxi-parks-activation" ]; then
  PARKS_ACTIVATION_BINARY_PATH="$PARKS_ACTIVATION_PATH/yandex-taxi-parks-activation"
elif [ -f "$PARKS_ACTIVATION_ARCADIA_PATH/yandex-taxi-parks-activation" ]; then
  PARKS_ACTIVATION_BINARY_PATH="$PARKS_ACTIVATION_ARCADIA_PATH/yandex-taxi-parks-activation"
fi

if [ -f "$PARKS_ACTIVATION_BINARY_PATH" ]; then
    echo "parks-activation update package"
    mkdir -p /etc/yandex/taxi/parks-activation/
    rm -rf /etc/yandex/taxi/parks-activation/*
    ln -s $PARKS_ACTIVATION_PATH/configs/* /etc/yandex/taxi/parks-activation/
    cp $PARKS_ACTIVATION_PATH/config.yaml /etc/yandex/taxi/parks-activation/
    ln -s $PARKS_ACTIVATION_PATH/taxi_config_fallback.json /etc/yandex/taxi/parks-activation/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/parks-activation/
    ln -s config_vars.production.yaml /etc/yandex/taxi/parks-activation/config_vars.yaml

    ln -sf $PARKS_ACTIVATION_DEB_PATH/yandex-taxi-parks-activation.nginx /etc/nginx/sites-available/yandex-taxi-parks-activation
    ln -sf $PARKS_ACTIVATION_DEB_PATH/yandex-taxi-parks-activation.upstream_list /etc/nginx/conf.d/

    ln -sf $PARKS_ACTIVATION_PATH/taxi-parks-activation-stats.py /usr/bin/

    echo "using binary: $PARKS_ACTIVATION_BINARY_PATH"
    ln -sf $PARKS_ACTIVATION_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-parks-activation/
mkdir -p /var/log/yandex/taxi-parks-activation/
ln -sf /taxi/logs/application-taxi-parks-activation.log /var/log/yandex/taxi-parks-activation/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-parks-activation \
    --fix-userver-client-timeout /etc/yandex/taxi/parks-activation/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-parks-activation \
        --config /etc/yandex/taxi/parks-activation/config.yaml \
        --init-log /var/log/yandex/taxi-parks-activation/server.log
