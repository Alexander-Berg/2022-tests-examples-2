#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
DRIVER_STATUS_PATH=$USERVICES_PATH/build-integration/services/driver-status
DRIVER_STATUS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/driver-status
DRIVER_STATUS_DEB_PATH=$USERVICES_PATH/services/driver-status/debian

DRIVER_STATUS_BINARY_PATH=
if [ -f "$DRIVER_STATUS_PATH/yandex-taxi-driver-status" ]; then
  DRIVER_STATUS_BINARY_PATH="$DRIVER_STATUS_PATH/yandex-taxi-driver-status"
elif [ -f "$DRIVER_STATUS_ARCADIA_PATH/yandex-taxi-driver-status" ]; then
  DRIVER_STATUS_BINARY_PATH="$DRIVER_STATUS_ARCADIA_PATH/yandex-taxi-driver-status"
fi

if [ -f "$DRIVER_STATUS_BINARY_PATH" ]; then
    echo "driver-status update package"
    mkdir -p /etc/yandex/taxi/driver-status/
    rm -rf /etc/yandex/taxi/driver-status/*

    ln -s $DRIVER_STATUS_PATH/configs/* /etc/yandex/taxi/driver-status/
    cp $DRIVER_STATUS_PATH/config.yaml /etc/yandex/taxi/driver-status/
    ln -s $DRIVER_STATUS_PATH/taxi_config_fallback.json /etc/yandex/taxi/driver-status/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/driver-status/
    ln -s config_vars.production.yaml /etc/yandex/taxi/driver-status/config_vars.yaml

    ln -sf $DRIVER_STATUS_DEB_PATH/yandex-taxi-driver-status.nginx /etc/nginx/sites-available/yandex-taxi-driver-status
    ln -sf $DRIVER_STATUS_DEB_PATH/yandex-taxi-driver-status.upstream_list /etc/nginx/conf.d/

    ln -sf $DRIVER_STATUS_PATH/taxi-driver-status-stats.py /usr/bin/

    echo "using binary: $DRIVER_STATUS_BINARY_PATH"
    ln -sf $DRIVER_STATUS_BINARY_PATH /usr/bin/
fi

/usr/lib/yandex/taxi-py3-2/bin/pgmigrate -c "host=pgaas.mail.yandex.net port=5432 user=user password=password dbname=driver-status" \
    -b 1 -t latest -d /taxi/pgmigrate/driver-status migrate

mkdir -p /var/log/yandex/taxi-driver-status/
mkdir -p /var/lib/yandex/taxi-driver-status/
mkdir -p /var/lib/yandex/taxi-driver-status/private/
mkdir -p /var/cache/yandex/taxi-driver-status/
ln -sf /taxi/logs/application-taxi-driver-status.log /var/log/yandex/taxi-driver-status/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-driver-status \
    --fix-userver-client-timeout /etc/yandex/taxi/driver-status/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-driver-status \
        --config /etc/yandex/taxi/driver-status/config.yaml \
        --init-log /var/log/yandex/taxi-driver-status/server.log

