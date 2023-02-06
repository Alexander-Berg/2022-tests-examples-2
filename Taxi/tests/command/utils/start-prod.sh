ROOT_DIR=$(node -e 'console.log(require("app-root-path").path)')
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

export NODE_ENV=production
export CONFIG_ENV_CUSTOM=e2e
export DOCKER_HOST_INTERNAL=$($ROOT_DIR/tools/command/e2e/utils/get-docker-intenral-host.sh)
export PORT=$APP_CLIENT_PORT
export CFG_DIR='dist/configs'

npx kill-port $APP_CLIENT_PORT
node dist/server/index.js