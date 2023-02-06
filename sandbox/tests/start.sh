#!/bin/bash

npm run start --prefix /yharnam/server/apps/mockService &
sleep 30
BASE_COMMAND="npm run test:autotests:docker -- --mockUrl http://localhost:3000/api --stand https://docker.partner.yandex.ru --chunk=${CHUNK}"
if [ "${OPTION}" == "pattern" ];
then
    BASE_COMMAND="${BASE_COMMAND} --test ${PATTERN}"
    echo $BASE_COMMAND
    $BASE_COMMAND
    exit
fi
if [ -n "${OPTION}" ];
then
    BASE_COMMAND="${BASE_COMMAND} --set ${OPTION}"
    echo $BASE_COMMAND
    $BASE_COMMAND
    exit
fi
echo $BASE_COMMAND
$BASE_COMMAND
