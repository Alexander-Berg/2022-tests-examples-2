#!/usr/bin/env bash
set -e

if [[ ${BUILD_BRANCH} == "taxi"* ]]; then
    export project=${BUILD_BRANCH}
else
    export project=taxi-${BUILD_BRANCH}
fi

if ./scripts/get_services.py --service ${project}; then
    url=$(./scripts/get_services.py --service ${project})
    if [[ ${url} == registry.yandex.net/taxi/taxi-integration/* ]]; then
        if [[ -n "${TOOL_DEBUG}" ]]; then
            echo "DEBUG mode enabled. Push images is aborted"
            exit 0
        fi
        env IMAGE_VERSION=${BUILD_NUMBER} docker-compose push ${project}
        env IMAGE_VERSION=latest docker-compose push ${project}
    fi
fi
