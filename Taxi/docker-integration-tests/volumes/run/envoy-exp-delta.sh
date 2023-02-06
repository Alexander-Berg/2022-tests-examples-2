#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
ENVOY_EXP_DELTA_PATH=$USERVICES_PATH/build-integration/services/envoy-exp-delta
ENVOY_EXP_DELTA_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/envoy-exp-delta
ENVOY_EXP_DELTA_DEB_PATH=$USERVICES_PATH/services/envoy-exp-delta/debian

ENVOY_EXP_DELTA_BINARY_PATH=
if [ -f "$ENVOY_EXP_DELTA_PATH/yandex-taxi-envoy-exp-delta" ]; then
  ENVOY_EXP_DELTA_BINARY_PATH="$ENVOY_EXP_DELTA_PATH/yandex-taxi-envoy-exp-delta"
elif [ -f "$ENVOY_EXP_DELTA_ARCADIA_PATH/yandex-taxi-envoy-exp-delta" ]; then
  ENVOY_EXP_DELTA_BINARY_PATH="$ENVOY_EXP_DELTA_ARCADIA_PATH/yandex-taxi-envoy-exp-delta"
fi

if [ -f "$ENVOY_EXP_DELTA_BINARY_PATH" ]; then
    echo "envoy-exp-delta update package"
    mkdir -p /etc/yandex/taxi/envoy-exp-delta/
    rm -rf /etc/yandex/taxi/envoy-exp-delta/*

    ln -s $ENVOY_EXP_DELTA_PATH/configs/* /etc/yandex/taxi/envoy-exp-delta/
    cp $ENVOY_EXP_DELTA_PATH/config.yaml /etc/yandex/taxi/envoy-exp-delta/
    ln -s $ENVOY_EXP_DELTA_PATH/taxi_config_fallback.json /etc/yandex/taxi/envoy-exp-delta/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/envoy-exp-delta/
    ln -s config_vars.production.yaml /etc/yandex/taxi/envoy-exp-delta/config_vars.yaml

    ln -sf $ENVOY_EXP_DELTA_DEB_PATH/yandex-taxi-envoy-exp-delta.nginx /etc/nginx/sites-available/yandex-taxi-envoy-exp-delta
    ln -sf $ENVOY_EXP_DELTA_DEB_PATH/yandex-taxi-envoy-exp-delta.upstream_list /etc/nginx/conf.d/

    ln -sf $ENVOY_EXP_DELTA_PATH/taxi-envoy-exp-delta-stats.py /usr/bin/

    echo "using binary: $ENVOY_EXP_DELTA_BINARY_PATH"
    ln -sf $ENVOY_EXP_DELTA_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-envoy-exp-delta/
mkdir -p /var/lib/yandex/taxi-envoy-exp-delta/
mkdir -p /var/lib/yandex/taxi-envoy-exp-delta/private/
mkdir -p /var/cache/yandex/taxi-envoy-exp-delta/
ln -sf /taxi/logs/application-taxi-envoy-exp-delta.log /var/log/yandex/taxi-envoy-exp-delta/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-envoy-exp-delta \
    --fix-userver-client-timeout /etc/yandex/taxi/envoy-exp-delta/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-envoy-exp-delta \
        --config /etc/yandex/taxi/envoy-exp-delta/config.yaml \
        --init-log /var/log/yandex/taxi-envoy-exp-delta/server.log
