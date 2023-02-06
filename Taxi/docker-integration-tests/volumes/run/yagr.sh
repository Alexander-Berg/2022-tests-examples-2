#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
YAGR_PATH=$USERVICES_PATH/build-integration/services/yagr
YAGR_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/yagr
YAGR_DEB_PATH=$USERVICES_PATH/services/yagr/debian

YAGR_BINARY_PATH=
if [ -f "$YAGR_PATH/yandex-taxi-yagr" ]; then
  YAGR_BINARY_PATH="$YAGR_PATH/yandex-taxi-yagr"
elif [ -f "$YAGR_ARCADIA_PATH/yandex-taxi-yagr" ]; then
  YAGR_BINARY_PATH="$YAGR_ARCADIA_PATH/yandex-taxi-yagr"
fi

if [ -f "$YAGR_BINARY_PATH" ]; then
    echo "yagr update package"
    mkdir -p /etc/yandex/taxi/yagr/
    rm -rf /etc/yandex/taxi/yagr/*

    ln -s $YAGR_PATH/configs/* /etc/yandex/taxi/yagr/
    cp $YAGR_PATH/config.yaml /etc/yandex/taxi/yagr/
    ln -s $YAGR_PATH/taxi_config_fallback.json /etc/yandex/taxi/yagr/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/yagr/
    ln -s config_vars.production.yaml /etc/yandex/taxi/yagr/config_vars.yaml

    ln -sf $YAGR_DEB_PATH/yandex-taxi-yagr.nginx /etc/nginx/sites-available/yandex-taxi-yagr
    ln -sf $YAGR_DEB_PATH/yandex-taxi-yagr.upstream_list /etc/nginx/conf.d/

    ln -sf $YAGR_PATH/taxi-yagr-stats.py /usr/bin/

    echo "using binary: $YAGR_BINARY_PATH"
    ln -sf $YAGR_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-yagr/
mkdir -p /var/lib/yandex/taxi-yagr/
mkdir -p /var/lib/yandex/taxi-yagr/private/
mkdir -p /var/cache/yandex/taxi-yagr/
ln -sf /taxi/logs/application-taxi-yagr.log /var/log/yandex/taxi-yagr/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-yagr \
    --fix-userver-client-timeout /etc/yandex/taxi/yagr/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-yagr \
        --config /etc/yandex/taxi/yagr/config.yaml \
        --init-log /var/log/yandex/taxi-yagr/server.log

