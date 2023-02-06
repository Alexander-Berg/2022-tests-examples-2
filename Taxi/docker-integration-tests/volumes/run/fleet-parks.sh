#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
FLEET_PARKS_PATH=$USERVICES_PATH/build-integration/services/fleet-parks
FLEET_PARKS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/fleet-parks
FLEET_PARKS_DEB_PATH=$USERVICES_PATH/services/fleet-parks/debian

FLEET_PARKS_BINARY_PATH=
if [ -f "$FLEET_PARKS_PATH/yandex-taxi-fleet-parks" ]; then
  FLEET_PARKS_BINARY_PATH="$FLEET_PARKS_PATH/yandex-taxi-fleet-parks"
elif [ -f "$FLEET_PARKS_ARCADIA_PATH/yandex-taxi-fleet-parks" ]; then
  FLEET_PARKS_BINARY_PATH="$FLEET_PARKS_ARCADIA_PATH/yandex-taxi-fleet-parks"
fi

if [ -f "$FLEET_PARKS_BINARY_PATH" ]; then
    echo "fleet-parks update package"
    mkdir -p /etc/yandex/taxi/fleet-parks/
    mkdir -p /var/cache/yandex/taxi-fleet-parks/
    rm -rf /etc/yandex/taxi/fleet-parks/*
    ln -s $FLEET_PARKS_PATH/configs/* /etc/yandex/taxi/fleet-parks/
    cp $FLEET_PARKS_PATH/config.yaml /etc/yandex/taxi/fleet-parks/
    ln -s $FLEET_PARKS_PATH/taxi_config_fallback.json /etc/yandex/taxi/fleet-parks/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/fleet-parks/
    ln -s config_vars.production.yaml /etc/yandex/taxi/fleet-parks/config_vars.yaml

    ln -sf $FLEET_PARKS_DEB_PATH/yandex-taxi-fleet-parks.nginx /etc/nginx/sites-available/yandex-taxi-fleet-parks
    ln -sf $FLEET_PARKS_DEB_PATH/yandex-taxi-fleet-parks.upstream_list /etc/nginx/conf.d/

    ln -sf $FLEET_PARKS_PATH/taxi-fleet-parks-stats.py /usr/bin/

    echo "using binary: $FLEET_PARKS_BINARY_PATH"
    ln -sf $FLEET_PARKS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-fleet-parks/
mkdir -p /var/log/yandex/taxi-fleet-parks/
ln -sf /taxi/logs/application-taxi-fleet-parks.log /var/log/yandex/taxi-fleet-parks/server.log

/taxi/tools/run.py \
    --stdout-to-log \
    --nginx yandex-taxi-fleet-parks \
    --fix-userver-client-timeout /etc/yandex/taxi/fleet-parks/config.yaml \
    --syslog \
    --wait \
        mongo.taxi.yandex:27017 \
        redis.taxi.yandex:6379 \
        http://configs.taxi.yandex.net/ping \
    --run /usr/bin/yandex-taxi-fleet-parks \
        --config /etc/yandex/taxi/fleet-parks/config.yaml \
        --init-log /taxi/logs/application-taxi-fleet-parks-init.log
