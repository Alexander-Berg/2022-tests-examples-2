#!/usr/bin/env bash

set -e

CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
python -m projects.eats.places_ranking.rec_sys.launcher \
    --config-path ${CURR_DIR}/data_configs/$1.json \
    --steps create_data_splits_from_scratch
