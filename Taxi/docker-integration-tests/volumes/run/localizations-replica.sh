#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
LOCALIZATIONS_PATH=$USERVICES_PATH/build-integration/services/localizations-replica
LOCALIZATIONS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/localizations-replica
LOCALIZATIONS_DEB_PATH=$USERVICES_PATH/services/localizations-replica/debian

LOCALIZATIONS_BINARY_PATH=
if [ -f "$LOCALIZATIONS_PATH/yandex-taxi-localizations-replica" ]; then
   LOCALIZATIONS_BINARY_PATH="$LOCALIZATIONS_PATH/yandex-taxi-localizations-replica"
elif [ -f "$LOCALIZATIONS_ARCADIA_PATH/yandex-taxi-localizations-replica" ]; then
   LOCALIZATIONS_BINARY_PATH="$LOCALIZATIONS_ARCADIA_PATH/yandex-taxi-localizations-replica"
fi

if [ -f "$LOCALIZATIONS_BINARY_PATH" ]; then
    echo "localizations-replica update package"
    mkdir -p /etc/yandex/taxi/localizations-replica/
    rm -rf /etc/yandex/taxi/localizations-replica/*
    ln -s $LOCALIZATIONS_PATH/configs/* /etc/yandex/taxi/localizations-replica/
    cp $LOCALIZATIONS_PATH/config.yaml /etc/yandex/taxi/localizations-replica/
    ln -s $LOCALIZATIONS_PATH/taxi_config_fallback.json /etc/yandex/taxi/localizations-replica/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/localizations-replica/
    ln -s config_vars.production.yaml /etc/yandex/taxi/localizations-replica/config_vars.yaml

    ln -sf $LOCALIZATIONS_DEB_PATH/yandex-taxi-localizations-replica.nginx /etc/nginx/sites-available/yandex-taxi-localizations-replica
    ln -sf $LOCALIZATIONS_DEB_PATH/yandex-taxi-localizations-replica.upstream_list /etc/nginx/conf.d/

    ln -sf $LOCALIZATIONS_PATH/taxi-localizations-replica-stats.py /usr/bin/

    echo "using binary: $LOCALIZATIONS_BINARY_PATH"
    ln -sf $LOCALIZATIONS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-localizations-replica/
mkdir -p /var/log/yandex/taxi-localizations-replica/
ln -sf /taxi/logs/application-taxi-localizations-replica.log /var/log/yandex/taxi-localizations-replica/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-localizations-replica \
    --fix-userver-client-timeout /etc/yandex/taxi/localizations-replica/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-localizations-replica \
        --config /etc/yandex/taxi/localizations-replica/config.yaml \
        --init-log /var/log/yandex/taxi-localizations-replica/server.log
