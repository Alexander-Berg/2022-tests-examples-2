#!/usr/bin/env bash
set -e

if [ -f /taxi/backend/debian/changelog ]; then
    rm -rf /etc/yandex/taxi-cabinet/*
    ln -s /taxi/backend/debian/settings.*.py /etc/yandex/taxi-cabinet/
    ln -s /taxi/backend/debian/djangosettings.*.py /etc/yandex/taxi-cabinet/
    cp -f /taxi/backend/debian/yandex-taxi-cabinet.nginx \
        /etc/nginx/sites-available/yandex-taxi-cabinet

    rm -rf /usr/lib/yandex/taxi-cabinet/*
    mkdir -p /etc/yandex/taxi-cabinet/nginx.conf.d
    ln -s /taxi/backend/debian/nginx.conf.d/idm-cert-check.conf.production /etc/yandex/taxi-cabinet/nginx.conf.d/
    ln -s /etc/yandex/taxi-cabinet/djangosettings.production.py /usr/lib/yandex/taxi-cabinet/djangosettings.py
    ln -s /taxi/backend/taxi-cabinet/* /usr/lib/yandex/taxi-cabinet/
    ln -s /taxi/backend/debian/manage.py /usr/lib/yandex/taxi-cabinet/
    ln -s /taxi/backend/stq_config.py /usr/lib/yandex/taxi-cabinet/
    ln -s /taxi/backend/taxi /usr/lib/yandex/taxi-cabinet/
    ln -s /etc/yandex/taxi-cabinet/settings.production.py /usr/lib/yandex/taxi-cabinet/taxi_settings.py
    ln -s /taxi/backend/taxi_stq /usr/lib/yandex/taxi-cabinet/
    ln -s /taxi/backend/taxi_tasks /usr/lib/yandex/taxi-cabinet/
fi

touch /taxi/logs/application-taxi-cabinet.log
chown www-data /taxi/logs/application-taxi-cabinet.log
chmod 666 /taxi/logs/application-taxi-cabinet.log


/taxi/tools/run.py \
    --stdout-to-log \
    --syslog \
    --https-hosts \
        cabinet.taxi.yandex-team.ru \
        taxi-cabinet.mobile.yandex.ru \
        taxi-cabinet.tst.mobile.yandex.ru \
        taxi-cabinet-unstable.tst.mobile.yandex.ru \
    --nginx yandex-taxi-cabinet \
    --wait \
        mongo.taxi.yandex:27017 \
        http://configs.taxi.yandex.net/ping \
    --run su www-data -s /bin/sh -c \
        '/usr/lib/yandex/taxi-py2/bin/python /usr/lib/yandex/taxi-cabinet/manage.py runfcgi daemonize=false method=threaded socket=/var/run/yandex/taxi-cabinet/fcgi.sock'
