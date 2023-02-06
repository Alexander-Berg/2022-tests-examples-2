#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
UNITED_DISPATCH_PATH=$USERVICES_PATH/build-integration/services/united-dispatch
UNITED_DISPATCH_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/united-dispatch
UNITED_DISPATCH_DEB_PATH=$USERVICES_PATH/services/united-dispatch/debian

UNITED_DISPATCH_BINARY_PATH=
if [ -f "$UNITED_DISPATCH_PATH/yandex-taxi-united-dispatch" ]; then
  UNITED_DISPATCH_BINARY_PATH="$UNITED_DISPATCH_PATH/yandex-taxi-united-dispatch"
elif [ -f "$UNITED_DISPATCH_ARCADIA_PATH/yandex-taxi-united-dispatch" ]; then
  UNITED_DISPATCH_BINARY_PATH="$UNITED_DISPATCH_ARCADIA_PATH/yandex-taxi-united-dispatch"
fi

if [ -f "$UNITED_DISPATCH_BINARY_PATH" ]; then
    echo "united-dispatch update package"
    mkdir -p /etc/yandex/taxi/united-dispatch/
    rm -rf /etc/yandex/taxi/united-dispatch/*

    ln -s $UNITED_DISPATCH_PATH/configs/* /etc/yandex/taxi/united-dispatch/
    cp $UNITED_DISPATCH_PATH/config.yaml /etc/yandex/taxi/united-dispatch/
    ln -s $UNITED_DISPATCH_PATH/taxi_config_fallback.json /etc/yandex/taxi/united-dispatch/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/united-dispatch/
    ln -s config_vars.production.yaml /etc/yandex/taxi/united-dispatch/config_vars.yaml

    ln -sf $UNITED_DISPATCH_DEB_PATH/yandex-taxi-united-dispatch.nginx /etc/nginx/sites-available/yandex-taxi-united-dispatch
    ln -sf $UNITED_DISPATCH_DEB_PATH/yandex-taxi-united-dispatch.upstream_list /etc/nginx/conf.d/

    ln -sf $UNITED_DISPATCH_PATH/taxi-united-dispatch-stats.py /usr/bin/

    echo "using binary: $UNITED_DISPATCH_BINARY_PATH"
    ln -sf $UNITED_DISPATCH_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-united-dispatch/
mkdir -p /var/lib/yandex/taxi-united-dispatch/
mkdir -p /var/lib/yandex/taxi-united-dispatch/private/
mkdir -p /var/cache/yandex/taxi-united-dispatch/
ln -sf /taxi/logs/application-taxi-united-dispatch.log /var/log/yandex/taxi-united-dispatch/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-united-dispatch \
    --fix-userver-client-timeout /etc/yandex/taxi/united-dispatch/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-united-dispatch \
        --config /etc/yandex/taxi/united-dispatch/config.yaml \
        --init-log /var/log/yandex/taxi-united-dispatch/server.log
