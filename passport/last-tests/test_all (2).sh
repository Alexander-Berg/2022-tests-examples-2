#!/bin/bash
cd "$( dirname "${BASH_SOURCE[0]}" )"
ylast -j 6 -c last.conf -U https://api.my-passport.yandex.ru *.xml -N 2>/dev/null

## /etc/hosts/
# [self ip]        cerevra-dev-xenial.passport.yandex.net cerevra-dev-xenial mda-dev.yandex.ru mda-dev.yandex.ua mda-dev.yandex.com api.my-passport.yandex.ru
