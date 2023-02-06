#!/usr/bin/env bash
set -e
CPP_PATH=/taxi/backend-cpp
if [ -d "/arcadia/taxi/backend-cpp" ]; then
  CPP_PATH=/arcadia/taxi/backend-cpp
fi

if [ -f $CPP_PATH/build-integration/feedback/libyandex-taxi-feedback.so ]; then
    mkdir -p /etc/fastcgi2/taxi-feedback/
    rm -rf /etc/fastcgi2/taxi-feedback/*
    cp $CPP_PATH/build-integration/feedback/conf/files/* /etc/fastcgi2/taxi-feedback/
    ln -s $CPP_PATH/build-integration/common/conf/files/* /etc/fastcgi2/taxi-feedback/
    ln -sf $CPP_PATH/build-integration/feedback/libyandex-taxi-feedback.so /usr/lib/
    ln -sf /etc/fastcgi2/taxi-feedback/fastcgi.production.conf \
        /etc/fastcgi2/available/taxi-feedback.conf
    ln -sf $CPP_PATH/feedback/debian/yandex-taxi-feedback-nginx-conf.nginx \
        /etc/nginx/sites-available/yandex-taxi-feedback-nginx-conf

    mkdir -p /usr/lib/yandex/taxi-feedback/fallback
    ln -sf $CPP_PATH/build-integration/common/generated/fallback/configs.json \
        /usr/lib/yandex/taxi-feedback/fallback/configs.json
fi

/taxi/tools/run.py \
    --nginx yandex-taxi-feedback-nginx-conf \
    --stdout-to-log \
    --wait \
       mongo.taxi.yandex:27017 \
       http://configs.taxi.yandex.net/ping \
    --log-fastcgi-pools 1188 \
    --fix-fastcgi-config taxi-feedback \
    --run /usr/sbin/fastcgi-daemon2 --config=/etc/fastcgi2/available/taxi-feedback.conf
