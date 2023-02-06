#!/usr/bin/env bash
set -e

DST_DIR=/usr/lib/yandex/taxi-exp
END_TO_PGMIGRATE=pg_migrations/taxi_exp
ALTERNATE_END_TO_PGMIGRATE=pg_migrations/exp
REPO_DIR=/taxi/backend-py3
EXP_DIR=/taxi/backend-py3/services/taxi-exp
SETTINGS_PROD=$EXP_DIR/taxi_exp/generated/service/settings/settings.production
MIGRATE_PATH=$DST_DIR/$END_TO_PGMIGRATE

if [ -d $EXP_DIR/taxi_exp/generated ]; then
    echo "exp update package"
    mkdir -p /var/cache/yandex/taxi/configs/
    chown -R www-data:www-data /var/cache/yandex/taxi/configs
    mkdir -p /var/cache/yandex/taxi/taxi-exp/files/
    chown -R www-data:www-data /var/cache/yandex/taxi/taxi-exp/files/
    mkdir -p /usr/lib/yandex/taxi-exp/ \
             /etc/yandex/taxi-exp/
    rm -rf $DST_DIR/* /etc/yandex/taxi-exp/*

    ln -s /taxi/backend-py3/taxi $DST_DIR
    ln -s $EXP_DIR/taxi_exp $DST_DIR
    cp -r $EXP_DIR/pg_migrations $DST_DIR

    if [ -d $REPO_DIR/generated ]; then
      ln -s $REPO_DIR/generated /usr/lib/yandex/taxi-exp/generated
    fi
    for LIB_DIR in $REPO_DIR/libraries/*; do
        DIR_NAME=$(basename $LIB_DIR)
        PACKAGE_NAME=${DIR_NAME//-/_}
        PACKAGE_DIR=$LIB_DIR/$PACKAGE_NAME
        if [ -d $PACKAGE_DIR ]; then
            ln -s $PACKAGE_DIR /usr/lib/yandex/taxi-exp/$PACKAGE_NAME
        fi
    done

    ln -sf $EXP_DIR/debian/yandex-taxi-exp.nginx \
           /etc/nginx/sites-available/yandex-taxi-exp
    ln -sf $EXP_DIR/debian/yandex-taxi-exp.upstream_list.production \
           /etc/nginx/conf.d/99-yandex-taxi-exp-upstream

    if [ -f $SETTINGS_PROD ]; then
        ln -s $SETTINGS_PROD /etc/yandex/taxi-exp/settings.yaml
    fi
fi

for num in {01..16}; do
    ln -sf yandex_taxi_exp_00.sock /tmp/yandex_taxi_exp_${num}.sock
done

cp -r /taxi/$END_TO_PGMIGRATE/fill_integration_tests $MIGRATE_PATH

echo "exp applying migrations"
taxi-python3 -m pgmigrate \
   -c "host=pgaas.mail.yandex.net port=5432 user=user password=password dbname=dbexp" \
   -t latest -d $MIGRATE_PATH migrate

cd $DST_DIR
cp taxi_exp/stuff/add_experiments_script.py .
taxi-python3 add_experiments_script.py --exp_dir /taxi/pg_migrations/integration-tests

if [ -d taxi_exp/generated ]; then
    APP_MODULE="taxi_exp.generated.web.run_web"
else
    APP_MODULE="taxi_exp.app"
fi

taxi-python3 /taxi/tools/run.py \
    --syslog \
    --wait \
      postgresql:dbexp \
      http://configs.taxi.yandex.net/ping \
    --nginx yandex-taxi-exp \
    --run su www-data -s /bin/bash -c "/usr/lib/yandex/taxi-py3-2/bin/python3.7 \
          -m $APP_MODULE --path=/tmp/yandex_taxi_exp_00.sock \
          --instance=0"
