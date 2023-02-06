#!/usr/bin/env bash
set -e

REPO_DIR=/taxi/backend-py3
CONFIGS_ADMIN_DIR=$REPO_DIR/services/configs-admin
CONFIGS_ADMIN_GENERATED_DIR=${CONFIGS_ADMIN_DIR}/configs_admin/generated/
SETTINGS_PROD=$CONFIGS_ADMIN_GENERATED_DIR/service/settings/settings.production
BASE_SOURCE_PATH=/usr/lib/yandex/taxi-configs-admin-web

echo "Start install configs-admin"
if [ -d "$CONFIGS_ADMIN_GENERATED_DIR" ]; then
    echo "configs-admin update package -- create caches dirs"
    mkdir -p /var/cache/yandex/taxi/configs/
    mkdir -p /var/cache/yandex/taxi/configs-admin/files/
    mkdir -p /var/cache/yandex/taxi/clownductor/v1/
    chown -R www-data:www-data /var/cache/yandex/taxi/configs
    touch "/var/cache/yandex/taxi/clownductor/v1/configs_admin_web.json"

    echo "configs-admin update package -- create etc dirs"
    mkdir -p /etc/yandex/taxi-configs-admin-web/
    mkdir -p $BASE_SOURCE_PATH/ \
           /etc/yandex/taxi-configs-admin-web/
    rm -rf $BASE_SOURCE_PATH/* \
           /etc/yandex/taxi-configs-admin-web/*

    echo "configs-admin update package -- fill generated"
    ln -s $REPO_DIR/taxi $BASE_SOURCE_PATH/taxi
    if [ -d $REPO_DIR/generated ]; then
      ln -s $REPO_DIR/generated $BASE_SOURCE_PATH/generated
    fi

    echo "configs-admin update package -- fill fbs"
    if [ -d $REPO_DIR/generated/fbs ]; then
      echo "configs-admin update package -- real fill fbs"
      ln -s $REPO_DIR/generated/fbs/* $BASE_SOURCE_PATH
    fi

    echo "configs-admin update package -- fill libraries"
    for LIB_DIR in $REPO_DIR/libraries/*; do
        DIR_NAME=$(basename $LIB_DIR)
        PACKAGE_NAME=${DIR_NAME//-/_}
        PACKAGE_DIR=$LIB_DIR/$PACKAGE_NAME
        if [ -d $PACKAGE_DIR ]; then
            ln -s $PACKAGE_DIR $BASE_SOURCE_PATH/$PACKAGE_NAME
        fi
    done

    echo "configs-admin update package -- fill service"
    ln -s $CONFIGS_ADMIN_DIR/configs_admin \
          $BASE_SOURCE_PATH/configs_admin

    ls $BASE_SOURCE_PATH
    echo "configs-admin update package -- fill nginx"
    ln -sf $CONFIGS_ADMIN_DIR/debian/yandex-taxi-configs-admin-web.nginx \
           /etc/nginx/sites-available/yandex-taxi-configs-admin-web
    ln -sf $CONFIGS_ADMIN_DIR/debian/yandex-taxi-configs-admin-web.upstream_list.production \
           /etc/nginx/conf.d/99-yandex-taxi-configs-admin-web-upstream

    echo "configs-admin update package -- fill settings"
    if [ -f $SETTINGS_PROD ]; then
        ln -s $SETTINGS_PROD /etc/yandex/taxi-configs-admin-web/settings.yaml
    fi

    echo "configs-admin successfully custom update package"
fi
echo "Done configure"

for num in {01..16}; do
    ln -sf yandex_taxi_configs_admin_web_00.sock /tmp/yandex_taxi_configs_admin_web_${num}.sock
done

echo "run configs-admin"
/taxi/tools/run.py \
    --syslog \
    --wait \
      mongo.taxi.yandex:27017 \
      http://configs.taxi.yandex.net/ping \
    --nginx yandex-taxi-configs-admin-web \
    --stdout-to-log \
    --run /bin/bash -c "\
        /usr/lib/yandex/taxi-py3-2/bin/python3.7 \
          -m configs_admin.generated.web.run_web \
          --path=/tmp/yandex_taxi_configs_admin_web_00.sock \
          --instance=00"
