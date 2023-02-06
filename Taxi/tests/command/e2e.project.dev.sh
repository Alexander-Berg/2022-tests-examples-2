#!/bin/sh
set -e

SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

export APP_CLIENT_PORT=3200

$SCRIPT_DIR/utils/start-dev.sh
