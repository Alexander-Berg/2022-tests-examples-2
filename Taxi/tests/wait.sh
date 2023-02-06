#!/usr/bin/env bash

URL="http://${1}.taxi.dev.yandex.docker/ping"
: ${RETRY_ATTEMPT:=10}
: ${CONNECT_TIMEOUT:=1}
: ${RETRY_TIMEOUT:=20}
ARGS="-I ${URL} --connect-timeout ${CONNECT_TIMEOUT}"

function ping_service
{
    OUTPUT=$(curl $ARGS 2> /dev/null)
    STATUS="$?"
    if [ ! "${STATUS}" -eq "0" ]; then
        return 1
    fi
    OUTPUT=$(echo -e "${OUTPUT}" | head -n 1 | cut -d$' ' -f2)
    [ "${OUTPUT}" == "200" ] || return 1
}

until ping_service
do
    if [[ $RETRY_ATTEMPT -eq 0 ]]; then
        exit 1
    fi
    RETRY_ATTEMPT=$(($RETRY_ATTEMPT-1))
    sleep $RETRY_TIMEOUT
done

