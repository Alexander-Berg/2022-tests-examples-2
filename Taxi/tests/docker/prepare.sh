#!/usr/bin/env bash

mkdir -p /etc/ssl/yandex
openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/yandex/server.pem -out /etc/ssl/yandex/server.pem -days 365 -nodes -subj '/CN=localhost'
for cert in redtaxi.ru.pem taxisaturn.ru.pem vezetdobro.ru.pem rutaxi.ru.pem rutaxi_mobile_subdomains.pem taxi_leader.pem dooh_go_yandex.pem business_go_yandex.pem happybirthday_taxi_yandex-team_ru.pem; do
    cp /etc/ssl/yandex/server.pem /etc/ssl/yandex/$cert
done
