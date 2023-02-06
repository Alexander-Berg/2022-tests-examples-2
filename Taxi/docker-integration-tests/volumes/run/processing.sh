#!/usr/bin/env bash
set -e

PROCAAS_PATH=/arcadia/procaas
USERVICES_PATH=/arcadia/taxi/uservices
PROCESSING_PATH=$USERVICES_PATH/build-integration/services/processing
PROCESSING_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/processing
PROCESSING_SRC_PATH=$USERVICES_PATH/services/processing
PROCESSING_DEB_PATH=$PROCESSING_SRC_PATH/debian

SANDBOX_EXTERNAL=/taxi/sandbox/procaas
SANDBOX_HOME=/etc/yandex/taxi/processing/sandbox-home

PROCESSING_BINARY_PATH=
if [ -f "$PROCESSING_PATH/yandex-taxi-processing" ]; then
  PROCESSING_BINARY_PATH="$PROCESSING_PATH/yandex-taxi-processing"
elif [ -f "$PROCESSING_ARCADIA_PATH/yandex-taxi-processing" ]; then
  PROCESSING_BINARY_PATH="$PROCESSING_ARCADIA_PATH/yandex-taxi-processing"
fi

if [ -d "$PROCESSING_PATH/units" ]; then
    echo "multiunit processing"
    PROCESSING_UNIT_ROOT="$PROCESSING_PATH/units/processing"
else
    echo "single unit processing"
    PROCESSING_UNIT_ROOT="$PROCESSING_PATH"
fi

if [ -f "$PROCESSING_BINARY_PATH" ]; then
    echo "processing update package"
    mkdir -p /etc/yandex/taxi/processing/
    rm -rf /etc/yandex/taxi/processing/*

    cp $PROCESSING_UNIT_ROOT/configs/* /etc/yandex/taxi/processing/
    cp $PROCESSING_UNIT_ROOT/config.yaml /etc/yandex/taxi/processing/

    ln -s $PROCESSING_PATH/taxi_config_fallback.json /etc/yandex/taxi/processing/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/processing/
    ln -s config_vars.production.yaml /etc/yandex/taxi/processing/config_vars.yaml

    ln -sf $PROCESSING_DEB_PATH/yandex-taxi-processing.nginx /etc/nginx/sites-available/yandex-taxi-processing
    ln -sf $PROCESSING_DEB_PATH/yandex-taxi-processing.upstream_list /etc/nginx/conf.d/

    ln -sf $PROCESSING_UNIT_ROOT/taxi-processing-stats.py /usr/bin/

    echo "using binary: $PROCESSING_BINARY_PATH"
    ln -sf $PROCESSING_BINARY_PATH /usr/bin/
fi

# Extract AGL modules
mkdir -p $SANDBOX_HOME/taxi

echo "[debug]"
echo 'ls -la $SANDBOX_EXTERNAL'
ls -la $SANDBOX_EXTERNAL
echo 'ls -la $SANDBOX_EXTERNAL/taxi'
ls -la $SANDBOX_EXTERNAL/taxi
echo 'ls -la $SANDBOX_EXTERNAL/taxi/agl-modules.tar'
ls -la $SANDBOX_EXTERNAL/taxi/agl-modules.tar
echo 'ls -la $SANDBOX_HOME/taxi'
ls -la $SANDBOX_HOME/taxi

tar -xvf $SANDBOX_EXTERNAL/taxi/agl-modules.tar -C $SANDBOX_HOME/taxi

#make fetch-taxi-modules -C $PROCAAS_PATH TAXI_MODULES_OUTPUT_PATH=$SANDBOX_HOME/taxi TAXI_DOCKER_TESTS_BRANCH=$TAXI_BRANCH

# fixup config_vars: set sandbox home
CONFIG_VARS=/etc/yandex/taxi/processing/config_vars.yaml
SANDBOX_HOME_ESCAPED=$(echo "$SANDBOX_HOME" | sed 's/\//\\\//g')
sed -ie "s/agl-modules-docker-prefix:.*/agl-modules-docker-prefix:/g" $CONFIG_VARS
sed -ie "s/agl-modules-sandbox-home:.*/agl-modules-sandbox-home: $SANDBOX_HOME_ESCAPED/g" $CONFIG_VARS


/usr/lib/yandex/taxi-py3-2/bin/pgmigrate -c "host=pgaas.mail.yandex.net port=5432 user=user password=password dbname=processing_db" \
     -t latest -d /taxi/pgmigrate/processing_db migrate
/usr/lib/yandex/taxi-py3-2/bin/pgmigrate -c "host=pgaas.mail.yandex.net port=5432 user=user password=password dbname=processing_db_1" \
     -t latest -d /taxi/pgmigrate/processing_db migrate
/usr/lib/yandex/taxi-py3-2/bin/pgmigrate -c "host=pgaas.mail.yandex.net port=5432 user=user password=password dbname=processing_db_2" \
     -t latest -d /taxi/pgmigrate/processing_db migrate
/usr/lib/yandex/taxi-py3-2/bin/pgmigrate -c "host=pgaas.mail.yandex.net port=5432 user=user password=password dbname=processing_noncritical_db" \
     -t latest -d /taxi/pgmigrate/processing_noncritical_db migrate

mkdir -p /var/log/yandex/taxi-processing/
mkdir -p /var/lib/yandex/taxi-processing/
mkdir -p /var/lib/yandex/taxi-processing/private/
mkdir -p /var/cache/yandex/taxi-processing/
ln -sf /taxi/logs/application-taxi-processing.log /var/log/yandex/taxi-processing/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-processing \
    --fix-userver-client-timeout /etc/yandex/taxi/processing/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-processing \
        --config /etc/yandex/taxi/processing/config.yaml \
        --init-log /var/log/yandex/taxi-processing/server.log

