#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
PERSUGGEST_PATH=$USERVICES_PATH/build-integration/services/persuggest
PERSUGGEST_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/persuggest
PERSUGGEST_DEB_PATH=$USERVICES_PATH/services/persuggest/debian

PERSUGGEST_BINARY_PATH=
if [ -f "$PERSUGGEST_PATH/yandex-taxi-persuggest" ]; then
  PERSUGGEST_BINARY_PATH="$PERSUGGEST_PATH/yandex-taxi-persuggest"
elif [ -f "$PERSUGGEST_ARCADIA_PATH/yandex-taxi-persuggest" ]; then
  PERSUGGEST_BINARY_PATH="$PERSUGGEST_ARCADIA_PATH/yandex-taxi-persuggest"
fi

if [ -f "$PERSUGGEST_BINARY_PATH" ]; then
    echo "persuggest update package"
    mkdir -p /etc/yandex/taxi/persuggest/
    rm -rf /etc/yandex/taxi/persuggest/*
    ln -s $PERSUGGEST_PATH/configs/* /etc/yandex/taxi/persuggest/
    cp $PERSUGGEST_PATH/config.yaml /etc/yandex/taxi/persuggest/
    ln -s $PERSUGGEST_PATH/taxi_config_fallback.json /etc/yandex/taxi/persuggest/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/persuggest/
    ln -s config_vars.production.yaml /etc/yandex/taxi/persuggest/config_vars.yaml

    ln -sf $PERSUGGEST_DEB_PATH/yandex-taxi-persuggest.nginx /etc/nginx/sites-available/yandex-taxi-persuggest
    ln -sf $PERSUGGEST_DEB_PATH/yandex-taxi-persuggest.upstream_list /etc/nginx/conf.d/

    ln -sf $PERSUGGEST_PATH/taxi-persuggest-stats.py /usr/bin/

    echo "using binary: $PERSUGGEST_BINARY_PATH"
    ln -sf $PERSUGGEST_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-persuggest/
mkdir -p /var/log/yandex/taxi-persuggest/
ln -sf /taxi/logs/application-taxi-persuggest.log /var/log/yandex/taxi-persuggest/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-persuggest \
    --fix-userver-client-timeout /etc/yandex/taxi/persuggest/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-persuggest \
        --config /etc/yandex/taxi/persuggest/config.yaml \
        --init-log /var/log/yandex/taxi-persuggest/server.log
