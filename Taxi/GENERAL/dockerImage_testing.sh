#!/bin/bash

# $1 is tag of this build
# $2 is docker image path
# $3 is build env
# $4 is service name
# $5 is needless to push: y | n
# $6 is return val of container_name
function buildDockerImage() {
    TAG=$1
    IMAGE_PATH=$2
    BUILD_ENV=$3
    SERVICE_NAME=$4
    IS_PUSH=${5:-y}
    ONLY_PARTIAL=$6

    APP_DOCKER_VERSION="${IMAGE_PATH}/${BUILD_ENV}"
    BASE_IMAGE_ENV="${BUILD_ENV}"
    CONTAINER_NAME="${APP_DOCKER_VERSION}:${TAG}"

    # Билдим сборку сервиса
    docker build \
        --pull \
        --build-arg BASE_IMAGE_TAG="build_${BUILD_ENV}" \
        --build-arg BUILD="$BUILD_ENV" \
        --build-arg VERSION="$TAG" \
        --build-arg BASE_IMAGE_ENV="$BASE_IMAGE_ENV" \
        --build-arg APP_SERVICE_NAME="$SERVICE_NAME" \
        -f "services/${SERVICE_NAME}/docker/Dockerfile" \
        -t "${CONTAINER_NAME}" \
        .

    TST_APP_DOCKER_VERSION="${IMAGE_PATH}/testing"
    pushImage "${CONTAINER_NAME}" "${TST_APP_DOCKER_VERSION}" "${TAG}"

    eval "$6='${CONTAINER_NAME}'"
}

# $1 is container name
# $2 is docker path
# $3 is tag
function pushImage() {
    CONTAINER=$1
    IMAGE=$2
    TAG=$3
    REGISTRY="registry.yandex.net"

    echo "${CONTAINER} // ${IMAGE} // ${REGISTRY}/${IMAGE}:${TAG}"

    docker tag "${CONTAINER}" "${REGISTRY}/${IMAGE}:${TAG}"
    docker push "${REGISTRY}/${IMAGE}:${TAG}"
}
