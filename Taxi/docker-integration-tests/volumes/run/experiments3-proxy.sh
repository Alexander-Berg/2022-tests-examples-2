#!/usr/bin/env bash
set -e
CPP_PATH=/taxi/backend-cpp
if [ -d "/arcadia/taxi/backend-cpp" ]; then
  CPP_PATH=/arcadia/taxi/backend-cpp
fi

if [ -f $CPP_PATH/build-integration/experiments3-proxy/libyandex-taxi-experiments3-proxy.so ]; then
    mkdir -p /etc/fastcgi2/taxi-experiments3-proxy/
    rm -rf /etc/fastcgi2/taxi-experiments3-proxy/*
    cp $CPP_PATH/build-integration/experiments3-proxy/conf/files/* /etc/fastcgi2/taxi-experiments3-proxy/
    ln -s $CPP_PATH/build-integration/common/conf/files/* /etc/fastcgi2/taxi-experiments3-proxy/
    ln -sf $CPP_PATH/build-integration/experiments3-proxy/libyandex-taxi-experiments3-proxy.so /usr/lib/
    ln -sf /etc/fastcgi2/taxi-experiments3-proxy/fastcgi.production.conf \
        /etc/fastcgi2/available/taxi-experiments3-proxy.conf
    ln -sf $CPP_PATH/experiments3-proxy/debian/yandex-taxi-experiments3-proxy-nginx-conf.nginx \
        /etc/nginx/sites-available/yandex-taxi-experiments3-proxy-nginx-conf

    mkdir -p /usr/lib/yandex/taxi-experiments3-proxy/fallback
    ln -sf $CPP_PATH/build-integration/common/generated/fallback/configs.json \
        /usr/lib/yandex/taxi-experiments3-proxy/fallback/configs.json
fi
/taxi/tools/run.py \
    --nginx yandex-taxi-experiments3-proxy-nginx-conf \
    --stdout-to-log \
    --wait \
        http://exp.taxi.yandex.net/ping \
        http://configs.taxi.yandex.net/ping \
    --log-fastcgi-pools 1188 \
    --fix-fastcgi-config taxi-experiments3-proxy \
    --run /usr/sbin/fastcgi-daemon2 --config=/etc/fastcgi2/available/taxi-experiments3-proxy.conf
