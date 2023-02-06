#!/usr/bin/env bash

cp /taxi/redis/sentinel.conf /etc/redis/sentinel.conf
chmod 666 /etc/redis/sentinel.conf
/taxi/tools/run.py \
    --stdout-to-log \
    --run \
        redis-server /etc/redis/sentinel.conf --sentinel
