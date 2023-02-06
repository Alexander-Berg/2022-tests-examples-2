#!/bin/sh
set -e

SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
PROJECT_DIR=$(node -e 'console.log(require("app-root-path").path)')/projects/webview

cd_project_dir() {
  cd $PROJECT_DIR
}

restore_script_dir() {
  cd $SCRIPT_DIR
}

kill_potentially_running_ports() {
  npx kill-port $APP_CLIENT_PORT $SUPERAPP_CLIENT_PORT
}

build_and_run_project() {
  npm run e2e:project:prod:build && npm run e2e:project:prod:start
}

wait_for_project_port() {
  echo "Waiting for port:$APP_CLIENT_PORT"
  npx wait-on tcp:$APP_CLIENT_PORT --timeout $((5*60*1000))
}

cd_project_dir
kill_potentially_running_ports
build_and_run_project &
wait_for_project_port
restore_script_dir