#!/bin/sh
set -e

export APP_CLIENT_PORT=3200
export SELENOID_PORT=4444
export PROJECT_NAME=website

ROOT_DIR=$(node -e 'console.log(require("app-root-path").path)')
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

$ROOT_DIR/tools/command/e2e/utils/prerun.sh
$SCRIPT_DIR/utils/build-and-run-prod.sh
$ROOT_DIR/tools/command/e2e/utils/run-tests-with-report.sh "$@"
