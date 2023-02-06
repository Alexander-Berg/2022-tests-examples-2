#!/bin/sh

set -e

ya make
./conductor run CreateConductorTicket --input "`cat test_data_create.json`" --local
echo
echo "Please log in as robot-passport-ci@ (password: https://yav.yandex-team.ru/secret/sec-01f67hyytg2g8a363srnb143ax/explore/versions) and revoke this conductor ticket"
