#!/usr/bin/env bash
set -e

CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

python -m projects.eats.places_ranking.rec_sys.launcher \
    --config-path ${CURR_DIR}/learn_configs/learn_linear_weights.json \
    --config-template-path ${CURR_DIR}/learn_template.json \
    --steps \
    create_dataset_splits \
    learn_linear_weights
