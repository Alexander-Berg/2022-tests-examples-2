#!/usr/bin/env bash
set -e
CPP_PATH=/taxi/backend-cpp
if [ -d "/arcadia/taxi/backend-cpp" ]; then
  CPP_PATH=/arcadia/taxi/backend-cpp
fi

if [ -f $CPP_PATH/build-integration/parks/libyandex-taxi-parks.so ]; then
    mkdir -p /etc/fastcgi2/taxi-parks/
    rm -rf /etc/fastcgi2/taxi-parks/*
    cp $CPP_PATH/build-integration/parks/conf/files/* /etc/fastcgi2/taxi-parks/
    ln -s $CPP_PATH/build-integration/common/conf/files/* /etc/fastcgi2/taxi-parks/
    ln -sf $CPP_PATH/build-integration/parks/libyandex-taxi-parks.so /usr/lib/
    ln -sf /etc/fastcgi2/taxi-parks/fastcgi.production.conf \
        /etc/fastcgi2/available/taxi-parks.conf
    ln -sf $CPP_PATH/parks/debian/yandex-taxi-parks-nginx-conf.nginx \
        /etc/nginx/sites-available/yandex-taxi-parks-nginx-conf

    mkdir -p /usr/lib/yandex/taxi-parks/fallback
    ln -sf $CPP_PATH/build-integration/common/generated/fallback/configs.json \
        /usr/lib/yandex/taxi-parks/fallback/configs.json
fi

/taxi/tools/run.py \
    --nginx yandex-taxi-parks-nginx-conf \
    --stdout-to-log \
    --fix-fastcgi-config taxi-parks \
    --wait \
       mongo.taxi.yandex:27017 \
       http://configs.taxi.yandex.net/ping \
    --log-fastcgi-pools 1188 \
    --run /usr/sbin/fastcgi-daemon2 \
        --config=/etc/fastcgi2/available/taxi-parks.conf
