#!/bin/sh

# Изолированный проект
DOCKER_PROJECT="${DOCKER_PROJECT:-lavka_`date +%s_%N`}"

# Очистка окружения
cleanup() {
    CODE="${1:-1}"
    docker-compose \
        --project-name ${DOCKER_PROJECT} \
        --file dockers/compose/docker-compose.db.yml \
        --file dockers/compose/docker-compose.ci.yml \
        down \
        --remove-orphans
    exit $CODE
}
trap cleanup HUP INT TERM QUIT ABRT ALRM

timeout --foreground --kill-after=65m 60m \
    docker-compose \
        --project-name ${DOCKER_PROJECT} \
        --file dockers/compose/docker-compose.db.yml \
        --file dockers/compose/docker-compose.ci.yml \
        up \
        --force-recreate \
        --abort-on-container-exit \
        --remove-orphans \
        test

cleanup $?
