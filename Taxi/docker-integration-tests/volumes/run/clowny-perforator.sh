#!/usr/bin/env bash
set -e

REPO_DIR=/taxi/backend-py3
CLOWNY_PERFORATOR_DIR=$REPO_DIR/services/clowny-perforator
CLOWNY_PERFORATOR_GENERATED_DIR=${CLOWNY_PERFORATOR_DIR}/clowny_perforator/generated/
SETTINGS_PROD=$CLOWNY_PERFORATOR_GENERATED_DIR/service/settings/settings.production
if [ -d "$CLOWNY_PERFORATOR_GENERATED_DIR" ]; then
    echo "clowny-perforator update package"
    mkdir -p /var/cache/yandex/taxi/configs/
    mkdir -p /etc/yandex/taxi-clowny-perforator-web/
    chown -R www-data:www-data /var/cache/yandex/taxi/configs
    mkdir -p /usr/lib/yandex/taxi-clowny-perforator-web/ \
           /etc/yandex/taxi-clowny-perforator-web/
    rm -rf /usr/lib/yandex/taxi-clowny-perforator-web/* \
           /etc/yandex/taxi-clowny-perforator-web/*
    mkdir -p /var/cache/yandex/taxi/clowny-perforator/files/

    ln -s $REPO_DIR/taxi /usr/lib/yandex/taxi-clowny-perforator-web/taxi
    if [ -d $REPO_DIR/generated ]; then
      ln -s $REPO_DIR/generated /usr/lib/yandex/taxi-clowny-perforator-web/generated
    fi
    for LIB_DIR in $REPO_DIR/libraries/*; do
        DIR_NAME=$(basename $LIB_DIR)
        PACKAGE_NAME=${DIR_NAME//-/_}
        PACKAGE_DIR=$LIB_DIR/$PACKAGE_NAME
        if [ -d $PACKAGE_DIR ]; then
            ln -s $PACKAGE_DIR /usr/lib/yandex/taxi-clowny-perforator-web/$PACKAGE_NAME
        fi
    done
    ln -s $CLOWNY_PERFORATOR_DIR/clowny_perforator \
          /usr/lib/yandex/taxi-clowny-perforator-web/clowny_perforator
    ln -sf $CLOWNY_PERFORATOR_DIR/debian/yandex-taxi-clowny-perforator-web.nginx \
           /etc/nginx/sites-available/yandex-taxi-clowny-perforator-web
    ln -sf $CLOWNY_PERFORATOR_DIR/debian/yandex-taxi-clowny-perforator-web.upstream_list.production \
           /etc/nginx/conf.d/99-yandex-taxi-clowny-perforator-web-upstream
    if [ -f $SETTINGS_PROD ]; then
        ln -s $SETTINGS_PROD /etc/yandex/taxi-clowny-perforator-web/settings.yaml
    fi
fi

for num in {01..16}; do
    ln -sf yandex_taxi_clowny_perforator_web_00.sock /tmp/yandex_taxi_clowny_perforator_web_${num}.sock
done

taxi-python3 /taxi/tools/run.py \
    --syslog \
    --wait \
      mongo.taxi.yandex:27017 \
      postgresql:dbclowny-perforator \
      http://configs.taxi.yandex.net/ping \
    --nginx yandex-taxi-clowny-perforator-web \
    --run su www-data -s /bin/bash -c "/usr/lib/yandex/taxi-py3-2/bin/python3.7 \
          -m clowny_perforator.generated.web.run_web --path=/tmp/yandex_taxi_clowny_perforator_web_00.sock \
          --instance=00"
