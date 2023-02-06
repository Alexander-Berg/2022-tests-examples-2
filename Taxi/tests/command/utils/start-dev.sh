#!/bin/sh
set -e

ROOT_DIR=$(node -e 'console.log(require("app-root-path").path)')
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

export CONFIG_ENV_CUSTOM=e2e
export DOCKER_HOST_INTERNAL=$($ROOT_DIR/tools/command/e2e/utils/get-docker-intenral-host.sh)
export NODE_ENV=development

npx kill-port $APP_CLIENT_PORT

npm run dev:prepare
npm run dev:start:webpack &
npm run dev:start:server
