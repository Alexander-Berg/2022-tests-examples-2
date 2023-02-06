#!/bin/bash

set -e

if [[ -n "$1" ]]; then
    SERVICE_NAME=$1
else
    echo "Pass service name to script"
    exit 1
fi

/taxi/dockertest/healthcheck-env.sh

if [[ -n "$ENABLE_COVERAGE" ]]; then
    /taxi/dockertest/run-as-user.sh make "teamcity-coverage-$SERVICE_NAME"
else
    /taxi/dockertest/run-as-user.sh make "teamcity-test-$SERVICE_NAME"
fi
