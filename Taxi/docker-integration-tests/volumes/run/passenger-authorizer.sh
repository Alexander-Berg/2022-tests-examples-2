#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
PASSENGER_AUTHORIZER_PATH=$USERVICES_PATH/build-integration/services/passenger-authorizer
PASSENGER_AUTHORIZER_PATH_UNIT=$USERVICES_PATH/build-integration/services/passenger-authorizer/units/passenger-authorizer/
PASSENGER_AUTHORIZER_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/passenger-authorizer
PASSENGER_AUTHORIZER_DEB_PATH=$USERVICES_PATH/services/passenger-authorizer/debian

PASSENGER_AUTHORIZER_BINARY_PATH=
if [ -f "$PASSENGER_AUTHORIZER_PATH/yandex-taxi-passenger-authorizer" ]; then
  PASSENGER_AUTHORIZER_BINARY_PATH="$PASSENGER_AUTHORIZER_PATH/yandex-taxi-passenger-authorizer"
elif [ -f "$PASSENGER_AUTHORIZER_ARCADIA_PATH/yandex-taxi-passenger-authorizer" ]; then
  PASSENGER_AUTHORIZER_BINARY_PATH="$PASSENGER_AUTHORIZER_ARCADIA_PATH/yandex-taxi-passenger-authorizer"
fi

if [ -f "$PASSENGER_AUTHORIZER_BINARY_PATH" ]; then
    echo "passenger-authorizer update package"
    mkdir -p /etc/yandex/taxi/passenger-authorizer/
    mkdir -p /etc/nginx/sites-production/
    mkdir -p /etc/nginx/includes/
    rm -rf /etc/yandex/taxi/passenger-authorizer/* ||:
    if [ -e $PASSENGER_AUTHORIZER_PATH/config.yaml ]; then
        ln -s $PASSENGER_AUTHORIZER_PATH/configs/* /etc/yandex/taxi/passenger-authorizer/
        cp $PASSENGER_AUTHORIZER_PATH/config.yaml /etc/yandex/taxi/passenger-authorizer/
    else
        ln -s $PASSENGER_AUTHORIZER_PATH_UNIT/configs/* /etc/yandex/taxi/passenger-authorizer/
        cp $PASSENGER_AUTHORIZER_PATH_UNIT/config.yaml /etc/yandex/taxi/passenger-authorizer/
    fi
    ln -s $PASSENGER_AUTHORIZER_PATH/taxi_config_fallback.json /etc/yandex/taxi/passenger-authorizer/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/passenger-authorizer/
    ln -s config_vars.production.yaml /etc/yandex/taxi/passenger-authorizer/config_vars.yaml

    ln -sf $PASSENGER_AUTHORIZER_PATH/taxi-passenger-authorizer-stats.py /usr/bin/

    ln -sf $USERVICES_PATH/services/passenger-authorizer/nginx/taxi-client/yandex-taxi-client-proxy.production.conf /etc/nginx/sites-production/yandex-taxi-client-proxy.production.conf
    ln -sf $USERVICES_PATH/services/passenger-authorizer/nginx/taxi-client/yandex-taxi-client-proxy-upstream.production.conf /etc/nginx/includes/yandex-taxi-client-proxy-upstream.production.conf
    ln -sf $USERVICES_PATH/services/passenger-authorizer/nginx/taxi-client/yandex-taxi-client-proxy-locations-pa.conf /etc/nginx/includes/yandex-taxi-client-proxy-locations-pa.conf
    ln -sf $USERVICES_PATH/services/passenger-authorizer/nginx/taxi-client/yandex-taxi-client-proxy-locations-const.conf /etc/nginx/includes/yandex-taxi-client-proxy-locations-const.conf
    ln -sf $USERVICES_PATH/services/passenger-authorizer/nginx/taxi-client/yandex-taxi-client-proxy-locations-support.conf /etc/nginx/includes/yandex-taxi-client-proxy-locations-support.conf

    echo "using binary: $PASSENGER_AUTHORIZER_BINARY_PATH"
    ln -sf $PASSENGER_AUTHORIZER_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-passenger-authorizer/
mkdir -p /var/log/yandex/taxi-passenger-authorizer/
ln -sf /taxi/logs/application-taxi-passenger-authorizer.log /var/log/yandex/taxi-passenger-authorizer/server.log
ln -sf /etc/nginx/sites-production/yandex-taxi-client-proxy.production.conf /etc/nginx/sites-available/yandex-taxi-client-proxy

mkdir -p /var/run/yandex/taxi-passenger-authorizer/private/
mkdir -p /var/lib/yandex/taxi-passenger-authorizer/private/

touch /var/run/tc-alive

/taxi/tools/run.py \
    --nginx yandex-taxi-client-proxy \
    --syslog \
    --fix-userver-client-timeout /etc/yandex/taxi/passenger-authorizer/config.yaml \
    --wait \
        taxi-protocol.taxi.yandex.net:80 \
        mapsuggest-internal.yandex.net:80 \
        http://configs.taxi.yandex.net/ping \
        mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-passenger-authorizer \
        --config /etc/yandex/taxi/passenger-authorizer/config.yaml \
        --init-log /var/log/yandex/taxi-passenger-authorizer/server.log
