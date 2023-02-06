#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
STQ_AGENT_PATH=$USERVICES_PATH/build-integration/services/stq-agent
STQ_AGENT_UNIT_PATH=$STQ_AGENT_PATH/units/stq-agent
STQ_AGENT_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/stq-agent
STQ_AGENT_DEB_PATH=$USERVICES_PATH/services/stq-agent/debian

STQ_AGENT_BINARY_PATH=
if [ -f "$STQ_AGENT_PATH/yandex-taxi-stq-agent" ]; then
  STQ_AGENT_BINARY_PATH="$STQ_AGENT_PATH/yandex-taxi-stq-agent"
elif [ -f "$STQ_AGENT_ARCADIA_PATH/yandex-taxi-stq-agent" ]; then
  STQ_AGENT_BINARY_PATH="$STQ_AGENT_ARCADIA_PATH/yandex-taxi-stq-agent"
fi

if [ -f "$STQ_AGENT_BINARY_PATH" ]; then
    echo "stq-agent update package"
    mkdir -p /etc/yandex/taxi/stq-agent/
    rm -rf /etc/yandex/taxi/stq-agent/*

    if [ -e $STQ_AGENT_PATH/config.yaml ]; then
        ln -s $STQ_AGENT_PATH/configs/* /etc/yandex/taxi/stq-agent/
        cp $STQ_AGENT_PATH/config.yaml /etc/yandex/taxi/stq-agent/
    else
        ln -s $STQ_AGENT_UNIT_PATH/configs/* /etc/yandex/taxi/stq-agent/
        cp $STQ_AGENT_UNIT_PATH/config.yaml /etc/yandex/taxi/stq-agent/
    fi

    ln -s $STQ_AGENT_PATH/taxi_config_fallback.json /etc/yandex/taxi/stq-agent/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/stq-agent/
    ln -s config_vars.production.yaml /etc/yandex/taxi/stq-agent/config_vars.yaml

    ln -sf $STQ_AGENT_DEB_PATH/yandex-taxi-stq-agent.nginx /etc/nginx/sites-available/yandex-taxi-stq-agent
    ln -sf $STQ_AGENT_DEB_PATH/yandex-taxi-stq-agent.upstream_list /etc/nginx/conf.d/

    ln -sf $STQ_AGENT_PATH/taxi-stq-agent-stats.py /usr/bin/

    echo "using binary: $STQ_AGENT_BINARY_PATH"
    ln -sf $STQ_AGENT_BINARY_PATH /usr/bin/
fi

mkdir -p /var/lib/yandex/taxi-stq-agent/
mkdir -p /var/log/yandex/taxi-stq-agent/
ln -sf /taxi/logs/application-taxi-stq-agent.log /var/log/yandex/taxi-stq-agent/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-stq-agent \
    --fix-userver-client-timeout /etc/yandex/taxi/stq-agent/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-stq-agent \
        --config /etc/yandex/taxi/stq-agent/config.yaml \
        --init-log /var/log/yandex/taxi-stq-agent/server.log
