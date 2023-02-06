#!/usr/bin/env bash

set -e

TANKER_API_TOKEN=$(cat .dev/tanker.token)

docker build . -t taxi/lavka-falcon:dev -f services/lavka-falcon/Dockerfile.lavka-falcon \
  --build-arg TANKER_API_TOKEN=${TANKER_API_TOKEN} --no-cache

exec docker run -it --net=host taxi/lavka-falcon:dev bash -c \
  'cd /usr/local/app && node out/server/index.js'
