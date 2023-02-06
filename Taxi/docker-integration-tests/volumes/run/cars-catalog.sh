#!/usr/bin/env bash
set -e

REPO_DIR=/taxi/backend-py3
CARS_CATALOG_DIR=$REPO_DIR/services/cars-catalog
CARS_CATALOG_GENERATED_DIR=$CARS_CATALOG_DIR/cars_catalog/generated
SETTINGS_PROD=$CARS_CATALOG_GENERATED_DIR/service/settings/settings.production

if [ -d $CARS_CATALOG_GENERATED_DIR ]; then
    echo "cars-catalog update package"
    mkdir -p /var/cache/yandex/taxi/configs/
    mkdir -p /etc/yandex/taxi-cars-catalog-web /etc/yandex/taxi-cars-catalog-cron
    chown -R www-data:www-data /var/cache/yandex/taxi/configs
    rm -rf /usr/lib/yandex/taxi-cars-catalog-web/*
    ln -s $REPO_DIR/taxi /usr/lib/yandex/taxi-cars-catalog-web/taxi
    if [ -d $REPO_DIR/generated ]; then
      ln -s $REPO_DIR/generated /usr/lib/yandex/taxi-cars-catalog-web/generated
    fi
    for LIB_DIR in $REPO_DIR/libraries/*; do
        DIR_NAME=$(basename $LIB_DIR)
        PACKAGE_NAME=${DIR_NAME//-/_}
        PACKAGE_DIR=$LIB_DIR/$PACKAGE_NAME
        if [ -d $PACKAGE_DIR ]; then
            ln -s $PACKAGE_DIR /usr/lib/yandex/taxi-cars-catalog-web/$PACKAGE_NAME
        fi
    done
    ln -s $CARS_CATALOG_DIR/cars_catalog \
          /usr/lib/yandex/taxi-cars-catalog-web/cars_catalog
    ln -sf $CARS_CATALOG_DIR/debian/yandex-taxi-cars-catalog-web.nginx \
        /etc/nginx/sites-available/yandex-taxi-cars-catalog-web
    ln -sf $CARS_CATALOG_DIR/debian/yandex-taxi-cars-catalog-web.upstream_list.production \
        /etc/nginx/conf.d/99-yandex-taxi-cars-catalog-web-upstream
    if [ -f $SETTINGS_PROD ]; then
        ln -sf $SETTINGS_PROD /etc/yandex/taxi-cars-catalog-web/settings.yaml
        ln -sf $SETTINGS_PROD /etc/yandex/taxi-cars-catalog-cron/settings.yaml
    fi
fi

/usr/lib/yandex/taxi-py3-2/bin/python3.7 \
    -m cars_catalog.generated.cron.run_cron \
    -d --force -t0 \
    cars_catalog.crontasks.normalize_cars_fields

for num in {01..16}; do
    ln -sf yandex_taxi_cars_catalog_web_00.sock /tmp/yandex_taxi_cars_catalog_web_${num}.sock
done

taxi-python3 /taxi/tools/run.py \
    --syslog \
    --wait \
        postgresql:cars_catalog \
        http://configs.taxi.yandex.net/ping \
    --nginx yandex-taxi-cars-catalog-web \
    --run su www-data -s /bin/bash -c "/usr/lib/yandex/taxi-py3-2/bin/python3.7 \
          -m cars_catalog.generated.web.run_web --path=/tmp/yandex_taxi_cars_catalog_web_00.sock \
          --instance=00"
