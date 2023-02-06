#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
CONTRACTOR_ORDERS_POLLING_PATH=$USERVICES_PATH/build-integration/services/contractor-orders-polling
CONTRACTOR_ORDERS_POLLING_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/contractor-orders-polling
CONTRACTOR_ORDERS_POLLING_DEB_PATH=$USERVICES_PATH/services/contractor-orders-polling/debian

CONTRACTOR_ORDERS_POLLING_BINARY_PATH=
if [ -f "$CONTRACTOR_ORDERS_POLLING_PATH/yandex-taxi-contractor-orders-polling" ]; then
  CONTRACTOR_ORDERS_POLLING_BINARY_PATH="$CONTRACTOR_ORDERS_POLLING_PATH/yandex-taxi-contractor-orders-polling"
elif [ -f "$CONTRACTOR_ORDERS_POLLING_ARCADIA_PATH/yandex-taxi-contractor-orders-polling" ]; then
  CONTRACTOR_ORDERS_POLLING_BINARY_PATH="$CONTRACTOR_ORDERS_POLLING_ARCADIA_PATH/yandex-taxi-contractor-orders-polling"
fi

if [ -f "$CONTRACTOR_ORDERS_POLLING_BINARY_PATH" ]; then
    echo "contractor-orders-polling update package"
    mkdir -p /etc/yandex/taxi/contractor-orders-polling/
    rm -rf /etc/yandex/taxi/contractor-orders-polling/*

    ln -s $CONTRACTOR_ORDERS_POLLING_PATH/configs/* /etc/yandex/taxi/contractor-orders-polling/
    cp $CONTRACTOR_ORDERS_POLLING_PATH/config.yaml /etc/yandex/taxi/contractor-orders-polling/
    ln -s $CONTRACTOR_ORDERS_POLLING_PATH/taxi_config_fallback.json /etc/yandex/taxi/contractor-orders-polling/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/contractor-orders-polling/
    ln -s config_vars.production.yaml /etc/yandex/taxi/contractor-orders-polling/config_vars.yaml

    ln -sf $CONTRACTOR_ORDERS_POLLING_DEB_PATH/yandex-taxi-contractor-orders-polling.nginx /etc/nginx/sites-available/yandex-taxi-contractor-orders-polling
    ln -sf $CONTRACTOR_ORDERS_POLLING_DEB_PATH/yandex-taxi-contractor-orders-polling.upstream_list /etc/nginx/conf.d/

    ln -sf $CONTRACTOR_ORDERS_POLLING_PATH/taxi-contractor-orders-polling-stats.py /usr/bin/

    echo "using binary: $CONTRACTOR_ORDERS_POLLING_BINARY_PATH"
    ln -sf $CONTRACTOR_ORDERS_POLLING_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-contractor-orders-polling/
mkdir -p /var/lib/yandex/taxi-contractor-orders-polling/
mkdir -p /var/lib/yandex/taxi-contractor-orders-polling/private/
mkdir -p /var/cache/yandex/taxi-contractor-orders-polling/
ln -sf /taxi/logs/application-taxi-contractor-orders-polling.log /var/log/yandex/taxi-contractor-orders-polling/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-contractor-orders-polling \
    --fix-userver-client-timeout /etc/yandex/taxi/contractor-orders-polling/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-contractor-orders-polling \
        --config /etc/yandex/taxi/contractor-orders-polling/config.yaml \
        --init-log /var/log/yandex/taxi-contractor-orders-polling/server.log
