#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
PERSONAL_PATH=$USERVICES_PATH/build-integration/services/personal
PERSONAL_UNIT_PATH=$PERSONAL_PATH/units/personal
PERSONAL_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/personal
PERSONAL_DEB_PATH=$USERVICES_PATH/services/personal/debian

PERSONAL_BINARY_PATH=
if [ -f "$PERSONAL_PATH/yandex-taxi-personal" ]; then
  PERSONAL_BINARY_PATH="$PERSONAL_PATH/yandex-taxi-personal"
elif [ -f "$PERSONAL_ARCADIA_PATH/yandex-taxi-personal" ]; then
  PERSONAL_BINARY_PATH="$PERSONAL_ARCADIA_PATH/yandex-taxi-personal"
fi

if [ -f "$PERSONAL_BINARY_PATH" ]; then
    echo "personal update package"
    mkdir -p /etc/yandex/taxi/personal/
    rm -rf /etc/yandex/taxi/personal/*

    if [ -e $PERSONAL_PATH/config.yaml ]; then
        ln -s $PERSONAL_PATH/configs/* /etc/yandex/taxi/personal/
        cp $PERSONAL_PATH/config.yaml /etc/yandex/taxi/personal/
    else
        ln -s $PERSONAL_UNIT_PATH/configs/* /etc/yandex/taxi/personal/
        cp $PERSONAL_UNIT_PATH/config.yaml /etc/yandex/taxi/personal/
    fi

    ln -s $PERSONAL_PATH/taxi_config_fallback.json /etc/yandex/taxi/personal/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/personal/
    ln -s config_vars.production.yaml /etc/yandex/taxi/personal/config_vars.yaml

    ln -sf $PERSONAL_DEB_PATH/yandex-taxi-personal.nginx /etc/nginx/sites-available/yandex-taxi-personal
    ln -sf $PERSONAL_DEB_PATH/yandex-taxi-personal.upstream_list /etc/nginx/conf.d/

    ln -sf $PERSONAL_PATH/taxi-personal-stats.py /usr/bin/

    echo "using binary: $PERSONAL_BINARY_PATH"
    ln -sf $PERSONAL_BINARY_PATH /usr/bin/
fi


mkdir -p /var/cache/yandex/taxi-personal/
mkdir -p /var/lib/yandex/taxi-personal/
mkdir -p /var/log/yandex/taxi-personal/
ln -sf /taxi/logs/application-taxi-personal.log /var/log/yandex/taxi-personal/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-personal \
    --fix-userver-client-timeout /etc/yandex/taxi/personal/config.yaml \
    --wait \
       mongo.taxi.yandex:27017 \
       http://configs.taxi.yandex.net/ping \
    --run /usr/bin/yandex-taxi-personal \
        --config /etc/yandex/taxi/personal/config.yaml \
        --init-log /var/log/yandex/taxi-personal/server.log
