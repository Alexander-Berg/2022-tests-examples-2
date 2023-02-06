#!/bin/bash

set -e
cd /taxi/repo

run_command(){
    echo -e "=====================\tRunning command: '$@'\t====================="
    "$@"
}

if [[ (-z "$AWS_ACCESS_KEY_ID") || (-z "$AWS_SECRET_ACCESS_KEY") ]]; then
    echo "[deploy_static_testing] [ERROR]: No secret specified"
    exit 1
fi

if [[ (-z "$APP_ENV") ]]; then
    echo "[deploy_static_testing] [ERROR]: APP_ENV is not defiend"
    exit 1
fi

if [[ "$APP_ENV"="testing" ]]; then
    run_command yarn node -r esbuild-register tools/deploy_static_testing.ts
fi