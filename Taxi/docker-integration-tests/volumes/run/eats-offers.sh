#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
EATS_OFFERS_PATH=$USERVICES_PATH/build-integration/services/eats-offers
EATS_OFFERS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/eats-offers
EATS_OFFERS_DEB_PATH=$USERVICES_PATH/services/eats-offers/debian

EATS_OFFERS_BINARY_PATH=
if [ -f "$EATS_OFFERS_PATH/yandex-taxi-eats-offers" ]; then
  EATS_OFFERS_BINARY_PATH="$EATS_OFFERS_PATH/yandex-taxi-eats-offers"
elif [ -f "$EATS_OFFERS_ARCADIA_PATH/yandex-taxi-eats-offers" ]; then
  EATS_OFFERS_BINARY_PATH="$EATS_OFFERS_ARCADIA_PATH/yandex-taxi-eats-offers"
fi

if [ -f "$EATS_OFFERS_BINARY_PATH" ]; then
    echo "eats-offers update package"
    mkdir -p /etc/yandex/taxi/eats-offers/
    rm -rf /etc/yandex/taxi/eats-offers/*

    ln -s $EATS_OFFERS_PATH/configs/* /etc/yandex/taxi/eats-offers/
    cp $EATS_OFFERS_PATH/config.yaml /etc/yandex/taxi/eats-offers/
    ln -s $EATS_OFFERS_PATH/taxi_config_fallback.json /etc/yandex/taxi/eats-offers/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/eats-offers/
    ln -s config_vars.production.yaml /etc/yandex/taxi/eats-offers/config_vars.yaml

    ln -sf $EATS_OFFERS_DEB_PATH/yandex-taxi-eats-offers.nginx /etc/nginx/sites-available/yandex-taxi-eats-offers
    ln -sf $EATS_OFFERS_DEB_PATH/yandex-taxi-eats-offers.upstream_list /etc/nginx/conf.d/

    ln -sf $EATS_OFFERS_PATH/taxi-eats-offers-stats.py /usr/bin/
    echo "using binary: $EATS_OFFERS_BINARY_PATH"
    ln -sf $EATS_OFFERS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-eats-offers/
mkdir -p /var/lib/yandex/taxi-eats-offers/
mkdir -p /var/lib/yandex/taxi-eats-offers/private/
mkdir -p /var/cache/yandex/taxi-eats-offers/
ln -sf /taxi/logs/application-taxi-eats-offers.log /var/log/yandex/taxi-eats-offers/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-eats-offers \
    --fix-userver-client-timeout /etc/yandex/taxi/eats-offers/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-eats-offers \
        --config /etc/yandex/taxi/eats-offers/config.yaml \
        --init-log /var/log/yandex/taxi-eats-offers/server.log
