#!/usr/bin/env bash
set -e

REPO_DIR=/taxi/backend-py3
CONFIG_SCHEMAS_DIR=${REPO_DIR}/taxi-config-schemas
if [ -f $REPO_DIR/services/taxi-config-schemas/debian/changelog ]; then
  CONFIG_SCHEMAS_DIR=${REPO_DIR}/services/taxi-config-schemas
fi
CONFIG_SCHEMAS_GENERATED_DIR=${CONFIG_SCHEMAS_DIR}/taxi_config_schemas/generated

if [ -f $CONFIG_SCHEMAS_DIR/debian/changelog ]; then
    NO_CODEGEN=$(grep -c "codegen_disabled: true" $CONFIG_SCHEMAS_DIR/service.yaml ||:)
    if [ $NO_CODEGEN -eq 1 -o -d $CONFIG_SCHEMAS_GENERATED_DIR ]; then
      echo "config-schemas update package"
      mkdir -p /var/cache/yandex/taxi/configs/
      chown -R www-data:www-data /var/cache/yandex/taxi/configs
      mkdir -p /usr/lib/yandex/taxi-config-schemas/ \
               /etc/yandex/taxi-config-schemas/
      rm -rf /usr/lib/yandex/taxi-config-schemas/* \
             /etc/yandex/taxi-config-schemas/*
      ln -s /taxi/backend-py3/taxi /usr/lib/yandex/taxi-config-schemas/taxi
      cp -r $CONFIG_SCHEMAS_DIR/taxi_config_schemas \
            /usr/lib/yandex/taxi-config-schemas/taxi_config_schemas
      ln -sf $CONFIG_SCHEMAS_DIR/debian/yandex-taxi-config-schemas.nginx \
             /etc/nginx/sites-available/yandex-taxi-config-schemas
      ln -sf $CONFIG_SCHEMAS_DIR/debian/yandex-taxi-config-schemas.upstream_list.production \
             /etc/nginx/conf.d/99-yandex-taxi-config-schemas-upstream
      mkdir -p /usr/lib/yandex/taxi-config-schemas/repo
      chown -R www-data:www-data /usr/lib/yandex/taxi-config-schemas/repo
      ln -sf $CONFIG_SCHEMAS_DIR/debian/yandex-taxi-config-schemas.nginx \
          /etc/nginx/sites-available/yandex-taxi-config-schemas
      ln -sf $CONFIG_SCHEMAS_DIR/debian/yandex-taxi-config-schemas.upstream_list.production \
          /etc/nginx/conf.d/99-yandex-taxi-config-schemas-upstream

      if [ -d $CONFIG_SCHEMAS_GENERATED_DIR ]; then
          echo "config-schemas update package with generated"
          SETTINGS_PROD=$CONFIG_SCHEMAS_GENERATED_DIR/service/settings/settings.production
          if [ -d $REPO_DIR/generated ]; then
            ln -s $REPO_DIR/generated /usr/lib/yandex/taxi-config-schemas/generated
            if [ -d $REPO_DIR/generated/fbs ]; then
              ln -s $REPO_DIR/generated/fbs/* /usr/lib/yandex/taxi-config-schemas
            fi
          fi
          for LIB_DIR in $REPO_DIR/libraries/*; do
              DIR_NAME=$(basename $LIB_DIR)
              PACKAGE_NAME=${DIR_NAME//-/_}
              PACKAGE_DIR=$LIB_DIR/$PACKAGE_NAME
              if [ -d $PACKAGE_DIR ]; then
                  ln -s $PACKAGE_DIR /usr/lib/yandex/taxi-config-schemas/$PACKAGE_NAME
              fi
          done
          if [ -f $SETTINGS_PROD ]; then
              ln -sf $SETTINGS_PROD /etc/yandex/taxi-config-schemas/settings.yaml
          fi
      fi
    fi
fi

if [ -f /usr/lib/yandex/taxi-config-schemas/taxi_config_schemas/app.py ]; then
  RUN_MODULE=taxi_config_schemas.app
else
  RUN_MODULE=taxi_config_schemas.generated.web.run_web
fi

# TODO(aselutin): fix repo removing in TAXITOOLS-1637
rm -rf /usr/lib/yandex/taxi-config-schemas/repo/schemas
rm -rf /srv/yandex/taxi/configs/schemas
mkdir -p /srv/yandex/taxi/configs

cp -r /taxi/schemas /srv/yandex/taxi/configs/schemas
rm -rf /srv/yandex/taxi/configs/schemas/.git
git config --global user.email "taxi-robot@yandex-team.com"

cd /srv/yandex/taxi/configs/schemas/
git init
touch README
git add --all
git commit -m "Initial commit"
git branch custom/unstable
git branch custom/testing
git branch develop
cd -

for num in {01..16}; do
    ln -sf yandex_taxi_config_schemas_00.sock /tmp/yandex_taxi_config_schemas_${num}.sock
done

/taxi/tools/run.py \
    --syslog \
    --wait \
        mongo.taxi.yandex:27017 \
    --nginx yandex-taxi-config-schemas \
    --run su www-data -s /bin/bash -c "/usr/lib/yandex/taxi-py3-2/bin/python3.7 \
          -m $RUN_MODULE --path=/tmp/yandex_taxi_config_schemas_00.sock \
          --instance=00"
