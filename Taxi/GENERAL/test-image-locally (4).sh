#!/usr/bin/env bash

set -e

TANKER_API_TOKEN=$(cat services/pigeon/.dev/tanker.token)
DOCKER_BUILDKIT=0; docker build . -t taxi/pigeon:dev -f services/pigeon/Dockerfile.pigeon \
  --build-arg TANKER_API_TOKEN=${TANKER_API_TOKEN} --no-cache

exec docker run -it --net=host taxi/pigeon:dev bash -c \
  'cd /usr/local/app && node services/pigeon/out/server/index.js'
