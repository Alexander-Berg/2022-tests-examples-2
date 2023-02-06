ARG BASE_IMAGE
FROM ${BASE_IMAGE}

LABEL maintainer="v-pereskokov@yandex-team.ru"

WORKDIR /var/www/html

RUN cd /var/www/html/ && \
    npm run lint && \
    npm run test
