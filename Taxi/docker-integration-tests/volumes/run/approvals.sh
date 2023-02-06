#!/usr/bin/env bash

set -e

APP_COMMAND=taxi_approvals.generated.web.run_web

REPO_DIR=/taxi/backend-py3
TAXI_APPROVALS_DIR=${REPO_DIR}/services/taxi-approvals
TAXI_APPROVALS_GENERATED_DIR=${TAXI_APPROVALS_DIR}/taxi_approvals/generated/
SETTINGS_PROD=${TAXI_APPROVALS_GENERATED_DIR}/service/settings/settings.production

if  [ -d "${TAXI_APPROVALS_GENERATED_DIR}" ]; then
    # Сервис кодгенный
    echo "taxi-approvals update generated package"
    mkdir -p /var/cache/yandex/taxi/configs/
    mkdir -p /etc/yandex/taxi-approvals/
    chown -R www-data:www-data /var/cache/yandex/taxi/configs
    mkdir -p /usr/lib/yandex/taxi-approvals/ \
           /etc/yandex/taxi-approvals/
    rm -rf /usr/lib/yandex/taxi-approvals/* \
           /etc/yandex/taxi-approvals/*
    mkdir -p /var/cache/yandex/taxi/taxi-approvals/files/

    ln -s ${REPO_DIR}/taxi /usr/lib/yandex/taxi-approvals/taxi
    if [ -d ${REPO_DIR}/generated ]; then
      ln -s ${REPO_DIR}/generated /usr/lib/yandex/taxi-approvals/generated
    fi
    for LIB_DIR in ${REPO_DIR}/libraries/*; do
        DIR_NAME=$(basename ${LIB_DIR})
        PACKAGE_NAME=${DIR_NAME//-/_}
        PACKAGE_DIR=${LIB_DIR}/${PACKAGE_NAME}
        if [ -d ${PACKAGE_DIR} ]; then
            ln -s ${PACKAGE_DIR} /usr/lib/yandex/taxi-approvals/${PACKAGE_NAME}
        fi
    done
    ln -s ${TAXI_APPROVALS_DIR}/taxi_approvals \
          /usr/lib/yandex/taxi-approvals/taxi_approvals
    ln -sf ${TAXI_APPROVALS_DIR}/debian/yandex-taxi-approvals.nginx \
           /etc/nginx/sites-available/yandex-taxi-approvals
    ln -sf ${TAXI_APPROVALS_DIR}/debian/yandex-taxi-approvals.upstream_list.production \
           /etc/nginx/conf.d/99-yandex-taxi-approvals-upstream
    if [ -f ${SETTINGS_PROD} ]; then
        ln -s ${SETTINGS_PROD} /etc/yandex/taxi-approvals/settings.yaml
    fi

fi

echo "Start command ${APP_COMMAND}"

chown -R www-data:www-data /var/log/supervisor/
chown -R www-data:www-data /etc/supervisor/
chown -R www-data:www-data /var/run/

/taxi/tools/run.py \
    --syslog \
    --wait \
      mongo.taxi.yandex:27017 \
      postgresql:dbapprovals \
      http://configs.taxi.yandex.net/ping \
    --nginx yandex-taxi-approvals \
    --run su www-data -s /bin/bash -c "/usr/lib/yandex/taxi-py3-2/bin/python3.7 \
          -m ${APP_COMMAND} --path=/tmp/yandex_taxi_approvals_00.sock \
          --instance=00"
