#!/bin/bash

set -e
cd /taxi/repo

run_command(){
    echo -e "=====================\tRunning command: '$@'\t====================="
    "$@"
}

case "$APP_ENV" in
    "production") S3_URL="https://yastatic.net/s3/fleet" ;;
    "testing") S3_URL="https://fleet-web.s3.mdst.yandex.net" ;;
    *) echo "[build_static] [ERROR]: APP_ENV is not defiend"; exit 1 ;;
esac

if [[ -z "$APP_VERSION" ]]; then
    echo "[build_static] [ERROR]: APP_VERSION is not defiend"
    exit 1
fi

export REACT_APP_ENV=$APP_ENV
export REACT_APP_VERSION=$APP_VERSION

run_command yarn app:build --mode testing --base $S3_URL/fleet/

rm -rf dist
cp -r packages/app/dist/ dist
