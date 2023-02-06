#!/usr/bin/env bash
set -e

REPO_DIR=/taxi/backend-py3
CLOWNDUCTOR_DIR=$REPO_DIR/services/clownductor
CLOWNDUCTOR_GENERATED_DIR=${CLOWNDUCTOR_DIR}/clownductor/generated/
SETTINGS_PROD=$CLOWNDUCTOR_GENERATED_DIR/service/settings/settings.production
if [ -d "$CLOWNDUCTOR_GENERATED_DIR" ]; then
    echo "clownductor update package"
    mkdir -p /var/cache/yandex/taxi/configs/
    mkdir -p /etc/yandex/taxi-clownductor-web/
    chown -R www-data:www-data /var/cache/yandex/taxi/configs
    mkdir -p /usr/lib/yandex/taxi-clownductor-web/ \
           /etc/yandex/taxi-clownductor-web/
    rm -rf /usr/lib/yandex/taxi-clownductor-web/* \
           /etc/yandex/taxi-clownductor-web/*
    mkdir -p /var/cache/yandex/taxi/clownductor/
    chown -R www-data:www-data /var/cache/yandex/taxi/clownductor/
    mkdir -p /var/cache/yandex/taxi/clownductor/files/

    mkdir -p /etc/ssl/certs
    ln -s /taxi/tools/YandexInternalRootCA.pem /etc/ssl/certs
    ln -s $REPO_DIR/taxi /usr/lib/yandex/taxi-clownductor-web/taxi
    if [ -d $REPO_DIR/generated ]; then
      ln -s $REPO_DIR/generated /usr/lib/yandex/taxi-clownductor-web/generated
      cp -r $REPO_DIR/generated/proto/* /usr/lib/yandex/taxi-clownductor-web/
    fi
    for LIB_DIR in $REPO_DIR/libraries/*; do
        DIR_NAME=$(basename $LIB_DIR)
        PACKAGE_NAME=${DIR_NAME//-/_}
        PACKAGE_DIR=$LIB_DIR/$PACKAGE_NAME
        if [ -d $PACKAGE_DIR ]; then
            ln -s $PACKAGE_DIR /usr/lib/yandex/taxi-clownductor-web/$PACKAGE_NAME
        fi
    done
    ln -s $CLOWNDUCTOR_DIR/clownductor \
          /usr/lib/yandex/taxi-clownductor-web/clownductor
    ln -sf $CLOWNDUCTOR_DIR/debian/yandex-taxi-clownductor-web.nginx \
           /etc/nginx/sites-available/yandex-taxi-clownductor-web
    ln -sf $CLOWNDUCTOR_DIR/debian/yandex-taxi-clownductor-web.upstream_list.production \
           /etc/nginx/conf.d/99-yandex-taxi-clownductor-web-upstream
    if [ -f $SETTINGS_PROD ]; then
        ln -s $SETTINGS_PROD /etc/yandex/taxi-clownductor-web/settings.yaml
    fi
fi

for num in {01..16}; do
    ln -sf yandex_taxi_clownductor_web_00.sock /tmp/yandex_taxi_clownductor_web_${num}.sock
done

taxi-python3 /taxi/tools/run.py \
    --syslog \
    --wait \
      mongo.taxi.yandex:27017 \
      postgresql:dbclownductor \
      http://configs.taxi.yandex.net/ping \
    --nginx yandex-taxi-clownductor-web \
    --run su www-data -s /bin/bash -c "/usr/lib/yandex/taxi-py3-2/bin/python3.7 \
          -m clownductor.generated.web.run_web --path=/tmp/yandex_taxi_clownductor_web_00.sock \
          --instance=00"
