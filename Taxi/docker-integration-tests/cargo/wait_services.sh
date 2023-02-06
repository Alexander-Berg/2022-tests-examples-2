#!/usr/bin/env bash

/taxi/tools/run.py \
    --wait \
        http://mock-server.yandex.net/ping/ \
        http://uconfigs.taxi.yandex.net/ping \
        http://cargo-orders.taxi.yandex.net/ping \
        http://cargo-dispatch.taxi.yandex.net/ping \
        http://cargo-claims.taxi.yandex.net/ping \
        http://united-dispatch.taxi.yandex.net/ping \
     --run echo 'Services started'
