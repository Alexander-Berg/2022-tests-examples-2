#!/usr/bin/env bash

docker build -t config-nginx-davos-landing-proxy-tests:latest ./tests/docker/

NGINX_CONFIGS="$(pwd)/src/nginx"
TESTS="$(pwd)/tests"

docker run --rm -it \
    -v $NGINX_CONFIGS:/etc/nginx/sites-enabled:ro \
    -v $TESTS:/tests:ro \
    -v $TESTS/.cache:/tests/.cache:rw \
    config-nginx-davos-landing-proxy-tests:latest
