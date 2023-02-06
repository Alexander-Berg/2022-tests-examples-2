#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
EATS_PICKER_SUPPLY_PATH=$USERVICES_PATH/build-integration/services/eats-picker-supply
EATS_PICKER_SUPPLY_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/eats-picker-supply
EATS_PICKER_SUPPLY_DEB_PATH=$USERVICES_PATH/services/eats-picker-supply/debian

EATS_PICKER_SUPPLY_BINARY_PATH=
if [ -f "$EATS_PICKER_SUPPLY_PATH/yandex-taxi-eats-picker-supply" ]; then
  EATS_PICKER_SUPPLY_BINARY_PATH="$EATS_PICKER_SUPPLY_PATH/yandex-taxi-eats-picker-supply"
elif [ -f "$EATS_PICKER_SUPPLY_ARCADIA_PATH/yandex-taxi-eats-picker-supply" ]; then
  EATS_PICKER_SUPPLY_BINARY_PATH="$EATS_PICKER_SUPPLY_ARCADIA_PATH/yandex-taxi-eats-picker-supply"
fi

if [ -f "$EATS_PICKER_SUPPLY_BINARY_PATH" ]; then
    echo "eats-picker-supply update package"
    mkdir -p /etc/yandex/taxi/eats-picker-supply/
    rm -rf /etc/yandex/taxi/eats-picker-supply/*

    ln -s $EATS_PICKER_SUPPLY_PATH/configs/* /etc/yandex/taxi/eats-picker-supply/
    cp $EATS_PICKER_SUPPLY_PATH/config.yaml /etc/yandex/taxi/eats-picker-supply/
    ln -s $EATS_PICKER_SUPPLY_PATH/taxi_config_fallback.json /etc/yandex/taxi/eats-picker-supply/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/eats-picker-supply/
    ln -s config_vars.production.yaml /etc/yandex/taxi/eats-picker-supply/config_vars.yaml

    ln -sf $EATS_PICKER_SUPPLY_DEB_PATH/yandex-taxi-eats-picker-supply.nginx /etc/nginx/sites-available/yandex-taxi-eats-picker-supply
    ln -sf $EATS_PICKER_SUPPLY_DEB_PATH/yandex-taxi-eats-picker-supply.upstream_list /etc/nginx/conf.d/

    ln -sf $EATS_PICKER_SUPPLY_PATH/taxi-eats-picker-supply-stats.py /usr/bin/
    echo "using binary: $EATS_PICKER_SUPPLY_BINARY_PATH"
    ln -sf $EATS_PICKER_SUPPLY_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-eats-picker-supply/
mkdir -p /var/lib/yandex/taxi-eats-picker-supply/
mkdir -p /var/lib/yandex/taxi-eats-picker-supply/private/
mkdir -p /var/cache/yandex/taxi-eats-picker-supply/
ln -sf /taxi/logs/application-taxi-eats-picker-supply.log /var/log/yandex/taxi-eats-picker-supply/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-eats-picker-supply \
    --fix-userver-client-timeout /etc/yandex/taxi/eats-picker-supply/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-eats-picker-supply \
        --config /etc/yandex/taxi/eats-picker-supply/config.yaml \
        --init-log /var/log/yandex/taxi-eats-picker-supply/server.log
