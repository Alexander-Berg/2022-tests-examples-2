#!/usr/bin/env bash
set -e
CPP_PATH=/taxi/backend-cpp
if [ -d "/arcadia/taxi/backend-cpp" ]; then
  CPP_PATH=/arcadia/taxi/backend-cpp
fi

if [ -f $CPP_PATH/build-integration/protocol/lib/libyandex-taxi-protocol-cxx.so ]; then
    mkdir -p /etc/fastcgi2/taxi-protocol/
    rm -rf /etc/fastcgi2/taxi-protocol/*
    cp  $CPP_PATH/build-integration/protocol/lib/conf/files/* /etc/fastcgi2/taxi-protocol/
    ln -s $CPP_PATH/build-integration/common/conf/files/* /etc/fastcgi2/taxi-protocol/
    ln -sf $CPP_PATH/build-integration/protocol/lib/libyandex-taxi-protocol-cxx.so /usr/lib/
    ln -sf $CPP_PATH/protocol/debian/yandex-taxi-protocol-nginx-conf.nginx \
        /etc/nginx/sites-available/yandex-taxi-protocol-nginx-conf
    ln -sf /etc/fastcgi2/taxi-protocol/fastcgi.production.conf \
        /etc/fastcgi2/available/taxi-protocol.conf

    mkdir -p /usr/lib/yandex/taxi-protocol/fallback
    ln -sf $CPP_PATH/build-integration/common/generated/fallback/configs.json \
        /usr/lib/yandex/taxi-protocol/fallback/configs.json
fi

/taxi/tools/run.py \
    --https-hosts \
        taxi-protocol.taxi.dev.yandex.net \
        taxi-protocol.taxi.tst.yandex.net \
        taxi-protocol.taxi.yandex.net \
        taxi-protocol-l7.taxi.yandex.net \
        taxi-utils.taxi.yandex.net \
        taxi-utils-l7.taxi.yandex.net \
        taximeter-api.taxi.yandex.net \
    --nginx yandex-taxi-protocol-nginx-conf \
    --stdout-to-log \
    --fix-fastcgi-config taxi-protocol \
    --log-fastcgi-pools 1188 \
    --wait \
       mongo.taxi.yandex:27017 \
       http://configs.taxi.yandex.net/ping \
    --run /usr/sbin/fastcgi-daemon2 \
        --config=/etc/fastcgi2/available/taxi-protocol.conf
