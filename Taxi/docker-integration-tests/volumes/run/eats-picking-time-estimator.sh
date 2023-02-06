#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
EATS_PICKING_TIME_ESTIMATOR_PATH=$USERVICES_PATH/build-integration/services/eats-picking-time-estimator
EATS_PICKING_TIME_ESTIMATOR_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/eats-picking-time-estimator
EATS_PICKING_TIME_ESTIMATOR_DEB_PATH=$USERVICES_PATH/services/eats-picking-time-estimator/debian

EATS_PICKING_TIME_ESTIMATOR_BINARY_PATH=
if [ -f "$EATS_PICKING_TIME_ESTIMATOR_PATH/yandex-taxi-eats-picking-time-estimator" ]; then
  EATS_PICKING_TIME_ESTIMATOR_BINARY_PATH="$EATS_PICKING_TIME_ESTIMATOR_PATH/yandex-taxi-eats-picking-time-estimator"
elif [ -f "$EATS_PICKING_TIME_ESTIMATOR_ARCADIA_PATH/yandex-taxi-eats-picking-time-estimator" ]; then
  EATS_PICKING_TIME_ESTIMATOR_BINARY_PATH="$EATS_PICKING_TIME_ESTIMATOR_ARCADIA_PATH/yandex-taxi-eats-picking-time-estimator"
fi

if [ -f "$EATS_PICKING_TIME_ESTIMATOR_BINARY_PATH" ]; then
    echo "eats-picking-time-estimator update package"
    mkdir -p /etc/yandex/taxi/eats-picking-time-estimator/
    rm -rf /etc/yandex/taxi/eats-picking-time-estimator/*

    ln -s $EATS_PICKING_TIME_ESTIMATOR_PATH/configs/* /etc/yandex/taxi/eats-picking-time-estimator/
    cp $EATS_PICKING_TIME_ESTIMATOR_PATH/config.yaml /etc/yandex/taxi/eats-picking-time-estimator/
    ln -s $EATS_PICKING_TIME_ESTIMATOR_PATH/taxi_config_fallback.json /etc/yandex/taxi/eats-picking-time-estimator/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/eats-picking-time-estimator/
    ln -s config_vars.production.yaml /etc/yandex/taxi/eats-picking-time-estimator/config_vars.yaml

    ln -sf $EATS_PICKING_TIME_ESTIMATOR_DEB_PATH/yandex-taxi-eats-picking-time-estimator.nginx /etc/nginx/sites-available/yandex-taxi-eats-picking-time-estimator
    ln -sf $EATS_PICKING_TIME_ESTIMATOR_DEB_PATH/yandex-taxi-eats-picking-time-estimator.upstream_list /etc/nginx/conf.d/

    ln -sf $EATS_PICKING_TIME_ESTIMATOR_PATH/taxi-eats-picking-time-estimator-stats.py /usr/bin/
    echo "using binary: $EATS_PICKING_TIME_ESTIMATOR_BINARY_PATH"
    ln -sf $EATS_PICKING_TIME_ESTIMATOR_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-eats-picking-time-estimator/
mkdir -p /var/lib/yandex/taxi-eats-picking-time-estimator/
mkdir -p /var/lib/yandex/taxi-eats-picking-time-estimator/private/
mkdir -p /var/cache/yandex/taxi-eats-picking-time-estimator/
ln -sf /taxi/logs/application-taxi-eats-picking-time-estimator.log /var/log/yandex/taxi-eats-picking-time-estimator/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-eats-picking-time-estimator \
    --fix-userver-client-timeout /etc/yandex/taxi/eats-picking-time-estimator/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-eats-picking-time-estimator \
        --config /etc/yandex/taxi/eats-picking-time-estimator/config.yaml \
        --init-log /var/log/yandex/taxi-eats-picking-time-estimator/server.log
