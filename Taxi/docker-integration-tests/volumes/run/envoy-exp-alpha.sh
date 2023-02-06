#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
ENVOY_EXP_ALPHA_PATH=$USERVICES_PATH/build-integration/services/envoy-exp-alpha
ENVOY_EXP_ALPHA_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/envoy-exp-alpha
ENVOY_EXP_ALPHA_DEB_PATH=$USERVICES_PATH/services/envoy-exp-alpha/debian

ENVOY_EXP_ALPHA_BINARY_PATH=
if [ -f "$ENVOY_EXP_ALPHA_PATH/yandex-taxi-envoy-exp-alpha" ]; then
  ENVOY_EXP_ALPHA_BINARY_PATH="$ENVOY_EXP_ALPHA_PATH/yandex-taxi-envoy-exp-alpha"
elif [ -f "$ENVOY_EXP_ALPHA_ARCADIA_PATH/yandex-taxi-envoy-exp-alpha" ]; then
  ENVOY_EXP_ALPHA_BINARY_PATH="$ENVOY_EXP_ALPHA_ARCADIA_PATH/yandex-taxi-envoy-exp-alpha"
fi

if [ -f "$ENVOY_EXP_ALPHA_BINARY_PATH" ]; then
    echo "envoy-exp-alpha update package"
    mkdir -p /etc/yandex/taxi/envoy-exp-alpha/
    rm -rf /etc/yandex/taxi/envoy-exp-alpha/*

    ln -s $ENVOY_EXP_ALPHA_PATH/configs/* /etc/yandex/taxi/envoy-exp-alpha/
    cp $ENVOY_EXP_ALPHA_PATH/config.yaml /etc/yandex/taxi/envoy-exp-alpha/
    ln -s $ENVOY_EXP_ALPHA_PATH/taxi_config_fallback.json /etc/yandex/taxi/envoy-exp-alpha/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/envoy-exp-alpha/
    ln -s config_vars.production.yaml /etc/yandex/taxi/envoy-exp-alpha/config_vars.yaml

    ln -sf $ENVOY_EXP_ALPHA_DEB_PATH/yandex-taxi-envoy-exp-alpha.nginx /etc/nginx/sites-available/yandex-taxi-envoy-exp-alpha
    ln -sf $ENVOY_EXP_ALPHA_DEB_PATH/yandex-taxi-envoy-exp-alpha.upstream_list /etc/nginx/conf.d/

    ln -sf $ENVOY_EXP_ALPHA_PATH/taxi-envoy-exp-alpha-stats.py /usr/bin/

    echo "using binary: $ENVOY_EXP_ALPHA_BINARY_PATH"
    ln -sf $ENVOY_EXP_ALPHA_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-envoy-exp-alpha/
mkdir -p /var/lib/yandex/taxi-envoy-exp-alpha/
mkdir -p /var/lib/yandex/taxi-envoy-exp-alpha/private/
mkdir -p /var/cache/yandex/taxi-envoy-exp-alpha/
ln -sf /taxi/logs/application-taxi-envoy-exp-alpha.log /var/log/yandex/taxi-envoy-exp-alpha/server.log

/taxi/tools/start_envoy.sh taxi_tst_envoy-exp-alpha_stable

/taxi/tools/run.py \
    --nginx yandex-taxi-envoy-exp-alpha \
    --fix-userver-client-timeout /etc/yandex/taxi/envoy-exp-alpha/config.yaml \
    --fix-userver-client-timeout-value 30s \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-envoy-exp-alpha \
        --config /etc/yandex/taxi/envoy-exp-alpha/config.yaml \
        --init-log /var/log/yandex/taxi-envoy-exp-alpha/server.log
