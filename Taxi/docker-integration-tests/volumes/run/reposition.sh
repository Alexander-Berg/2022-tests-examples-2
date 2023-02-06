#!/usr/bin/env bash
set -e
CPP_PATH=/taxi/backend-cpp
if [ -d "/arcadia/taxi/backend-cpp" ]; then
  CPP_PATH=/arcadia/taxi/backend-cpp
fi

if [ -f $CPP_PATH/build-integration/reposition/libyandex-taxi-reposition.so ]; then
    mkdir -p /etc/fastcgi2/taxi-reposition/
    rm -rf /etc/fastcgi2/taxi-reposition/*
    cp $CPP_PATH/build-integration/reposition/conf/files/* /etc/fastcgi2/taxi-reposition/
    ln -s $CPP_PATH/build-integration/common/conf/files/* /etc/fastcgi2/taxi-reposition/
    ln -sf $CPP_PATH/build-integration/reposition/libyandex-taxi-reposition.so /usr/lib/
    ln -sf /etc/fastcgi2/taxi-reposition/fastcgi.production.conf \
        /etc/fastcgi2/available/taxi-reposition.conf

    ln -sf $CPP_PATH/reposition/debian/yandex-taxi-reposition-nginx-conf.nginx \
        /etc/nginx/sites-available/yandex-taxi-reposition-nginx-conf

    mkdir -p /usr/lib/yandex/taxi-reposition/fallback
    ln -sf $CPP_PATH/build-integration/common/generated/fallback/configs.json \
        /usr/lib/yandex/taxi-reposition/fallback/configs.json

    pgmigrate -c "host=pgaas.mail.yandex.net port=5432 user=user password=password dbname=dbreposition" -t latest -d $CPP_PATH/reposition/db/reposition migrate
else
    pgmigrate -c "host=pgaas.mail.yandex.net port=5432 user=user password=password dbname=dbreposition" -t latest -d /var/lib/yandex/taxi/db/reposition/ migrate
fi


/taxi/tools/run.py \
    --nginx yandex-taxi-reposition-nginx-conf \
    --stdout-to-log \
    --wait \
        mongo.taxi.yandex:27017 \
        http://configs.taxi.yandex.net/ping \
        http://mock-server.yandex.net/ping/ \
        postgresql:dbreposition \
    --log-fastcgi-pools 1188 \
    --fix-fastcgi-config taxi-reposition \
    --run /usr/sbin/fastcgi-daemon2 --config=/etc/fastcgi2/available/taxi-reposition.conf
