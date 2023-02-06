#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
LOOKUP_PATH=$USERVICES_PATH/build-integration/services/lookup
LOOKUP_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/lookup
LOOKUP_DEB_PATH=$USERVICES_PATH/services/lookup/debian

LOOKUP_BINARY_PATH=
if [ -f "$LOOKUP_PATH/yandex-taxi-lookup" ]; then
  LOOKUP_BINARY_PATH="$LOOKUP_PATH/yandex-taxi-lookup"
elif [ -f "$LOOKUP_ARCADIA_PATH/yandex-taxi-lookup" ]; then
  LOOKUP_BINARY_PATH="$LOOKUP_ARCADIA_PATH/yandex-taxi-lookup"
fi

if [ -f "$LOOKUP_BINARY_PATH" ]; then
    echo "lookup update package"
    mkdir -p /etc/yandex/taxi/lookup/
    rm -rf /etc/yandex/taxi/lookup/*
    ln -s $LOOKUP_PATH/configs/* /etc/yandex/taxi/lookup/
    cp $LOOKUP_PATH/config.yaml /etc/yandex/taxi/lookup/
    ln -s $LOOKUP_PATH/taxi_config_fallback.json /etc/yandex/taxi/lookup/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/lookup/
    ln -s config_vars.production.yaml /etc/yandex/taxi/lookup/config_vars.yaml

    ln -sf $LOOKUP_DEB_PATH/yandex-taxi-lookup.nginx /etc/nginx/sites-available/yandex-taxi-lookup
    ln -sf $LOOKUP_DEB_PATH/yandex-taxi-lookup.upstream_list /etc/nginx/conf.d/

    ln -sf $LOOKUP_PATH/taxi-lookup-stats.py /usr/bin/

    echo "using binary: $LOOKUP_BINARY_PATH"
    ln -sf $LOOKUP_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-lookup/
mkdir -p /var/log/yandex/taxi-lookup/
ln -sf /taxi/logs/application-taxi-lookup.log /var/log/yandex/taxi-lookup/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-lookup \
    --fix-userver-client-timeout /etc/yandex/taxi/lookup/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-lookup \
        --config /etc/yandex/taxi/lookup/config.yaml \
        --init-log /var/log/yandex/taxi-lookup/server.log
