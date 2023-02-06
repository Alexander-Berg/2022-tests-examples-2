#!/usr/bin/env bash

/taxi/tools/run.py \
    --nginx grocery-proxy.conf \
    --run sleep infinity
