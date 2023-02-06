#!/usr/bin/env bash

envsubst '${REDIS_MASTER_IPV6}' < /taxi/redis/sentinel.conf > /etc/redis/sentinel.conf
chmod 666 /etc/redis/sentinel.conf
redis-server /etc/redis/sentinel.conf --sentinel
