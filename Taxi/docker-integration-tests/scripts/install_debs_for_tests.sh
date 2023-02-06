#!/usr/bin/env bash
set -e
# TODO(rumkex): remove this script in TAXITOOLS-3153

DEFAULT_BASE_IMAGE=registry.yandex.net/taxi/taxi-integration-xenial-base:latest
BASE_IMAGE=${2:-$DEFAULT_BASE_IMAGE}

if [[ -z "${1}" ]]; then
    echo "Pass image name with tag for new image"
    exit 1
fi

NEW_IMAGE=${1}
CONTAINER_ID=$(docker run -d --volume ${PWD}/volumes/ext-debs:/taxi/ext-debs ${BASE_IMAGE} sleep infinity)

docker exec ${CONTAINER_ID} apt update
docker exec ${CONTAINER_ID} bash -c "find /taxi/ext-debs -name '*.deb' | xargs -r apt install -y" || docker rm -f ${CONTAINER_ID}
docker commit ${CONTAINER_ID} ${NEW_IMAGE}
docker rm -f ${CONTAINER_ID}
