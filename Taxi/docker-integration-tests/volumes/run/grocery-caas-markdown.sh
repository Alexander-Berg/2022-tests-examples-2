#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_CAAS_MARKDOWN_PATH=$USERVICES_PATH/build-integration/services/grocery-caas-markdown
GROCERY_CAAS_MARKDOWN_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-caas-markdown
GROCERY_CAAS_MARKDOWN_DEB_PATH=$USERVICES_PATH/services/grocery-caas-markdown/debian

GROCERY_CAAS_MARKDOWN_BINARY_PATH=
if [ -f "$GROCERY_CAAS_MARKDOWN_PATH/yandex-taxi-grocery-caas-markdown" ]; then
  GROCERY_CAAS_MARKDOWN_BINARY_PATH="$GROCERY_CAAS_MARKDOWN_PATH/yandex-taxi-grocery-caas-markdown"
elif [ -f "$GROCERY_CAAS_MARKDOWN_ARCADIA_PATH/yandex-taxi-grocery-caas-markdown" ]; then
  GROCERY_CAAS_MARKDOWN_BINARY_PATH="$GROCERY_CAAS_MARKDOWN_ARCADIA_PATH/yandex-taxi-grocery-caas-markdown"
fi

if [ -f "$GROCERY_CAAS_MARKDOWN_BINARY_PATH" ]; then
    echo "grocery-caas-markdown update package"
    mkdir -p /etc/yandex/taxi/grocery-caas-markdown/
    rm -rf /etc/yandex/taxi/grocery-caas-markdown/*

    ln -s $GROCERY_CAAS_MARKDOWN_PATH/configs/* /etc/yandex/taxi/grocery-caas-markdown/
    cp $GROCERY_CAAS_MARKDOWN_PATH/config.yaml /etc/yandex/taxi/grocery-caas-markdown/
    ln -s $GROCERY_CAAS_MARKDOWN_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-caas-markdown/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-caas-markdown/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-caas-markdown/config_vars.yaml

    ln -sf $GROCERY_CAAS_MARKDOWN_DEB_PATH/yandex-taxi-grocery-caas-markdown.nginx /etc/nginx/sites-available/yandex-taxi-grocery-caas-markdown
    ln -sf $GROCERY_CAAS_MARKDOWN_DEB_PATH/yandex-taxi-grocery-caas-markdown.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_CAAS_MARKDOWN_PATH/taxi-grocery-caas-markdown-stats.py /usr/bin/
    echo "using binary: $GROCERY_CAAS_MARKDOWN_BINARY_PATH"
    ln -sf $GROCERY_CAAS_MARKDOWN_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-caas-markdown/
mkdir -p /var/lib/yandex/taxi-grocery-caas-markdown/
mkdir -p /var/lib/yandex/taxi-grocery-caas-markdown/private/
mkdir -p /var/cache/yandex/taxi-grocery-caas-markdown/
ln -sf /taxi/logs/application-taxi-grocery-caas-markdown.log /var/log/yandex/taxi-grocery-caas-markdown/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-caas-markdown \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-caas-markdown/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-caas-markdown \
        --config /etc/yandex/taxi/grocery-caas-markdown/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-caas-markdown/server.log
