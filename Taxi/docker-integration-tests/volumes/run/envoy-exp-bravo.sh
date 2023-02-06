#!/usr/bin/env bash
set -e

REPO_DIR=/taxi/backend-py3
ENVOY_EXP_BRAVO_DIR=$REPO_DIR/services/envoy-exp-bravo
ENVOY_EXP_BRAVO_GENERATED_DIR=${ENVOY_EXP_BRAVO_DIR}/envoy_exp_bravo/generated/
SETTINGS_PROD=$ENVOY_EXP_BRAVO_GENERATED_DIR/service/settings/settings.production
if [ -d "$ENVOY_EXP_BRAVO_GENERATED_DIR" ]; then
    echo "envoy-exp-bravo update package"
    mkdir -p /var/cache/yandex/taxi/configs/
    mkdir -p /etc/yandex/taxi-envoy-exp-bravo-web/
    chown -R www-data:www-data /var/cache/yandex/taxi/configs
    mkdir -p /usr/lib/yandex/taxi-envoy-exp-bravo-web/ \
           /etc/yandex/taxi-envoy-exp-bravo-web/
    rm -rf /usr/lib/yandex/taxi-envoy-exp-bravo-web/* \
           /etc/yandex/taxi-envoy-exp-bravo-web/*
    mkdir -p /var/cache/yandex/taxi/envoy-exp-bravo/files/

    ln -s $REPO_DIR/taxi /usr/lib/yandex/taxi-envoy-exp-bravo-web/taxi
    if [ -d $REPO_DIR/generated ]; then
      ln -s $REPO_DIR/generated /usr/lib/yandex/taxi-envoy-exp-bravo-web/generated
    fi
    for LIB_DIR in $REPO_DIR/libraries/*; do
        DIR_NAME=$(basename $LIB_DIR)
        PACKAGE_NAME=${DIR_NAME//-/_}
        PACKAGE_DIR=$LIB_DIR/$PACKAGE_NAME
        if [ -d $PACKAGE_DIR ]; then
            ln -s $PACKAGE_DIR /usr/lib/yandex/taxi-envoy-exp-bravo-web/$PACKAGE_NAME
        fi
    done
    ln -s $ENVOY_EXP_BRAVO_DIR/envoy_exp_bravo \
          /usr/lib/yandex/taxi-envoy-exp-bravo-web/envoy_exp_bravo
    ln -sf $ENVOY_EXP_BRAVO_DIR/debian/yandex-taxi-envoy-exp-bravo-web.nginx \
           /etc/nginx/sites-available/yandex-taxi-envoy-exp-bravo-web
    ln -sf $ENVOY_EXP_BRAVO_DIR/debian/yandex-taxi-envoy-exp-bravo-web.upstream_list.production \
           /etc/nginx/conf.d/99-yandex-taxi-envoy-exp-bravo-web-upstream
    if [ -f $SETTINGS_PROD ]; then
        ln -s $SETTINGS_PROD /etc/yandex/taxi-envoy-exp-bravo-web/settings.yaml
    fi
fi

for num in {01..16}; do
    ln -sf yandex_taxi_envoy_exp_bravo_web_00.sock /tmp/yandex_taxi_envoy_exp_bravo_web_${num}.sock
done

/taxi/tools/start_envoy.sh taxi_tst_envoy-exp-bravo_stable

/taxi/tools/run.py \
    --syslog \
    --wait \
      mongo.taxi.yandex:27017 \
      http://configs.taxi.yandex.net/ping \
    --nginx yandex-taxi-envoy-exp-bravo-web \
    --run su www-data -s /bin/bash -c "/usr/lib/yandex/taxi-py3-2/bin/python3.7 \
          -m envoy_exp_bravo.generated.web.run_web --path=/tmp/yandex_taxi_envoy_exp_bravo_web_00.sock \
          --instance=00"
