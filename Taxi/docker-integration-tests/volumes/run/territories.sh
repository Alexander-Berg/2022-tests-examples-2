#!/usr/bin/env bash
set -e

REPO_DIR=/taxi/backend-py3
TERRITORIES_DIR=/taxi/backend-py3/services/taxi-territories
SETTINGS_PROD=$TERRITORIES_DIR/taxi_territories/generated/service/settings/settings.production

if [ -f $TERRITORIES_DIR/debian/yandex-taxi-territories.nginx ]; then
    echo "territories update package"
    mkdir -p /var/cache/yandex/taxi/configs/
    chown -R www-data:www-data /var/cache/yandex/taxi/configs
    mkdir -p /usr/lib/yandex/taxi-territories/ \
             /etc/yandex/taxi-territories/
    rm -rf /usr/lib/yandex/taxi-territories/* \
           /etc/yandex/taxi-territories/*
    ln -s /taxi/backend-py3/taxi /usr/lib/yandex/taxi-territories/taxi
    ln -s $TERRITORIES_DIR/taxi_territories \
          /usr/lib/yandex/taxi-territories/taxi_territories
    if [ -d $REPO_DIR/generated ]; then
        ln -s $REPO_DIR/generated /usr/lib/yandex/taxi-territories/generated
    fi
    for LIB_DIR in $REPO_DIR/libraries/*; do
        DIR_NAME=$(basename $LIB_DIR)
        PACKAGE_NAME=${DIR_NAME//-/_}
        PACKAGE_DIR=$LIB_DIR/$PACKAGE_NAME
        if [ -d $PACKAGE_DIR ]; then
            ln -s $PACKAGE_DIR /usr/lib/yandex/taxi-territories/$PACKAGE_NAME
        fi
    done
    ln -sf /$TERRITORIES_DIR/debian/yandex-taxi-territories.nginx \
           /etc/nginx/sites-available/yandex-taxi-territories
    ln -sf $TERRITORIES_DIR/debian/yandex-taxi-territories.upstream_list.production \
           /etc/nginx/conf.d/99-yandex-taxi-territories-upstream
    ln -sf $TERRITORIES_DIR/debian/yandex-taxi-territories.nginx \
        /etc/nginx/sites-available/yandex-taxi-territories
    ln -sf $TERRITORIES_DIR/debian/yandex-taxi-territories.upstream_list.production \
        /etc/nginx/conf.d/99-yandex-taxi-territories-upstream
    if [ -f $SETTINGS_PROD ]; then
        ln -s $SETTINGS_PROD /etc/yandex/taxi-territories/settings.yaml
    fi
fi

if [ -d taxi_territories/generated ]; then
    APP_MODULE="taxi_territories.generated.web.run_web"
else
    APP_MODULE="taxi_territories.app"
fi

/taxi/tools/run.py \
    --syslog \
    --wait \
        mongo.taxi.yandex:27017 \
        http://configs.taxi.yandex.net/ping \
    --nginx yandex-taxi-territories \
    --run su www-data -s /bin/bash -c "/usr/lib/yandex/taxi-py3-2/bin/python3.7 \
          -m $APP_MODULE --path=/tmp/yandex_taxi_territories_00.sock \
          --instance=0"
