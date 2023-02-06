#!/usr/bin/env bash
set -e
appname=taxi-atlas-frontend

ln -sf /taxi/logs/application-$appname-nginx-error.log /var/log/nginx/error.log
ln -sf /taxi/logs/application-$appname-nginx-access.log /var/log/nginx/access.log

/usr/sbin/nginx -g 'daemon off;'
