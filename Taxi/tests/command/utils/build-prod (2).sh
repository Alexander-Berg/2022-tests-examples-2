#!/bin/sh
set -e

ROOT_DIR=$(node -e 'console.log(require("app-root-path").path)')
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

export DOCKER_HOST_INTERNAL=$($ROOT_DIR/tools/command/e2e/utils/get-docker-intenral-host.sh)

if  [ $(uname -n | grep yp-c.yandex.net) ]; then
    export CONFIG_ENV_CUSTOM=e2e.qyp
else
    export CONFIG_ENV_CUSTOM=e2e
fi

echo "Build project..."
npm run build:grocery:superapp
chmod -R +rwx ./tools/build
