#!/usr/bin/env bash
set -e

REPO_DIR=/taxi/backend-py3
TARIFFS_DIR=$REPO_DIR/taxi-tariffs
TARIFFS_DIR=$REPO_DIR/services/taxi-tariffs
TARIFFS_GENERATED_DIR=${TARIFFS_DIR}/taxi_tariffs/generated
SETTINGS_PROD=$TARIFFS_GENERATED_DIR/service/settings/settings.production

if [ -d $TARIFFS_GENERATED_DIR ]; then
    echo "tariffs update package"
    mkdir -p /var/cache/yandex/taxi/configs/
    chown -R www-data:www-data /var/cache/yandex/taxi/configs
    mkdir -p /usr/lib/yandex/taxi-tariffs-web/ \
             /etc/yandex/taxi-tariffs-web/
    rm -rf /usr/lib/yandex/taxi-tariffs-web/* \
           /etc/yandex/taxi-tariffs-web/*
    ln -s  $REPO_DIR/taxi \
           /usr/lib/yandex/taxi-tariffs-web/taxi
    if [ -d $REPO_DIR/generated ]; then
      ln -s $REPO_DIR/generated /usr/lib/yandex/taxi-tariffs-web/generated
    fi
    for LIB_DIR in $REPO_DIR/libraries/*; do
        DIR_NAME=$(basename $LIB_DIR)
        PACKAGE_NAME=${DIR_NAME//-/_}
        PACKAGE_DIR=$LIB_DIR/$PACKAGE_NAME
        if [ -d $PACKAGE_DIR ]; then
            ln -s $PACKAGE_DIR /usr/lib/yandex/taxi-tariffs-web/$PACKAGE_NAME
        fi
    done
    ln -s  $TARIFFS_DIR/taxi_tariffs \
           /usr/lib/yandex/taxi-tariffs-web/taxi_tariffs
    ln -sf $TARIFFS_DIR/debian/yandex-taxi-tariffs.nginx \
        /etc/nginx/sites-available/yandex-taxi-tariffs
    ln -sf $TARIFFS_DIR/debian/yandex-taxi-tariffs.upstream_list.production \
        /etc/nginx/conf.d/99-yandex-taxi-tariffs-web-upstream
    if [ -f $SETTINGS_PROD ]; then
        ln -sf $SETTINGS_PROD /etc/yandex/taxi-tariffs-web/settings.yaml
    fi
fi

for num in {01..16}; do
    ln -sf yandex_taxi_tariffs_web_00.sock /tmp/yandex_taxi_tariffs_web_${num}.sock
done

/taxi/tools/run.py \
    --syslog \
    --wait \
      mongo.taxi.yandex:27017 \
      http://configs.taxi.yandex.net/ping \
    --nginx yandex-taxi-tariffs \
    --run su www-data -s /bin/bash \
        -c "/usr/lib/yandex/taxi-py3-2/bin/python3.7 -m taxi_tariffs.generated.web.run_web \
            --path /tmp/yandex_taxi_tariffs_web_00.sock --instance 00"
