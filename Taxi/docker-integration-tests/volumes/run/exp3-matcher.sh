#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
EXP3_MATCHER_PATH=$USERVICES_PATH/build-integration/services/exp3-matcher
EXP3_MATCHER_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/exp3-matcher
EXP3_MATCHER_UNIT_PATH=$EXP3_MATCHER_PATH/units/exp3-matcher
EXP3_MATCHER_DEB_PATH=$USERVICES_PATH/services/exp3-matcher/debian

EXP3_MATCHER_BINARY_PATH=
if [ -f "$EXP3_MATCHER_PATH/yandex-taxi-exp3-matcher" ]; then
  EXP3_MATCHER_BINARY_PATH="$EXP3_MATCHER_PATH/yandex-taxi-exp3-matcher"
  echo "using binary: $EXP3_MATCHER_BINARY_PATH"
elif [ -f "$EXP3_MATCHER_ARCADIA_PATH/yandex-taxi-exp3-matcher" ]; then
  EXP3_MATCHER_BINARY_PATH="$EXP3_MATCHER_ARCADIA_PATH/yandex-taxi-exp3-matcher"
  echo "using binary: $EXP3_MATCHER_BINARY_PATH"
fi

if [ -f "$EXP3_MATCHER_BINARY_PATH" ]; then
    echo "exp3-matcher update package"
    mkdir -p /etc/yandex/taxi/exp3-matcher/
    rm -rf /etc/yandex/taxi/exp3-matcher/*
    mkdir -p /var/lib/yandex/taxi-exp3-matcher/

    if [ -d $EXP3_MATCHER_PATH/configs/ ]; then
        ln -s $EXP3_MATCHER_PATH/configs/* /etc/yandex/taxi/exp3-matcher/
    else
        ln -s $EXP3_MATCHER_UNIT_PATH/configs/* /etc/yandex/taxi/exp3-matcher/
    fi

    cp $EXP3_MATCHER_PATH/config.yaml /etc/yandex/taxi/exp3-matcher/ || \
        cp $EXP3_MATCHER_UNIT_PATH/config.yaml /etc/yandex/taxi/exp3-matcher/
    ln -s $EXP3_MATCHER_PATH/taxi_config_fallback.json /etc/yandex/taxi/exp3-matcher/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/exp3-matcher/
    ln -s config_vars.production.yaml /etc/yandex/taxi/exp3-matcher/config_vars.yaml

    ln -sf $EXP3_MATCHER_DEB_PATH/yandex-taxi-exp3-matcher.nginx /etc/nginx/sites-available/yandex-taxi-exp3-matcher
    ln -sf $EXP3_MATCHER_DEB_PATH/yandex-taxi-exp3-matcher.upstream_list /etc/nginx/conf.d/

    ln -sf $EXP3_MATCHER_PATH/taxi-exp3-matcher-stats.py /usr/bin/ || \
        ln -sf $EXP3_MATCHER_UNIT_PATH/taxi-exp3-matcher-stats.py /usr/bin/

    echo "using binary: $EXP3_MATCHER_BINARY_PATH"
    ln -sf $EXP3_MATCHER_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-exp3-matcher/
mkdir -p /var/log/yandex/taxi-exp3-matcher/
ln -sf /taxi/logs/application-taxi-exp3-matcher.log /var/log/yandex/taxi-exp3-matcher/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-exp3-matcher \
    --fix-userver-client-timeout /etc/yandex/taxi/exp3-matcher/config.yaml \
    --wait \
        http://exp.taxi.yandex.net/ping \
        http://configs.taxi.yandex.net/ping \
        http://experiments3-proxy.taxi.yandex.net/ping \
    --run /usr/bin/yandex-taxi-exp3-matcher \
    --config /etc/yandex/taxi/exp3-matcher/config.yaml \
    --init-log /var/log/yandex/taxi-exp3-matcher/server.log
