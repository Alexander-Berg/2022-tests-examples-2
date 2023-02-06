#!/usr/bin/env bash

cp /taxi/redis/redis.conf /etc/redis/redis.conf
chmod 666 /etc/redis/redis.conf
/taxi/tools/run.py \
    --stdout-to-log \
    --run redis-server /etc/redis/redis.conf
