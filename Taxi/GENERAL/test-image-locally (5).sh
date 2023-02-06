#!/usr/bin/env bash

set -e

TANKER_API_TOKEN=$(cat services/pigeon-market/.dev/tanker.token)
DOCKER_BUILDKIT=0; docker build . -t taxi/pigeon-market:dev -f services/pigeon-market/Dockerfile.pigeon-market \
  --build-arg TANKER_API_TOKEN=${TANKER_API_TOKEN} --no-cache

exec docker run -it --net=host taxi/pigeon-market:dev bash -c \
  'cd /usr/local/app && node services/pigeon-market/out/server/index.js'
