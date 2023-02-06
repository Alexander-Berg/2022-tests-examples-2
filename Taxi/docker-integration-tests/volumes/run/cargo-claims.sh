#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
CARGO_CLAIMS_PATH=$USERVICES_PATH/build-integration/services/cargo-claims
CARGO_CLAIMS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/cargo-claims
CARGO_CLAIMS_DEB_PATH=$USERVICES_PATH/services/cargo-claims/debian

CARGO_CLAIMS_BINARY_PATH=
if [ -f "$CARGO_CLAIMS_PATH/yandex-taxi-cargo-claims" ]; then
  CARGO_CLAIMS_BINARY_PATH="$CARGO_CLAIMS_PATH/yandex-taxi-cargo-claims"
elif [ -f "$CARGO_CLAIMS_ARCADIA_PATH/yandex-taxi-cargo-claims" ]; then
  CARGO_CLAIMS_BINARY_PATH="$CARGO_CLAIMS_ARCADIA_PATH/yandex-taxi-cargo-claims"
fi

if [ -f "$CARGO_CLAIMS_PATH/yandex-taxi-cargo-claims" ]; then
    echo "cargo-claims update package"
    mkdir -p /etc/yandex/taxi/cargo-claims/
    rm -rf /etc/yandex/taxi/cargo-claims/*

    ln -s $CARGO_CLAIMS_PATH/configs/* /etc/yandex/taxi/cargo-claims/
    cp $CARGO_CLAIMS_PATH/config.yaml /etc/yandex/taxi/cargo-claims/
    ln -s $CARGO_CLAIMS_PATH/taxi_config_fallback.json /etc/yandex/taxi/cargo-claims/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/cargo-claims/
    ln -s config_vars.production.yaml /etc/yandex/taxi/cargo-claims/config_vars.yaml

    ln -sf $CARGO_CLAIMS_DEB_PATH/yandex-taxi-cargo-claims.nginx /etc/nginx/sites-available/yandex-taxi-cargo-claims
    ln -sf $CARGO_CLAIMS_DEB_PATH/yandex-taxi-cargo-claims.upstream_list /etc/nginx/conf.d/

    ln -sf $CARGO_CLAIMS_PATH/taxi-cargo-claims-stats.py /usr/bin/

    echo "using binary: $CARGO_CLAIMS_BINARY_PATH"
    ln -sf $CARGO_CLAIMS_PATH/yandex-taxi-cargo-claims /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-cargo-claims/
mkdir -p /var/lib/yandex/taxi-cargo-claims/
mkdir -p /var/lib/yandex/taxi-cargo-claims/private/
mkdir -p /var/cache/yandex/taxi-cargo-claims/
ln -sf /taxi/logs/application-taxi-cargo-claims.log /var/log/yandex/taxi-cargo-claims/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-cargo-claims \
    --fix-userver-client-timeout /etc/yandex/taxi/cargo-claims/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-cargo-claims \
        --config /etc/yandex/taxi/cargo-claims/config.yaml \
        --init-log /var/log/yandex/taxi-cargo-claims/server.log
