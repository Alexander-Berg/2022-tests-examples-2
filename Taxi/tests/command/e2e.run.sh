#!/bin/sh
set -e

export PROJECT_NAME=website
export APP_CLIENT_PORT=3200

ROOT_DIR=$(node -e 'console.log(require("app-root-path").path)')

$ROOT_DIR/tools/command/e2e/run/e2e.run.sh "$@"