#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
EATS_LAUNCH_PATH=$USERVICES_PATH/build-integration/services/eats-launch
EATS_LAUNCH_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/eats-launch
EATS_LAUNCH_DEB_PATH=$USERVICES_PATH/services/eats-launch/debian

EATS_LAUNCH_BINARY_PATH=
if [ -f "$EATS_LAUNCH_PATH/yandex-taxi-eats-launch" ]; then
  EATS_LAUNCH_BINARY_PATH="$EATS_LAUNCH_PATH/yandex-taxi-eats-launch"
elif [ -f "$EATS_LAUNCH_ARCADIA_PATH/yandex-taxi-eats-launch" ]; then
  EATS_LAUNCH_BINARY_PATH="$EATS_LAUNCH_ARCADIA_PATH/yandex-taxi-eats-launch"
fi

if [ -f "$EATS_LAUNCH_BINARY_PATH" ]; then
    echo "eats-launch update package"
    mkdir -p /etc/yandex/taxi/eats-launch/
    rm -rf /etc/yandex/taxi/eats-launch/*

    ln -s $EATS_LAUNCH_PATH/configs/* /etc/yandex/taxi/eats-launch/
    cp $EATS_LAUNCH_PATH/config.yaml /etc/yandex/taxi/eats-launch/
    ln -s $EATS_LAUNCH_PATH/taxi_config_fallback.json /etc/yandex/taxi/eats-launch/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/eats-launch/
    ln -s config_vars.production.yaml /etc/yandex/taxi/eats-launch/config_vars.yaml

    ln -sf $EATS_LAUNCH_DEB_PATH/yandex-taxi-eats-launch.nginx /etc/nginx/sites-available/yandex-taxi-eats-launch
    ln -sf $EATS_LAUNCH_DEB_PATH/yandex-taxi-eats-launch.upstream_list /etc/nginx/conf.d/

    ln -sf $EATS_LAUNCH_PATH/taxi-eats-launch-stats.py /usr/bin/
    echo "using binary: $EATS_LAUNCH_BINARY_PATH"
    ln -sf $EATS_LAUNCH_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-eats-launch/
mkdir -p /var/lib/yandex/taxi-eats-launch/
mkdir -p /var/lib/yandex/taxi-eats-launch/private/
mkdir -p /var/cache/yandex/taxi-eats-launch/
ln -sf /taxi/logs/application-taxi-eats-launch.log /var/log/yandex/taxi-eats-launch/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-eats-launch \
    --fix-userver-client-timeout /etc/yandex/taxi/eats-launch/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-eats-launch \
        --config /etc/yandex/taxi/eats-launch/config.yaml \
        --init-log /var/log/yandex/taxi-eats-launch/server.log
