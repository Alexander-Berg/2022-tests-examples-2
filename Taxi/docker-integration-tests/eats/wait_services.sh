#!/usr/bin/env bash

/taxi/tools/run.py \
    --wait \
        http://cardstorage.taxi.yandex.net/ping \
        http://mock-server.yandex.net/ping/ \
        http://eats-cart.eda.yandex.net/ping \
        http://eats-picker-dispatch.eda.yandex.net/ping \
        http://eats-picker-orders.eda.yandex.net/ping \
        http://eats-picker-supply.eda.yandex.net/ping \
        http://eats-picking-time-estimator.eda.yandex.net/ping \
        http://eats-picker-payments.eda.yandex.net/ping \
        http://eats-launch.eda.yandex.net/ping \
        http://eats-offers.eda.yandex.net/ping \
        http://eats-payments.eda.yandex.net/ping \
        https://eda.yandex/ping \
        http://eats-orders-tracking.eda.yandex.net/ping \
        http://eats-catalog.eda.yandex.net/ping \
        http://eats-catalog-storage.eda.yandex.net/ping \
        http://eats-picker-item-categories.eda.yandex.net/ping \
        http://uconfigs.taxi.yandex.net/ping \
     --run echo 'Services started'
