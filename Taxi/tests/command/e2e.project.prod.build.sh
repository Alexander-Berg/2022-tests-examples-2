#!/bin/sh
set -e

SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

$SCRIPT_DIR/utils/build-prod.sh
