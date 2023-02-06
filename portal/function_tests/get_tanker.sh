#!/usr/bin/env bash
CWD=$(pwd)
TANKER_DIR="$CWD/tanker"
LOCK_FILE="tanker.lock"

if [ ! -d ${TANKER_DIR} ]; then
    mkdir ${TANKER_DIR}
fi

cd $TANKER_DIR

if [ ! -f ${LOCK_FILE} ] || ["$(find ${LOCK_FILE} -mmin +120)" ];
then
    echo "Updating tanker"

    for project in "tune" "home" "maps_api" "zen" "lego-islands-user";
        do echo "Downloading tanker project ${project}";
        curl "https://tanker-api.yandex-team.ru/projects/export/xml/?project-id=${project}" -o "${project}.xml"
    done

    echo "Updated: $(date)" >> ${LOCK_FILE}
else
    echo "Tanker data is up to date, won't update"
fi

cd $CWD
