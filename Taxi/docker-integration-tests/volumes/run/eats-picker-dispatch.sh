#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
EATS_PICKER_DISPATCH_PATH=$USERVICES_PATH/build-integration/services/eats-picker-dispatch
EATS_PICKER_DISPATCH_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/eats-picker-dispatch
EATS_PICKER_DISPATCH_DEB_PATH=$USERVICES_PATH/services/eats-picker-dispatch/debian

EATS_PICKER_DISPATCH_BINARY_PATH=
if [ -f "$EATS_PICKER_DISPATCH_PATH/yandex-taxi-eats-picker-dispatch" ]; then
  EATS_PICKER_DISPATCH_BINARY_PATH="$EATS_PICKER_DISPATCH_PATH/yandex-taxi-eats-picker-dispatch"
elif [ -f "$EATS_PICKER_DISPATCH_ARCADIA_PATH/yandex-taxi-eats-picker-dispatch" ]; then
  EATS_PICKER_DISPATCH_BINARY_PATH="$EATS_PICKER_DISPATCH_ARCADIA_PATH/yandex-taxi-eats-picker-dispatch"
fi

if [ -f "$EATS_PICKER_DISPATCH_BINARY_PATH" ]; then
    echo "eats-picker-dispatch update package"
    mkdir -p /etc/yandex/taxi/eats-picker-dispatch/
    rm -rf /etc/yandex/taxi/eats-picker-dispatch/*

    ln -s $EATS_PICKER_DISPATCH_PATH/configs/* /etc/yandex/taxi/eats-picker-dispatch/
    cp $EATS_PICKER_DISPATCH_PATH/config.yaml /etc/yandex/taxi/eats-picker-dispatch/
    ln -s $EATS_PICKER_DISPATCH_PATH/taxi_config_fallback.json /etc/yandex/taxi/eats-picker-dispatch/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/eats-picker-dispatch/
    ln -s config_vars.production.yaml /etc/yandex/taxi/eats-picker-dispatch/config_vars.yaml

    ln -sf $EATS_PICKER_DISPATCH_DEB_PATH/yandex-taxi-eats-picker-dispatch.nginx /etc/nginx/sites-available/yandex-taxi-eats-picker-dispatch
    ln -sf $EATS_PICKER_DISPATCH_DEB_PATH/yandex-taxi-eats-picker-dispatch.upstream_list /etc/nginx/conf.d/

    ln -sf $EATS_PICKER_DISPATCH_PATH/taxi-eats-picker-dispatch-stats.py /usr/bin/
    echo "using binary: $EATS_PICKER_DISPATCH_BINARY_PATH"
    ln -sf $EATS_PICKER_DISPATCH_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-eats-picker-dispatch/
mkdir -p /var/lib/yandex/taxi-eats-picker-dispatch/
mkdir -p /var/lib/yandex/taxi-eats-picker-dispatch/private/
mkdir -p /var/cache/yandex/taxi-eats-picker-dispatch/
ln -sf /taxi/logs/application-taxi-eats-picker-dispatch.log /var/log/yandex/taxi-eats-picker-dispatch/server.log

cat > /etc/nginx/conf.d/03-increased-timeout.conf <<EOF
    proxy_read_timeout 120;
EOF

/taxi/tools/run.py \
    --nginx yandex-taxi-eats-picker-dispatch \
    --fix-userver-client-timeout /etc/yandex/taxi/eats-picker-dispatch/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-eats-picker-dispatch \
        --config /etc/yandex/taxi/eats-picker-dispatch/config.yaml \
        --init-log /var/log/yandex/taxi-eats-picker-dispatch/server.log
