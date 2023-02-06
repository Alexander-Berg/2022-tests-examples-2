#!/bin/sh
set -e

ROOT_DIR=$(node -e 'console.log(require("app-root-path").path)')
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
export APP_CLIENT_PORT=3200

start_mock_server() {
  $ROOT_DIR/tools/command/e2e/run/mock.dev.sh
}

run_superapp_dev() {
  $SCRIPT_DIR/utils/start-dev.sh
}

start_mock_server &
run_superapp_dev
