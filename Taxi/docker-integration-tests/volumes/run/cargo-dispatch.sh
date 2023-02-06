#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
CARGO_DISPATCH_PATH=$USERVICES_PATH/build-integration/services/cargo-dispatch
CARGO_DISPATCH_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/cargo-dispatch
CARGO_DISPATCH_DEB_PATH=$USERVICES_PATH/services/cargo-dispatch/debian

CARGO_DISPATCH_BINARY_PATH=
if [ -f "$CARGO_DISPATCH_PATH/yandex-taxi-cargo-dispatch" ]; then
  CARGO_DISPATCH_BINARY_PATH="$CARGO_DISPATCH_PATH/yandex-taxi-cargo-dispatch"
elif [ -f "$CARGO_DISPATCH_ARCADIA_PATH/yandex-taxi-cargo-dispatch" ]; then
  CARGO_DISPATCH_BINARY_PATH="$CARGO_DISPATCH_ARCADIA_PATH/yandex-taxi-cargo-dispatch"
fi

if [ -f "$CARGO_DISPATCH_PATH/yandex-taxi-cargo-dispatch" ]; then
    echo "cargo-dispatch update package"
    mkdir -p /etc/yandex/taxi/cargo-dispatch/
    rm -rf /etc/yandex/taxi/cargo-dispatch/*

    ln -s $CARGO_DISPATCH_PATH/configs/* /etc/yandex/taxi/cargo-dispatch/
    cp $CARGO_DISPATCH_PATH/config.yaml /etc/yandex/taxi/cargo-dispatch/
    ln -s $CARGO_DISPATCH_PATH/taxi_config_fallback.json /etc/yandex/taxi/cargo-dispatch/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/cargo-dispatch/
    ln -s config_vars.production.yaml /etc/yandex/taxi/cargo-dispatch/config_vars.yaml

    ln -sf $CARGO_DISPATCH_DEB_PATH/yandex-taxi-cargo-dispatch.nginx /etc/nginx/sites-available/yandex-taxi-cargo-dispatch
    ln -sf $CARGO_DISPATCH_DEB_PATH/yandex-taxi-cargo-dispatch.upstream_list /etc/nginx/conf.d/

    ln -sf $CARGO_DISPATCH_PATH/taxi-cargo-dispatch-stats.py /usr/bin/

    echo "using binary: $CARGO_DISPATCH_BINARY_PATH"
    ln -sf $CARGO_DISPATCH_PATH/yandex-taxi-cargo-dispatch /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-cargo-dispatch/
mkdir -p /var/lib/yandex/taxi-cargo-dispatch/
mkdir -p /var/lib/yandex/taxi-cargo-dispatch/private/
mkdir -p /var/cache/yandex/taxi-cargo-dispatch/
ln -sf /taxi/logs/application-taxi-cargo-dispatch.log /var/log/yandex/taxi-cargo-dispatch/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-cargo-dispatch \
    --fix-userver-client-timeout /etc/yandex/taxi/cargo-dispatch/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-cargo-dispatch \
        --config /etc/yandex/taxi/cargo-dispatch/config.yaml \
        --init-log /var/log/yandex/taxi-cargo-dispatch/server.log
