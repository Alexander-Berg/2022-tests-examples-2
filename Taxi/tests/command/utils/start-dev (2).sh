#!/bin/sh
set -e

ROOT_DIR=$(node -e 'console.log(require("app-root-path").path)')
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

export DOCKER_HOST_INTERNAL=$($ROOT_DIR/tools/command/e2e/utils/get-docker-intenral-host.sh)

if  [ $(uname -n | grep yp-c.yandex.net) ]; then
    export CONFIG_ENV_CUSTOM=e2e.qyp
    echo 'match'
else
    export CONFIG_ENV_CUSTOM=e2e
fi

export SUPERAPP_CLIENT_PORT=3302

npx kill-port $APP_CLIENT_PORT $SUPERAPP_CLIENT_PORT
npm run dev:superapp
