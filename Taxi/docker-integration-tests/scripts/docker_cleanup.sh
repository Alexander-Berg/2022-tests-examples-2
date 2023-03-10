#!/bin/bash
# from https://gist.github.com/wdullaer/76b450a0c986e576e98b. edited
# Cleanup docker files: untagged containers and images.
#
# Use `docker-cleanup -n` for a dry run to see what would be deleted.

DOCKER_COMPOSE='docker-compose.yml docker-compose.eats.yml'

untagged_containers() {
    # Print containers using untagged images: $1 is used with awk's print: 0=line, 1=column 1.
    # NOTE: "[0-9a-f]{12}" does not work with GNU Awk 3.1.7 (RHEL6).
    # Ref: https://github.com/blueyed/dotfiles/commit/a14f0b4b#commitcomment-6736470
    docker ps -a | tail -n +2 | awk '$2 ~ "^[0-9a-f]+$" {print $'$1'}'
}

untagged_images() {
    # Print untagged images: $1 is used with awk's print: 0=line, 3=column 3.
    # NOTE: intermediate images (via -a) seem to only cause
    # "Error: Conflict, foobarid wasn't deleted" messages.
    # Might be useful sometimes when Docker messed things up?!
    # docker images -a | awk '$1 == "<none>" {print $'$1'}'
    docker images | tail -n +2 | awk '$1 == "<none>" {print $'$1'}'
}

# Dry-run.
if [ "$1" = "-n" ]; then
    echo "=== Containers with uncommitted images: ==="
    untagged_containers 0
    echo
    echo "=== Uncommitted images: ==="
    untagged_images 0
    echo
    echo "=== Dangling volumes: ==="
    docker volume ls --filter dangling=true -q
    exit
fi
if [ -n "$1" ]; then
    echo "Cleanup docker files: remove untagged containers and images."
    echo "Usage: ${0##*/} [-n]"
    echo " -n: dry run: display what would get removed."
    exit 1
fi

# Remove containers with untagged images.
echo "Removing containers:" >&2
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Xargs differs on Mac OSX
    untagged_containers 1 | xargs docker rm --volumes=true
else
    untagged_containers 1 | xargs --no-run-if-empty docker rm --volumes=true
fi

# Remove untagged images
echo "Removing untagged images:" >&2
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Xargs differs on Mac OSX
    untagged_images 3 | xargs docker rmi
else
    untagged_images 3 | xargs --no-run-if-empty docker rmi
fi

echo "Removing old images:" >&2
# Images in this list would not be removed
PROTECTED_IMAGES='registry.yandex.net/taxi/taxi-integration-plotva-ml:latest
registry.yandex.net/taxi/baseimages/taxi-base-qloud-xenial:latest
registry.yandex.net/taxi/rtc-baseimage/testing:latest
registry.yandex.net/taxi/rtc-baseimage/production:latest'
docker images | awk '$1 ~ /registry.yandex.net/ && $2 !~ /<none>/ {print $1 ":" $2}' | \
    grep -vxF "$(IMAGE_VERSION=latest ./scripts/get_services.py --images $DOCKER_COMPOSE)" | \
    grep -vxF "$PROTECTED_IMAGES" | xargs -r docker rmi

# Remove dangling volumes
echo "Removing dangling volumes:" >&2
docker volume prune -f

echo "Removing dangling images:" >&2
docker image prune -f
