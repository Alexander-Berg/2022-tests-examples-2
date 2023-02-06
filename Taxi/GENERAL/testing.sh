#!/bin/bash
set -e

WITH_PUSH=${1}

docker build \
    --no-cache \
    --build-arg BASE_IMAGE="service_dependencies_image" \
    -f "tools/docker/tests.dockerfile" \
    -t service_testing_image \
    .

TAG_TEST="build_${DEPLOY_BRANCH}"
TAG_COMMIT="registry.yandex.net/taxi/${BUILD_BRANCH}:${TAG_TEST}"
docker tag "service_testing_image" ${TAG_COMMIT}

echo "WITH PUSH: ${WITH_PUSH}"

# В сборке Checker указан параметр первый -- true | false
if [[ "$WITH_PUSH" == "true" ]]; then
    docker push ${TAG_COMMIT}
fi
