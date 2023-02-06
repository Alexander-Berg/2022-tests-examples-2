#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
PARKS_REPLICA_PATH=$USERVICES_PATH/build-integration/services/parks-replica
PARKS_REPLICA_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/parks-replica
PARKS_REPLICA_DEB_PATH=$USERVICES_PATH/services/parks-replica/debian

PARKS_REPLICA_BINARY_PATH=
if [ -f "$PARKS_REPLICA_PATH/yandex-taxi-parks-replica" ]; then
  PARKS_REPLICA_BINARY_PATH="$PARKS_REPLICA_PATH/yandex-taxi-parks-replica"
elif [ -f "$PARKS_REPLICA_ARCADIA_PATH/yandex-taxi-parks-replica" ]; then
  PARKS_REPLICA_BINARY_PATH="$PARKS_REPLICA_ARCADIA_PATH/yandex-taxi-parks-replica"
fi

if [ -f "$PARKS_REPLICA_BINARY_PATH" ]; then
    echo "parks-replica update package"
    mkdir -p /etc/yandex/taxi/parks-replica/
    rm -rf /etc/yandex/taxi/parks-replica/*
    ln -s $PARKS_REPLICA_PATH/configs/* /etc/yandex/taxi/parks-replica/
    cp $PARKS_REPLICA_PATH/config.yaml /etc/yandex/taxi/parks-replica/
    ln -s $PARKS_REPLICA_PATH/taxi_config_fallback.json /etc/yandex/taxi/parks-replica/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/parks-replica/
    ln -s config_vars.production.yaml /etc/yandex/taxi/parks-replica/config_vars.yaml

    ln -sf $PARKS_REPLICA_DEB_PATH/yandex-taxi-parks-replica.nginx /etc/nginx/sites-available/yandex-taxi-parks-replica
    ln -sf $PARKS_REPLICA_DEB_PATH/yandex-taxi-parks-replica.upstream_list /etc/nginx/conf.d/

    ln -sf $PARKS_REPLICA_PATH/taxi-parks-replica-stats.py /usr/bin/

    echo "using binary: $PARKS_REPLICA_BINARY_PATH"
    ln -sf $PARKS_REPLICA_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-parks-replica/
mkdir -p /var/log/yandex/taxi-parks-replica/
ln -sf /taxi/logs/application-taxi-parks-replica.log /var/log/yandex/taxi-parks-replica/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-parks-replica \
    --fix-userver-client-timeout /etc/yandex/taxi/parks-replica/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-parks-replica \
        --config /etc/yandex/taxi/parks-replica/config.yaml \
        --init-log /var/log/yandex/taxi-parks-replica/server.log
