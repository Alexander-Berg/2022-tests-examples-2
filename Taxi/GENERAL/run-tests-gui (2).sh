#!/bin/sh
set -e

ROOT_DIR=$(node -e 'console.log(require("app-root-path").path)')
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

export TESTS_REPORT_PORT=8000

cd  "$ROOT_DIR"/projects/"$PROJECT_NAME"/tests/dist
echo "Open report..."
(npx kill-port $TESTS_REPORT_PORT && hermione gui --set "$PROJECT_NAME" --port $TESTS_REPORT_PORT) &
cd "$SCRIPT_DIR"

if  [ $(uname -n | grep yp-c.yandex.net) ]; then
    echo "Opening tunnel to watch gui $TESTS_PROXY_REPORT_PORT"
    $ROOT_DIR/tools/command/ts-run.sh $SCRIPT_DIR/gui-tunnel.ts &
    echo "Use tunnel url to watch hermione report"
else
  echo "Opening tests report on port $TESTS_REPORT_PORT"
fi
