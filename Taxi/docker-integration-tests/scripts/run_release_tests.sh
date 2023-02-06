#!/usr/bin/env bash
set -e

DOCKER_COMPOSE_FILE='docker-compose.yml'

if [[ "$3" == *"eats"* ]]; then
    DOCKER_COMPOSE_FILE='eats/docker-compose.yml'
fi

if [[ ${BUILD_BRANCH} == "taxi"* ]]; then
    export project=${BUILD_BRANCH}
elif [[ ${BUILD_BRANCH} == "eats"* ]]; then
    export project=${BUILD_BRANCH}
else
    export project=taxi-${BUILD_BRANCH}
fi

if ./scripts/get_services.py $DOCKER_COMPOSE_FILE --service $project; then
    url=$(./scripts/get_services.py $DOCKER_COMPOSE_FILE --service $project)
    if [[ $url == registry.yandex.net/taxi/taxi-integration/* ]]; then
        env IMAGE_VERSION=${BUILD_NUMBER} docker-compose build --no-cache ${project}
        env IMAGE_VERSION=latest docker-compose build ${project}
    fi

    if [ -z "$1" ]; then
        make run-tests
    else
        "$@"
    fi
fi
