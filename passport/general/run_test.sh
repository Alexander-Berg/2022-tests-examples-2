#!/bin/sh

set -e

ya make
echo
echo "Running tests can be seen here: https://aqua.yandex-team.ru/#/launches?skip=0&limit=20&packId=615db37b8a90fe6cf0152206"
echo "You may cancel the latest launch to check how tests will be retried."
echo
./aqua run RunAquaTests --input "`cat test_data.json`" --local
