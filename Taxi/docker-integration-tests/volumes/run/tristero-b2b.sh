#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
TRISTERO_B2B_PATH=$USERVICES_PATH/build-integration/services/tristero-b2b
TRISTERO_B2B_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/tristero-b2b
TRISTERO_B2B_DEB_PATH=$USERVICES_PATH/services/tristero-b2b/debian

TRISTERO_B2B_BINARY_PATH=
if [ -f "$TRISTERO_B2B_PATH/yandex-taxi-tristero-b2b" ]; then
  TRISTERO_B2B_BINARY_PATH="$TRISTERO_B2B_PATH/yandex-taxi-tristero-b2b"
elif [ -f "$TRISTERO_B2B_ARCADIA_PATH/yandex-taxi-tristero-b2b" ]; then
  TRISTERO_B2B_BINARY_PATH="$TRISTERO_B2B_ARCADIA_PATH/yandex-taxi-tristero-b2b"
fi

if [ -f "$TRISTERO_B2B_BINARY_PATH" ]; then
    echo "tristero-b2b update package"
    mkdir -p /etc/yandex/taxi/tristero-b2b/
    rm -rf /etc/yandex/taxi/tristero-b2b/*

    ln -s $TRISTERO_B2B_PATH/configs/* /etc/yandex/taxi/tristero-b2b/
    cp $TRISTERO_B2B_PATH/config.yaml /etc/yandex/taxi/tristero-b2b/
    ln -s $TRISTERO_B2B_PATH/taxi_config_fallback.json /etc/yandex/taxi/tristero-b2b/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/tristero-b2b/
    ln -s config_vars.production.yaml /etc/yandex/taxi/tristero-b2b/config_vars.yaml

    ln -sf $TRISTERO_B2B_DEB_PATH/yandex-taxi-tristero-b2b.nginx /etc/nginx/sites-available/yandex-taxi-tristero-b2b
    ln -sf $TRISTERO_B2B_DEB_PATH/yandex-taxi-tristero-b2b.upstream_list /etc/nginx/conf.d/

    ln -sf $TRISTERO_B2B_PATH/taxi-tristero-b2b-stats.py /usr/bin/
    echo "using binary: $TRISTERO_B2B_BINARY_PATH"
    ln -sf $TRISTERO_B2B_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-tristero-b2b/
mkdir -p /var/lib/yandex/taxi-tristero-b2b/
mkdir -p /var/lib/yandex/taxi-tristero-b2b/private/
mkdir -p /var/cache/yandex/taxi-tristero-b2b/
ln -sf /taxi/logs/application-taxi-tristero-b2b.log /var/log/yandex/taxi-tristero-b2b/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-tristero-b2b \
    --fix-userver-client-timeout /etc/yandex/taxi/tristero-b2b/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-tristero-b2b \
        --config /etc/yandex/taxi/tristero-b2b/config.yaml \
        --init-log /var/log/yandex/taxi-tristero-b2b/server.log
