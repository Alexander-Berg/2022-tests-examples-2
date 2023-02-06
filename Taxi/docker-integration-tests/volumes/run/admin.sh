#!/usr/bin/env bash
set -e

if [ -f /taxi/backend/debian/changelog ]; then
    mkdir -p /etc/yandex/taxi-admin/
    rm -rf /etc/yandex/taxi-admin/*
    ln -s /taxi/backend/debian/settings.*.py /etc/yandex/taxi-admin/
    ln -s /taxi/backend/debian/djangosettings.*.py /etc/yandex/taxi-admin/
    ln -sf /taxi/backend/debian/yandex-taxi-admin.nginx \
        /etc/nginx/sites-available/yandex-taxi-admin

    mkdir -p /etc/yandex/taxi-admin/nginx.conf.d
    ln -s /taxi/backend/debian/nginx.conf.d/idm-cert-check.conf.production /etc/yandex/taxi-admin/nginx.conf.d/

    mkdir -p /usr/lib/yandex/taxi-admin/
    rm -rf /usr/lib/yandex/taxi-admin/*
    mkdir -p /var/run/yandex/taxi-admin/
    chown -R www-data:www-data /var/run/yandex/taxi-admin
    mkdir -p /var/cache/yandex/taxi/configs/
    chown -R www-data:www-data /var/cache/yandex/taxi/configs
    ln -s /etc/yandex/taxi-admin/djangosettings.production.py /usr/lib/yandex/taxi-admin/djangosettings.py
    ln -s /taxi/backend/taxi-admin/* /usr/lib/yandex/taxi-admin/
    ln -s /taxi/backend/debian/manage.py /usr/lib/yandex/taxi-admin/
    ln -s /taxi/backend/stq_config.py /usr/lib/yandex/taxi-admin/
    ln -s /taxi/backend/taxi /usr/lib/yandex/taxi-admin/
    ln -s /etc/yandex/taxi-admin/settings.production.py /usr/lib/yandex/taxi-admin/taxi_settings.py
    ln -s /taxi/backend/taxi_stq /usr/lib/yandex/taxi-admin/
    ln -s /taxi/backend/taxi_tasks /usr/lib/yandex/taxi-admin/
    touch /var/run/yandex/taxi-admin/fcgi.sock
    touch /var/run/yandex/taxi-admin/fcgi.pid

    mkdir -p /usr/lib/yandex/taxi-admin-yt-queries/
    rm -rf /usr/lib/yandex/taxi-admin-yt-queries/*
    mkdir -p /var/run/yandex/taxi-admin-yt-queries/
    chown -R www-data:www-data /var/run/yandex/taxi-admin-yt-queries
    ln -s /etc/yandex/taxi-admin/djangosettings.production.py /usr/lib/yandex/taxi-admin-yt-queries/djangosettings.py
    ln -s /taxi/backend/taxi-admin/* /usr/lib/yandex/taxi-admin-yt-queries/
    ln -s /taxi/backend/debian/manage.py /usr/lib/yandex/taxi-admin-yt-queries/
    ln -s /taxi/backend/stq_config.py /usr/lib/yandex/taxi-admin-yt-queries/
    ln -s /taxi/backend/taxi /usr/lib/yandex/taxi-admin-yt-queries/
    ln -s /etc/yandex/taxi-admin/settings.production.py /usr/lib/yandex/taxi-admin-yt-queries/taxi_settings.py
    ln -s /taxi/backend/taxi_stq /usr/lib/yandex/taxi-admin-yt-queries/
    ln -s /taxi/backend/taxi_tasks /usr/lib/yandex/taxi-admin-yt-queries/
    touch /var/run/yandex/taxi-admin-yt-queries/fcgi.sock
    touch /var/run/yandex/taxi-admin-yt-queries/fcgi.pid

    mkdir -p /usr/lib/yandex/taxi-admin-slow-queries/
    rm -rf /usr/lib/yandex/taxi-admin-slow-queries/*
    mkdir -p /var/run/yandex/taxi-admin-slow-queries/
    chown -R www-data:www-data /var/run/yandex/taxi-admin-slow-queries
    ln -s /etc/yandex/taxi-admin/djangosettings.production.py /usr/lib/yandex/taxi-admin-slow-queries/djangosettings.py
    ln -s /taxi/backend/taxi-admin/* /usr/lib/yandex/taxi-admin-slow-queries/
    ln -s /taxi/backend/debian/manage.py /usr/lib/yandex/taxi-admin-slow-queries/
    ln -s /taxi/backend/stq_config.py /usr/lib/yandex/taxi-admin-slow-queries/
    ln -s /taxi/backend/taxi /usr/lib/yandex/taxi-admin-slow-queries/
    ln -s /etc/yandex/taxi-admin/settings.production.py /usr/lib/yandex/taxi-admin-slow-queries/taxi_settings.py
    ln -s /taxi/backend/taxi_stq /usr/lib/yandex/taxi-admin-slow-queries/
    ln -s /taxi/backend/taxi_tasks /usr/lib/yandex/taxi-admin-slow-queries/
    touch /var/run/yandex/taxi-admin-slow-queries/fcgi.sock
    touch /var/run/yandex/taxi-admin-slow-queries/fcgi.pid
fi

touch /taxi/logs/application-taxi-admin.log
chown www-data /taxi/logs/application-taxi-admin.log
chmod 666 /taxi/logs/application-taxi-admin.log

/taxi/tools/run.py \
    --https-hosts \
        ymsh-admin.mobile.yandex-team.ru \
        ymsh-admin-unstable.tst.mobile.yandex-team.ru \
        ymsh-admin.tst.mobile.yandex-team.ru \
        ymsh-admin.tst.taxi.yandex-team.ru \
        taxi-admin.yandex.nonexistent \
    --nginx yandex-taxi-admin \
    --restart-service 9999 \
    --wait \
        mongo.taxi.yandex:27017 \
        http://configs.taxi.yandex.net/ping \
    --run su www-data -s /bin/sh -c "
        /usr/lib/yandex/taxi-py2/bin/python /usr/lib/yandex/taxi-admin-yt-queries/manage.py runfcgi daemonize=true method=threaded socket=/var/run/yandex/taxi-admin-yt-queries/fcgi.sock
        /usr/lib/yandex/taxi-py2/bin/python /usr/lib/yandex/taxi-admin-slow-queries/manage.py runfcgi daemonize=true method=threaded socket=/var/run/yandex/taxi-admin-slow-queries/fcgi.sock
        /usr/lib/yandex/taxi-py2/bin/python /usr/lib/yandex/taxi-admin/manage.py runfcgi daemonize=false method=threaded socket=/var/run/yandex/taxi-admin/fcgi.sock
    "
