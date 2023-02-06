#!/usr/bin/env bash
set -e

REPO_DIR=/taxi/backend-py3
ESLOGADMINPY3_DIR=$REPO_DIR/services/eslogadminpy3
ESLOGADMINPY3_GENERATED_DIR=$ESLOGADMINPY3_DIR/eslogadminpy3/generated
SETTINGS_PROD=$ESLOGADMINPY3_GENERATED_DIR/service/settings/settings.production

if [ -d $ESLOGADMINPY3_GENERATED_DIR ]; then
    echo "eslogadminpy3 update package"
    mkdir -p /var/cache/yandex/taxi/configs/
    chown -R www-data:www-data /var/cache/yandex/taxi/configs
    mkdir -p /usr/lib/yandex/taxi-eslogadminpy3-web/ \
             /etc/yandex/taxi-eslogadminpy3-web/
    rm -rf /usr/lib/yandex/taxi-eslogadminpy3-web/* \
           /etc/yandex/taxi-eslogadminpy3-web/*
    ln -s $REPO_DIR/taxi /usr/lib/yandex/taxi-eslogadminpy3-web/taxi
    if [ -d $REPO_DIR/generated ]; then
      ln -s $REPO_DIR/generated /usr/lib/yandex/taxi-eslogadminpy3-web/generated
    fi
    for LIB_DIR in $REPO_DIR/libraries/*; do
        DIR_NAME=$(basename $LIB_DIR)
        PACKAGE_NAME=${DIR_NAME//-/_}
        PACKAGE_DIR=$LIB_DIR/$PACKAGE_NAME
        if [ -d $PACKAGE_DIR ]; then
            ln -s $PACKAGE_DIR /usr/lib/yandex/taxi-eslogadminpy3-web/$PACKAGE_NAME
        fi
    done
    ln -s $ESLOGADMINPY3_DIR/eslogadminpy3 \
          /usr/lib/yandex/taxi-eslogadminpy3-web/eslogadminpy3
    ln -sf $ESLOGADMINPY3_DIR/debian/yandex-taxi-eslogadminpy3-web.nginx \
           /etc/nginx/sites-available/yandex-taxi-eslogadminpy3
    ln -sf $ESLOGADMINPY3_DIR/debian/yandex-taxi-eslogadminpy3-web.upstream_list.production \
           /etc/nginx/conf.d/99-yandex-taxi-eslogadminpy3-web-upstream
    ln -sf $ESLOGADMINPY3_DIR/debian/yandex-taxi-eslogadminpy3-web.nginx \
        /etc/nginx/sites-available/yandex-taxi-eslogadminpy3-web
    ln -sf $ESLOGADMINPY3_DIR/debian/yandex-taxi-eslogadminpy3-web.upstream_list.production \
        /etc/nginx/conf.d/99-yandex-taxi-eslogadminpy3-web-upstream
    if [ -f $SETTINGS_PROD ]; then
        ln -s $SETTINGS_PROD /etc/yandex/taxi-eslogadminpy3-web/settings.yaml
    fi
fi

# Wait for elastic-search and then bring to a fake entry to it
/taxi/tools/run.py \
    --wait \
        elasticsearch.taxi.yandex:9200 \
    --run curl -d '{"@timestamp":"2009-11-15T14:12:12Z"}' -H "Content-Type: application/json" \
        -X POST 'http://elasticsearch.taxi.yandex:9200/yandex-taxi-archive/_doc/'

for num in {01..16}; do
    ln -sf yandex_taxi_eslogadminpy3_web_00.sock /tmp/yandex_taxi_eslogadminpy3_web_${num}.sock
done

/taxi/tools/run.py \
    --syslog \
    --nginx yandex-taxi-eslogadminpy3-web \
    --run su www-data -s /bin/bash -c "/usr/lib/yandex/taxi-py3-2/bin/python3.7 \
          -m eslogadminpy3.generated.web.run_web --path=/tmp/yandex_taxi_eslogadminpy3_web_00.sock \
          --instance=00"
