#!/usr/bin/env bash
set -e

CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

python -m projects.eats.places_ranking.rec_sys.launcher \
    --config-path ${CURR_DIR}/apply_configs/apply_prod_model_config.json \
    --config-template-path ${CURR_DIR}/learn_template.json \
    --steps rank_common_rest_list
