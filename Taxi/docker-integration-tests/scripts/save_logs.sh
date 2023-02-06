#!/usr/bin/env bash

mkdir -p _logs

docker-compose logs --no-color | tail -n +2 | while read line; do
    echo "${line#*| }" >> "_logs/container-${line%% *}.log"
done

if arc root > /dev/null; then
    cp -r _logs ../../..
fi
