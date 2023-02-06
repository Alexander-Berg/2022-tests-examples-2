#!/usr/bin/env bash
set -e

REPO_DIR=/taxi/backend-py3
API_ADMIN_DIR=$REPO_DIR/services/taxi-api-admin
API_ADMIN_GENERATED_DIR=${API_ADMIN_DIR}/taxi_api_admin/generated/
SETTINGS_PROD=$API_ADMIN_GENERATED_DIR/service/settings/settings.production

if  [ -d "$API_ADMIN_GENERATED_DIR" ]; then
    echo "api-admin update generated package"
    mkdir -p /var/cache/yandex/taxi/configs/
    mkdir -p /etc/yandex/taxi-api-admin/
    chown -R www-data:www-data /var/cache/yandex/taxi/configs
    mkdir -p /usr/lib/yandex/taxi-api-admin/ \
           /etc/yandex/taxi-api-admin/
    rm -rf /usr/lib/yandex/taxi-api-admin/* \
           /etc/yandex/taxi-api-admin/*
    mkdir -p /var/cache/yandex/taxi/taxi-api-admin/files/

    ln -s $REPO_DIR/taxi /usr/lib/yandex/taxi-api-admin/taxi
    if [ -d $REPO_DIR/generated ]; then
      ln -s $REPO_DIR/generated /usr/lib/yandex/taxi-api-admin/generated
    fi
    for LIB_DIR in $REPO_DIR/libraries/*; do
        DIR_NAME=$(basename $LIB_DIR)
        PACKAGE_NAME=${DIR_NAME//-/_}
        PACKAGE_DIR=$LIB_DIR/$PACKAGE_NAME
        if [ -d $PACKAGE_DIR ]; then
            ln -s $PACKAGE_DIR /usr/lib/yandex/taxi-api-admin/$PACKAGE_NAME
        fi
    done
    ln -s $API_ADMIN_DIR/taxi_api_admin \
          /usr/lib/yandex/taxi-api-admin/taxi_api_admin
    ln -sf $API_ADMIN_DIR/debian/yandex-taxi-api-admin.nginx \
           /etc/nginx/sites-available/yandex-taxi-api-admin
    ln -sf $API_ADMIN_DIR/debian/yandex-taxi-api-admin.upstream_list.production \
           /etc/nginx/conf.d/99-yandex-taxi-api-admin-upstream
    if [ -f $SETTINGS_PROD ]; then
        ln -s $SETTINGS_PROD /etc/yandex/taxi-api-admin/settings.yaml
    fi

fi

chown -R www-data:www-data /var/log/supervisor/
chown -R www-data:www-data /etc/supervisor/
chown -R www-data:www-data /var/run/

for num in {01..16}; do
    ln -sf yandex_taxi_api_admin_00.sock /tmp/yandex_taxi_api_admin_${num}.sock
done

APP_COMMAND=taxi_api_admin.generated.web.run_web
echo "Start command ${APP_COMMAND}"

/taxi/tools/run.py \
    --syslog \
    --wait \
        mongo.taxi.yandex:27017 \
        http://configs.taxi.yandex.net/ping \
    --nginx yandex-taxi-api-admin \
    --run su www-data -s /bin/bash -c "/usr/lib/yandex/taxi-py3-2/bin/python3.7 \
          -m ${APP_COMMAND} --path=/tmp/yandex_taxi_api_admin_00.sock \
          --instance=00"
