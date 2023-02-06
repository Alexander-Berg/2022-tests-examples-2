#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
DRIVER_UI_PROFILE_PATH=$USERVICES_PATH/build-integration/services/driver-ui-profile
DRIVER_UI_PROFILE_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/driver-ui-profile
DRIVER_UI_PROFILE_DEB_PATH=$USERVICES_PATH/services/driver-ui-profile/debian

DRIVER_UI_PROFILE_BINARY_PATH=
if [ -f "$DRIVER_UI_PROFILE_PATH/yandex-taxi-driver-ui-profile" ]; then
  DRIVER_UI_PROFILE_BINARY_PATH="$DRIVER_UI_PROFILE_PATH/yandex-taxi-driver-ui-profile"
elif [ -f "$DRIVER_UI_PROFILE_ARCADIA_PATH/yandex-taxi-driver-ui-profile" ]; then
  DRIVER_UI_PROFILE_BINARY_PATH="$DRIVER_UI_PROFILE_ARCADIA_PATH/yandex-taxi-driver-ui-profile"
fi

if [ -f "$DRIVER_UI_PROFILE_BINARY_PATH" ]; then
    echo "driver-ui-profile update package"
    mkdir -p /etc/yandex/taxi/driver-ui-profile/
    rm -rf /etc/yandex/taxi/driver-ui-profile/*

    ln -s $DRIVER_UI_PROFILE_PATH/configs/* /etc/yandex/taxi/driver-ui-profile/
    cp $DRIVER_UI_PROFILE_PATH/config.yaml /etc/yandex/taxi/driver-ui-profile/
    ln -s $DRIVER_UI_PROFILE_PATH/taxi_config_fallback.json /etc/yandex/taxi/driver-ui-profile/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/driver-ui-profile/
    ln -s config_vars.production.yaml /etc/yandex/taxi/driver-ui-profile/config_vars.yaml

    ln -sf $DRIVER_UI_PROFILE_DEB_PATH/yandex-taxi-driver-ui-profile.nginx /etc/nginx/sites-available/yandex-taxi-driver-ui-profile
    ln -sf $DRIVER_UI_PROFILE_DEB_PATH/yandex-taxi-driver-ui-profile.upstream_list /etc/nginx/conf.d/

    ln -sf $DRIVER_UI_PROFILE_PATH/taxi-driver-ui-profile-stats.py /usr/bin/

    echo "using binary: $DRIVER_UI_PROFILE_BINARY_PATH"
    ln -sf $DRIVER_UI_PROFILE_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-driver-ui-profile/
mkdir -p /var/lib/yandex/taxi-driver-ui-profile/
mkdir -p /var/lib/yandex/taxi-driver-ui-profile/private/
mkdir -p /var/cache/yandex/taxi-driver-ui-profile/
ln -sf /taxi/logs/application-taxi-driver-ui-profile.log /var/log/yandex/taxi-driver-ui-profile/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-driver-ui-profile \
    --fix-userver-client-timeout /etc/yandex/taxi/driver-ui-profile/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-driver-ui-profile \
        --config /etc/yandex/taxi/driver-ui-profile/config.yaml \
        --init-log /var/log/yandex/taxi-driver-ui-profile/server.log
