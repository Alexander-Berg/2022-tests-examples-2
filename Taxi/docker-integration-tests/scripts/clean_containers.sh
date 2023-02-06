#!/bin/sh

DOCKER_CONTAINER_PREFIX=$(basename $PWD)

rm_all_containers() {
    # Discovers, stops and removes all the docker containers
    # specified with the string in $1
    containers=`docker ps -a | grep -F $1 | awk '{print $1}'`
    echo "Clearing containers $1:"
    echo "$containers"
    if [ -n "$containers" ]; then
        docker container stop $containers
        docker container rm -v $containers
    fi
}


echo "Clearing containers"

for service in $(docker-compose config --services); do
    rm_all_containers ${DOCKER_CONTAINER_PREFIX}_${service}
done
