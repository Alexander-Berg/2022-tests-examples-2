#!/bin/sh

# see https://lebkowski.name/docker-volumes/

if [[ "$OSTYPE" == "darwin"* ]]; then
    # Xargs differs on Mac OSX
    docker volume ls -qf dangling=true | xargs docker volume rm
else
    docker volume ls -qf dangling=true | xargs -r docker volume rm
fi
