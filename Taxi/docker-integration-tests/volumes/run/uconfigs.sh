#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
UCONFIGS_PATH=$USERVICES_PATH/build-integration/services/uconfigs
UCONFIGS_UNIT_PATH=$UCONFIGS_PATH/units/uconfigs
UCONFIGS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/uconfigs
UCONFIGS_DEB_PATH=$USERVICES_PATH/services/uconfigs/debian
UCONFIGS_CACHE_PATH=/var/cache/yandex/taxi-uconfigs/userver-cache-dumps/configs-defaults-cache
DEFAULTS_CACHE_PATH=$UCONFIGS_CACHE_PATH/$(date +%FT%H%M%S.000000Z)-v0

UCONFIGS_BINARY_PATH=
if [ -f "$UCONFIGS_PATH/yandex-taxi-uconfigs" ]; then
  UCONFIGS_BINARY_PATH="$UCONFIGS_PATH/yandex-taxi-uconfigs"
elif [ -f "$UCONFIGS_ARCADIA_PATH/yandex-taxi-uconfigs" ]; then
  UCONFIGS_BINARY_PATH="$UCONFIGS_ARCADIA_PATH/yandex-taxi-uconfigs"
fi

if [ -f "$UCONFIGS_BINARY_PATH" ]; then
    echo "uconfigs update package"
    mkdir -p /etc/yandex/taxi/uconfigs/
    rm -rf /etc/yandex/taxi/uconfigs/*

    if [ -e $UCONFIGS_PATH/config.yaml ]; then
        ln -s $UCONFIGS_PATH/configs/* /etc/yandex/taxi/uconfigs/
        cp $UCONFIGS_PATH/config.yaml /etc/yandex/taxi/uconfigs/
    else
        ln -s $UCONFIGS_UNIT_PATH/configs/* /etc/yandex/taxi/uconfigs/
        cp $UCONFIGS_UNIT_PATH/config.yaml /etc/yandex/taxi/uconfigs/
    fi

    ln -s $UCONFIGS_PATH/taxi_config_fallback.json /etc/yandex/taxi/uconfigs/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/uconfigs/
    ln -s config_vars.production.yaml /etc/yandex/taxi/uconfigs/config_vars.yaml

    ln -sf $UCONFIGS_DEB_PATH/yandex-taxi-uconfigs.nginx /etc/nginx/sites-available/yandex-taxi-uconfigs
    ln -sf $UCONFIGS_DEB_PATH/yandex-taxi-uconfigs.upstream_list /etc/nginx/conf.d/

    ln -sf $UCONFIGS_PATH/taxi-uconfigs-stats.py /usr/bin/ || \
        ln -sf $UCONFIGS_UNIT_PATH/taxi-uconfigs-stats.py /usr/bin/

    echo "using binary: $UCONFIGS_BINARY_PATH"
    ln -sf $UCONFIGS_BINARY_PATH /usr/bin/
fi

sed -i 's/first-update-mode: best-effort/first-update-mode: skip/' /etc/yandex/taxi/uconfigs/config_vars.yaml

mkdir -p /var/log/yandex/taxi-uconfigs/
mkdir -p /var/lib/yandex/taxi-uconfigs/
mkdir -p /var/lib/yandex/taxi-uconfigs/private/
ln -sf /taxi/logs/application-taxi-uconfigs.log /var/log/yandex/taxi-uconfigs/server.log

mkdir -p $UCONFIGS_CACHE_PATH
cp /taxi/cache_dumps/config_defaults.json $DEFAULTS_CACHE_PATH
chmod 0444 $DEFAULTS_CACHE_PATH

/taxi/tools/run.py \
    --nginx yandex-taxi-uconfigs \
    --fix-userver-client-timeout /etc/yandex/taxi/uconfigs/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-uconfigs \
        --config /etc/yandex/taxi/uconfigs/config.yaml \
        --init-log /var/log/yandex/taxi-uconfigs/server.log
