#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
ORDER_CORE_PATH=$USERVICES_PATH/build-integration/services/order-core
ORDER_CORE_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/order-core
ORDER_CORE_DEB_PATH=$USERVICES_PATH/services/order-core/debian

ORDER_CORE_BINARY_PATH=
if [ -f "$ORDER_CORE_PATH/yandex-taxi-order-core" ]; then
  ORDER_CORE_BINARY_PATH="$ORDER_CORE_PATH/yandex-taxi-order-core"
elif [ -f "$ORDER_CORE_ARCADIA_PATH/yandex-taxi-order-core" ]; then
  ORDER_CORE_BINARY_PATH="$ORDER_CORE_ARCADIA_PATH/yandex-taxi-order-core"
fi

if [ -f "$ORDER_CORE_BINARY_PATH" ]; then
    echo "order-core update package"
    mkdir -p /etc/yandex/taxi/order-core/
    rm -rf /etc/yandex/taxi/order-core/*

    ln -s $ORDER_CORE_PATH/configs/* /etc/yandex/taxi/order-core/
    cp $ORDER_CORE_PATH/config.yaml /etc/yandex/taxi/order-core/
    ln -s $ORDER_CORE_PATH/taxi_config_fallback.json /etc/yandex/taxi/order-core/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/order-core/
    ln -s config_vars.production.yaml /etc/yandex/taxi/order-core/config_vars.yaml

    ln -sf $ORDER_CORE_DEB_PATH/yandex-taxi-order-core.nginx /etc/nginx/sites-available/yandex-taxi-order-core
    ln -sf $ORDER_CORE_DEB_PATH/yandex-taxi-order-core.upstream_list /etc/nginx/conf.d/

    ln -sf $ORDER_CORE_PATH/taxi-order-core-stats.py /usr/bin/

    echo "using binary: $ORDER_CORE_BINARY_PATH"
    ln -sf $ORDER_CORE_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-order-core/
mkdir -p /var/lib/yandex/taxi-order-core/
mkdir -p /var/lib/yandex/taxi-order-core/private/
mkdir -p /var/cache/yandex/taxi-order-core/
ln -sf /taxi/logs/application-taxi-order-core.log /var/log/yandex/taxi-order-core/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-order-core \
    --fix-userver-client-timeout /etc/yandex/taxi/order-core/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-order-core \
        --config /etc/yandex/taxi/order-core/config.yaml \
        --init-log /var/log/yandex/taxi-order-core/server.log
