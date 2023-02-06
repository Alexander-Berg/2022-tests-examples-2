#!/usr/bin/env bash

/taxi/tools/run.py \
    --nginx grocery-proxy-lite.conf \
    --run sleep infinity
