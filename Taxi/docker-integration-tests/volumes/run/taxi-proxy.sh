#!/usr/bin/env bash

/taxi/tools/run.py \
    --nginx taxi-proxy.conf \
    --run sleep infinity
