#!/usr/bin/env bash

/taxi/tools/run.py \
    --wait \
        http://atlas.taxi.yandex-team.net/ping \
        http://taxi-atlas-api.taxi.yandex.net/ping \
    --run echo 'Atlas services started'
