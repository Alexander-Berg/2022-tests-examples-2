#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
GROCERY_TAGS_PATH=$USERVICES_PATH/build-integration/services/grocery-tags
GROCERY_TAGS_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/grocery-tags
GROCERY_TAGS_DEB_PATH=$USERVICES_PATH/services/grocery-tags/debian

GROCERY_TAGS_BINARY_PATH=
if [ -f "$GROCERY_TAGS_PATH/yandex-taxi-grocery-tags" ]; then
  GROCERY_TAGS_BINARY_PATH="$GROCERY_TAGS_PATH/yandex-taxi-grocery-tags"
elif [ -f "$GROCERY_TAGS_ARCADIA_PATH/yandex-taxi-grocery-tags" ]; then
  GROCERY_TAGS_BINARY_PATH="$GROCERY_TAGS_ARCADIA_PATH/yandex-taxi-grocery-tags"
fi

if [ -f "$GROCERY_TAGS_BINARY_PATH" ]; then
    echo "grocery-tags update package"
    mkdir -p /etc/yandex/taxi/grocery-tags/
    rm -rf /etc/yandex/taxi/grocery-tags/*

    ln -s $GROCERY_TAGS_PATH/configs/* /etc/yandex/taxi/grocery-tags/
    cp $GROCERY_TAGS_PATH/config.yaml /etc/yandex/taxi/grocery-tags/
    ln -s $GROCERY_TAGS_PATH/taxi_config_fallback.json /etc/yandex/taxi/grocery-tags/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/grocery-tags/
    ln -s config_vars.production.yaml /etc/yandex/taxi/grocery-tags/config_vars.yaml

    ln -sf $GROCERY_TAGS_DEB_PATH/yandex-taxi-grocery-tags.nginx /etc/nginx/sites-available/yandex-taxi-grocery-tags
    ln -sf $GROCERY_TAGS_DEB_PATH/yandex-taxi-grocery-tags.upstream_list /etc/nginx/conf.d/

    ln -sf $GROCERY_TAGS_PATH/taxi-grocery-tags-stats.py /usr/bin/
    echo "using binary: $GROCERY_TAGS_BINARY_PATH"
    ln -sf $GROCERY_TAGS_BINARY_PATH /usr/bin/
fi

mkdir -p /var/log/yandex/taxi-grocery-tags/
mkdir -p /var/lib/yandex/taxi-grocery-tags/
mkdir -p /var/lib/yandex/taxi-grocery-tags/private/
mkdir -p /var/cache/yandex/taxi-grocery-tags/
ln -sf /taxi/logs/application-taxi-grocery-tags.log /var/log/yandex/taxi-grocery-tags/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-grocery-tags \
    --fix-userver-client-timeout /etc/yandex/taxi/grocery-tags/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-grocery-tags \
        --config /etc/yandex/taxi/grocery-tags/config.yaml \
        --init-log /var/log/yandex/taxi-grocery-tags/server.log
