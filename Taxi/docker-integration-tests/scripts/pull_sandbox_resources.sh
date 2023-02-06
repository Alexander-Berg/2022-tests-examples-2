#!/usr/bin/env bash
set -e

DOCKER_TESTS_ROOT=`realpath $(dirname "${BASH_SOURCE[0]:-$0}")/..`
ARCADIA_ROOT=`realpath $DOCKER_TESTS_ROOT/../..`
SANDBOX_HOME=$DOCKER_TESTS_ROOT/_sandbox

# TODO: refactor if sandbox technology will be generalized


## procaas-taxi

# Try to detect that taxi AGL-modules has been changed
# https://bb.yandex-team.ru/projects/TAXI/repos/teamcity-backend-settings/browse/projects/arcadia-projects/projects/procaas/projects/integration-tests-tier0/builds/integration-tests-tier0.yaml#77
PROCAAS_TAXI_BRANCH="${PROCAAS_TAXI_BRANCH:-stable}"
if [ "$CHANGED_PROJECTS" = "processing" ]; then
    PROCAAS_TAXI_BRANCH="trunk"
fi

# Get procaas taxi AGL modules
mkdir -p $SANDBOX_HOME/procaas/taxi
make fetch-taxi-modules -C $ARCADIA_ROOT/procaas TAXI_MODULES_OUTPUT_PATH=$SANDBOX_HOME/procaas/taxi TAXI_DOCKER_TESTS_BRANCH=$PROCAAS_TAXI_BRANCH
