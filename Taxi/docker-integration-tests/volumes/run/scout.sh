#!/usr/bin/env bash
set -e

REPO_DIR=/taxi/backend-py3
SCOUT_DIR=$REPO_DIR/services/scout
SCOUT_GENERATED_DIR=${SCOUT_DIR}/scout/generated/
SETTINGS_PROD=$SCOUT_GENERATED_DIR/service/settings/settings.production
if [ -d "$SCOUT_GENERATED_DIR" ]; then
    echo "scout update package"
    mkdir -p /var/cache/yandex/taxi/configs/
    mkdir -p /etc/yandex/taxi-scout-web/
    chown -R www-data:www-data /var/cache/yandex/taxi/configs
    mkdir -p /usr/lib/yandex/taxi-scout-web/ \
           /etc/yandex/taxi-scout-web/
    rm -rf /usr/lib/yandex/taxi-scout-web/* \
           /etc/yandex/taxi-scout-web/*
    mkdir -p /var/cache/yandex/taxi/scout/files/

    ln -s $REPO_DIR/taxi /usr/lib/yandex/taxi-scout-web/taxi
    if [ -d $REPO_DIR/generated ]; then
      ln -s $REPO_DIR/generated /usr/lib/yandex/taxi-scout-web/generated
      cp -r $REPO_DIR/generated/proto/* /usr/lib/yandex/taxi-scout-web/
    fi
    for LIB_DIR in $REPO_DIR/libraries/*; do
        DIR_NAME=$(basename $LIB_DIR)
        PACKAGE_NAME=${DIR_NAME//-/_}
        PACKAGE_DIR=$LIB_DIR/$PACKAGE_NAME
        if [ -d $PACKAGE_DIR ]; then
            ln -s $PACKAGE_DIR /usr/lib/yandex/taxi-scout-web/$PACKAGE_NAME
        fi
    done
    ln -s $SCOUT_DIR/scout \
          /usr/lib/yandex/taxi-scout-web/scout
    ln -sf $SCOUT_DIR/debian/yandex-taxi-scout-web.nginx \
           /etc/nginx/sites-available/yandex-taxi-scout-web
    ln -sf $SCOUT_DIR/debian/yandex-taxi-scout-web.upstream_list.production \
           /etc/nginx/conf.d/99-yandex-taxi-scout-web-upstream
    if [ -f $SETTINGS_PROD ]; then
        ln -s $SETTINGS_PROD /etc/yandex/taxi-scout-web/settings.yaml
    fi
fi

for num in {01..16}; do
    ln -sf yandex_taxi_scout_web_00.sock /tmp/yandex_taxi_scout_web_${num}.sock
done

/taxi/tools/run.py \
    --syslog \
    --wait \
      mongo.taxi.yandex:27017 \
      http://configs.taxi.yandex.net/ping \
    --nginx yandex-taxi-scout-web \
    --run su www-data -s /bin/bash -c "/usr/lib/yandex/taxi-py3-2/bin/python3.7 \
          -m scout.generated.web.run_web --path=/tmp/yandex_taxi_scout_web_00.sock \
          --instance=00"
