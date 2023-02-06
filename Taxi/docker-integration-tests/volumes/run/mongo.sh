#!/usr/bin/env bash
set -e

/taxi/tools/run.py \
    --run /taxi/tools/run_as_user.sh /taxi/run/mongo-init.sh
