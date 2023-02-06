#!/bin/sh
set -e

ROOT_DIR=$(node -e 'console.log(require("app-root-path").path)')
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

export DOCKER_HOST_INTERNAL=$($ROOT_DIR/tools/command/e2e/utils/get-docker-intenral-host.sh)
export CONFIG_ENV_CUSTOM=e2e
export NODE_ENV=production

echo "Build project..."
npm run build
