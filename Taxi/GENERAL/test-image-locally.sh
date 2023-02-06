#!/usr/bin/env bash

set -e

TANKER_API_TOKEN=$(cat services/eagle/.dev/tanker.token)

docker build . -t taxi/lavka-eagle:dev -f services/eagle/Dockerfile.eagle \
  --build-arg TANKER_API_TOKEN=${TANKER_API_TOKEN} --no-cache

exec docker run -it --net=host taxi/lavka-eagle:dev bash -c \
  'cd /usr/local/app && node services/eagle/out/server/index.js'
