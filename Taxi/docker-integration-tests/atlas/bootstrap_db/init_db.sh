#!/usr/bin/env bash

set -e

/taxi/tools/run.py \
    --wait mongo.atlas.taxi.yandex:27017 \
    --run /taxi/atlas/bootstrap_db/bootstrap_atlas_db.py --force
