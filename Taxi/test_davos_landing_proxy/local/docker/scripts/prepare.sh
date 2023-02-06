#!/usr/bin/env bash

mkdir -p /etc/ssl/yandex
openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/yandex/server.pem -out /etc/ssl/yandex/server.pem -days 365 -nodes -subj '/CN=*'
for cert in webauth_yandex_team_ru.pem happybirthday_taxi_yandex-team_ru.pem; do
    cp /etc/ssl/yandex/server.pem /etc/ssl/yandex/$cert
done
