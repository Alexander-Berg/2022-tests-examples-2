#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_P13N_PATH=$USERVICES_PATH/build-integration/services/grocery-p13n
GROCERY_P13N_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-p13n
GROCERY_P13N_DEB_PATH=$USERVICES_PATH/services/grocery-p13n/debian

GROCERY_P13N_BINARY_PATH=
if [ -f "$GROCERY_P13N_PATH/yandex-taxi-grocery-p13n" ]; then
  GROCERY_P13N_BINARY_PATH="$GROCERY_P13N_PATH/yandex-taxi-grocery-p13n"
elif [ -f "$GROCERY_P13N_ARCADIA_PATH/yandex-taxi-grocery-p13n" ]; then
  GROCERY_P13N_BINARY_PATH="$GROCERY_P13N_ARCADIA_PATH/yandex-taxi-grocery-p13n"
fi

if [ -f "$GROCERY_P13N_BINARY_PATH" ]; then
    echo "grocery-p13n update package"
    mkdir -p /etc/yandex/taxi/grocery-p13n/
    rm -rf /etc/yandex/taxi/grocery-p13n/*

    ln -s $GROCERY_P13N_PATH/configs/* /etc/yandex/taxi/grocery-p13n/
    cp $GROCERY_P13N_PATH/config.yaml /etc/yandex/taxi/grocery-p13n/
    ln -s $GROCERY_P13N_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-p13n/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-p13n/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-p13n/config_vars.yaml

    ln -sf $GROCERY_P13N_DEB_PATH/yandex-taxi-grocery-p13n.nginx /etc/nginx/sites-available/yandex-taxi-grocery-p13n
    ln -sf $GROCERY_P13N_DEB_PATH/yandex-taxi-grocery-p13n.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_P13N_PATH/taxi-grocery-p13n-stats.py /usr/bin/
    echo "using binary: $GROCERY_P13N_BINARY_PATH"
    ln -sf $GROCERY_P13N_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-p13n/
mkdir -p /var/lib/yandex/taxi-grocery-p13n/
mkdir -p /var/lib/yandex/taxi-grocery-p13n/private/
mkdir -p /var/cache/yandex/taxi-grocery-p13n/
ln -sf /taxi/logs/application-taxi-grocery-p13n.log /var/log/yandex/taxi-grocery-p13n/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-p13n \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-p13n/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-p13n \
        --config /etc/yandex/taxi/grocery-p13n/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-p13n/server.log
