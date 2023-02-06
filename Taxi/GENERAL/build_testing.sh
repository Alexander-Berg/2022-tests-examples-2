#!/bin/bash
set -e

IS_PUSH=${1:-y}

DOCKER_IMAGE=$(/opt/nodejs/10/bin/node tools/service/build.js)

echo "tickets: $TICKETS"
echo "tag: $DOCKER_TAG"
echo "release tag: $RELEASE_TAG"
echo "image: $DOCKER_IMAGE"

if [[ -n $RELEASE_TAG ]]; then
    RESULT_TAG=$RELEASE_TAG
else
    RESULT_TAG=$DOCKER_TAG
fi

PROJECT_IMAGE_NAME=''
source ./tools/service/dockerImage_testing.sh;
buildDockerImage "$RESULT_TAG" "$DOCKER_IMAGE" "$DEPLOY_BRANCH" "$BUILD_BRANCH" "$IS_PUSH" PROJECT_IMAGE_NAME

echo "##teamcity[setParameter name='env.IMAGE' value='${DOCKER_IMAGE}']"
echo "##teamcity[setParameter name='env.PROJECT_IMAGE_NAME' value='${PROJECT_IMAGE_NAME}']"
