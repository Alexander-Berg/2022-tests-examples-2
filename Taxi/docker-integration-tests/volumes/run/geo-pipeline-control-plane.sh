#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GEO_PIPELINE_CONTROL_PLANE_PATH=$USERVICES_PATH/build-integration/services/geo-pipeline-control-plane
GEO_PIPELINE_CONTROL_PLANE_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/geo-pipeline-control-plane
GEO_PIPELINE_CONTROL_PLANE_DEB_PATH=$USERVICES_PATH/services/geo-pipeline-control-plane/debian

GEO_PIPELINE_CONTROL_PLANE_BINARY_PATH=
if [ -f "$GEO_PIPELINE_CONTROL_PLANE_PATH/yandex-taxi-geo-pipeline-control-plane" ]; then
  GEO_PIPELINE_CONTROL_PLANE_BINARY_PATH="$GEO_PIPELINE_CONTROL_PLANE_PATH/yandex-taxi-geo-pipeline-control-plane"
elif [ -f "$GEO_PIPELINE_CONTROL_PLANE_ARCADIA_PATH/yandex-taxi-geo-pipeline-control-plane" ]; then
  GEO_PIPELINE_CONTROL_PLANE_BINARY_PATH="$GEO_PIPELINE_CONTROL_PLANE_ARCADIA_PATH/yandex-taxi-geo-pipeline-control-plane"
fi

if [ -f "$GEO_PIPELINE_CONTROL_PLANE_BINARY_PATH" ]; then
    echo "geo-pipeline-control-plane update package"
    mkdir -p /etc/yandex/taxi/geo-pipeline-control-plane/
    rm -rf /etc/yandex/taxi/geo-pipeline-control-plane/*

    ln -s $GEO_PIPELINE_CONTROL_PLANE_PATH/configs/* /etc/yandex/taxi/geo-pipeline-control-plane/
    cp $GEO_PIPELINE_CONTROL_PLANE_PATH/config.yaml /etc/yandex/taxi/geo-pipeline-control-plane/
    ln -s $GEO_PIPELINE_CONTROL_PLANE_PATH/taxi_config_fallback.json /etc/yandex/taxi/geo-pipeline-control-plane/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/geo-pipeline-control-plane/
    ln -s config_vars.production.yaml /etc/yandex/taxi/geo-pipeline-control-plane/config_vars.yaml

    ln -sf $GEO_PIPELINE_CONTROL_PLANE_DEB_PATH/yandex-taxi-geo-pipeline-control-plane.nginx /etc/nginx/sites-available/yandex-taxi-geo-pipeline-control-plane
    ln -sf $GEO_PIPELINE_CONTROL_PLANE_DEB_PATH/yandex-taxi-geo-pipeline-control-plane.upstream_list /etc/nginx/conf.d/

    ln -sf $GEO_PIPELINE_CONTROL_PLANE_PATH/taxi-geo-pipeline-control-plane-stats.py /usr/bin/

    echo "using binary: $GEO_PIPELINE_CONTROL_PLANE_BINARY_PATH"
    ln -sf $GEO_PIPELINE_CONTROL_PLANE_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-geo-pipeline-control-plane/
mkdir -p /var/lib/yandex/taxi-geo-pipeline-control-plane/
mkdir -p /var/lib/yandex/taxi-geo-pipeline-control-plane/private/
mkdir -p /var/cache/yandex/taxi-geo-pipeline-control-plane/
ln -sf /taxi/logs/application-taxi-geo-pipeline-control-plane.log /var/log/yandex/taxi-geo-pipeline-control-plane/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-geo-pipeline-control-plane \
    --fix-userver-client-timeout /etc/yandex/taxi/geo-pipeline-control-plane/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-geo-pipeline-control-plane \
        --config /etc/yandex/taxi/geo-pipeline-control-plane/config.yaml \
        --init-log /var/log/yandex/taxi-geo-pipeline-control-plane/server.log
