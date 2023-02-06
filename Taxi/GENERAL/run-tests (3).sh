#!/bin/bash

set -e

if [[ -n "$1" ]]; then
    SERVICE_NAME=$1
else
    echo "Pass service name to script"
    exit 1
fi

mkdir -p "$CORES_DIR"
chmod 777 "$CORES_DIR"
echo "$CORES_DIR/core-%e-%s-%u-%g-%p-%t" > /proc/sys/kernel/core_pattern

/taxi/dockertest/healthcheck-env.sh

/taxi/dockertest/run-as-user.sh make "teamcity-test-$SERVICE_NAME"
