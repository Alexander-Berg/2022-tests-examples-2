#!/usr/bin/env bash
set -e
CPP_PATH=/taxi/backend-cpp
if [ -d "/arcadia/taxi/backend-cpp" ]; then
  CPP_PATH=/arcadia/taxi/backend-cpp
fi

if [ -f $CPP_PATH/build-integration/driver-protocol/libyandex-taxi-driver-protocol.so ]; then
    mkdir -p etc/fastcgi2/taxi-driver-protocol/
    rm -rf /etc/fastcgi2/taxi-driver-protocol/*
    cp $CPP_PATH/build-integration/driver-protocol/conf/files/* /etc/fastcgi2/taxi-driver-protocol/
    ln -s $CPP_PATH/build-integration/common/conf/files/* /etc/fastcgi2/taxi-driver-protocol/
    ln -sf $CPP_PATH/build-integration/driver-protocol/libyandex-taxi-driver-protocol.so /usr/lib/
    ln -sf /etc/fastcgi2/taxi-driver-protocol/fastcgi.production.conf \
        /etc/fastcgi2/available/taxi-driver-protocol.conf
    ln -sf $CPP_PATH/driver-protocol/debian/yandex-taxi-driver-protocol-nginx-conf.nginx \
        /etc/nginx/sites-available/yandex-taxi-driver-protocol-nginx-conf

    mkdir -p /usr/lib/yandex/taxi-driver-protocol/fallback
    ln -sf $CPP_PATH/build-integration/common/generated/fallback/configs.json \
        /usr/lib/yandex/taxi-driver-protocol/fallback/configs.json
fi

/taxi/tools/run.py \
    --nginx yandex-taxi-driver-protocol-nginx-conf \
    --stdout-to-log \
    --fix-fastcgi-config taxi-driver-protocol \
    --wait \
       mongo.taxi.yandex:27017 \
       redis.taxi.yandex:6379 \
       http://configs.taxi.yandex.net/ping \
    --log-fastcgi-pools 1188 \
    --run /usr/sbin/fastcgi-daemon2 \
        --config=/etc/fastcgi2/available/taxi-driver-protocol.conf
