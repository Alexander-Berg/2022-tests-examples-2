#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
FLEET_VEHICLES_PATH=$USERVICES_PATH/build-integration/services/fleet-vehicles
FLEET_VEHICLES_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/fleet-vehicles
FLEET_VEHICLES_DEB_PATH=$USERVICES_PATH/services/fleet-vehicles/debian

FLEET_VEHICLES_BINARY_PATH=
if [ -f "$FLEET_VEHICLES_PATH/yandex-taxi-fleet-vehicles" ]; then
  FLEET_VEHICLES_BINARY_PATH="$FLEET_VEHICLES_PATH/yandex-taxi-fleet-vehicles"
elif [ -f "$FLEET_VEHICLES_ARCADIA_PATH/yandex-taxi-fleet-vehicles" ]; then
  FLEET_VEHICLES_BINARY_PATH="$FLEET_VEHICLES_ARCADIA_PATH/yandex-taxi-fleet-vehicles"
fi

if [ -f "$FLEET_VEHICLES_BINARY_PATH" ]; then
    echo "fleet-vehicles update package"
    mkdir -p /etc/yandex/taxi/fleet-vehicles/
    mkdir -p /var/cache/yandex/taxi-fleet-vehicles/
    rm -rf /etc/yandex/taxi/fleet-vehicles/*
    ln -s $FLEET_VEHICLES_PATH/configs/* /etc/yandex/taxi/fleet-vehicles/
    cp $FLEET_VEHICLES_PATH/config.yaml /etc/yandex/taxi/fleet-vehicles/
    ln -s $FLEET_VEHICLES_PATH/taxi_config_fallback.json /etc/yandex/taxi/fleet-vehicles/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/fleet-vehicles/
    ln -s config_vars.production.yaml /etc/yandex/taxi/fleet-vehicles/config_vars.yaml

    ln -sf $FLEET_VEHICLES_DEB_PATH/yandex-taxi-fleet-vehicles.nginx /etc/nginx/sites-available/yandex-taxi-fleet-vehicles
    ln -sf $FLEET_VEHICLES_DEB_PATH/yandex-taxi-fleet-vehicles.upstream_list /etc/nginx/conf.d/

    ln -sf $FLEET_VEHICLES_PATH/taxi-fleet-vehicles-stats.py /usr/bin/

    echo "using binary: $FLEET_VEHICLES_BINARY_PATH"
    ln -sf $FLEET_VEHICLES_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-fleet-vehicles/
mkdir -p /var/lib/yandex/taxi-fleet-vehicles/
ln -sf /taxi/logs/application-taxi-fleet-vehicles.log /var/log/yandex/taxi-fleet-vehicles/server.log

/taxi/tools/run.py \
    --stdout-to-log \
    --nginx yandex-taxi-fleet-vehicles \
    --fix-userver-client-timeout /etc/yandex/taxi/fleet-vehicles/config.yaml \
    --syslog \
    --wait \
        mongo.taxi.yandex:27017 \
        http://configs.taxi.yandex.net/ping \
    --run /usr/bin/yandex-taxi-fleet-vehicles \
        --config /etc/yandex/taxi/fleet-vehicles/config.yaml \
        --init-log /taxi/logs/application-taxi-fleet-vehicles-init.log
