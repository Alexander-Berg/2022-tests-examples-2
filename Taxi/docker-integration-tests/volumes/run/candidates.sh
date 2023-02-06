#!/usr/bin/env bash
set -e

mkdir -p /usr/share/yandex/taxi/graph
ln -sf /usr/share/yandex/taxi/graph-test/graph3 /usr/share/yandex/taxi/graph/latest
mkdir -p /usr/share/yandex/taxi/mds_download/categories_bulk_dumps/current

USERVICES_PATH=/arcadia/taxi/uservices
CANDIDATES_PATH=$USERVICES_PATH/build-integration/services/candidates
CANDIDATES_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/candidates
CANDIDATES_DEB_PATH=$USERVICES_PATH/services/candidates/debian

CANDIDATES_BINARY_PATH=
if [ -f "$CANDIDATES_PATH/yandex-taxi-candidates" ]; then
  CANDIDATES_BINARY_PATH="$CANDIDATES_PATH/yandex-taxi-candidates"
elif [ -f "$CANDIDATES_ARCADIA_PATH/yandex-taxi-candidates" ]; then
  CANDIDATES_BINARY_PATH="$CANDIDATES_ARCADIA_PATH/yandex-taxi-candidates"
fi

if [ -f "$CANDIDATES_BINARY_PATH" ]; then
    echo "candidates update package"
    mkdir -p /etc/yandex/taxi/candidates/
    mkdir -p /var/cache/yandex/taxi-candidates/
    rm -rf /etc/yandex/taxi/candidates/*
    ln -s $CANDIDATES_PATH/configs/* /etc/yandex/taxi/candidates/
    cp $CANDIDATES_PATH/config.yaml /etc/yandex/taxi/candidates/
    ln -s $CANDIDATES_PATH/taxi_config_fallback.json /etc/yandex/taxi/candidates/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/candidates/
    ln -s config_vars.production.yaml /etc/yandex/taxi/candidates/config_vars.yaml

    ln -sf $CANDIDATES_DEB_PATH/yandex-taxi-candidates.nginx /etc/nginx/sites-available/yandex-taxi-candidates
    ln -sf $CANDIDATES_DEB_PATH/yandex-taxi-candidates.upstream_list /etc/nginx/conf.d/

    ln -sf $CANDIDATES_PATH/taxi-candidates-stats.py /usr/bin/

    echo "using binary: $CANDIDATES_BINARY_PATH"
    ln -sf $CANDIDATES_BINARY_PATH /usr/bin/
fi

sed -i '/parks-cache:/{n;N;s|.*|            update-interval: 2s\n\            update-types: only-full|}' /etc/yandex/taxi/candidates/config.yaml

mkdir -p /var/log/yandex/taxi-candidates/
mkdir -p /var/lib/yandex/taxi-candidates/
ln -sf /taxi/logs/application-taxi-candidates.log /var/log/yandex/taxi-candidates/server.log

/taxi/tools/run.py \
    --stdout-to-log \
    --nginx yandex-taxi-candidates \
    --fix-userver-client-timeout /etc/yandex/taxi/candidates/config.yaml \
    --syslog \
    --wait \
        mongo.taxi.yandex:27017 \
        memcached.taxi.yandex:11211 \
        redis.taxi.yandex:6379 \
        http://configs.taxi.yandex.net/ping \
    --run /usr/bin/yandex-taxi-candidates \
        --config /etc/yandex/taxi/candidates/config.yaml \
        --init-log /taxi/logs/application-taxi-candidates-init.log
