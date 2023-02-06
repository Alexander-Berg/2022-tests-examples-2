#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
CARDSTORAGE_PATH=$USERVICES_PATH/build-integration/services/cardstorage
CARDSTORAGE_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/cardstorage
CARDSTORAGE_DEB_PATH=$USERVICES_PATH/services/cardstorage/debian

CARDSTORAGE_BINARY_PATH=
if [ -f "$CARDSTORAGE_PATH/yandex-taxi-cardstorage" ]; then
  CARDSTORAGE_BINARY_PATH="$CARDSTORAGE_PATH/yandex-taxi-cardstorage"
elif [ -f "$CARDSTORAGE_ARCADIA_PATH/yandex-taxi-cardstorage" ]; then
  CARDSTORAGE_BINARY_PATH="$CARDSTORAGE_ARCADIA_PATH/yandex-taxi-cardstorage"
fi

if [ -f "$CARDSTORAGE_BINARY_PATH" ]; then
    echo "cardstorage update package"
    mkdir -p /etc/yandex/taxi/cardstorage/
    rm -rf /etc/yandex/taxi/cardstorage/*
    ln -s $CARDSTORAGE_PATH/configs/* /etc/yandex/taxi/cardstorage/
    cp $CARDSTORAGE_PATH/config.yaml /etc/yandex/taxi/cardstorage/
    ln -s $CARDSTORAGE_PATH/taxi_config_fallback.json /etc/yandex/taxi/cardstorage/
    ln -s $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/cardstorage/
    ln -s config_vars.production.yaml /etc/yandex/taxi/cardstorage/config_vars.yaml

    ln -sf $CARDSTORAGE_DEB_PATH/yandex-taxi-cardstorage.nginx /etc/nginx/sites-available/yandex-taxi-cardstorage
    ln -sf $CARDSTORAGE_DEB_PATH/yandex-taxi-cardstorage.upstream_list /etc/nginx/conf.d/

    ln -sf $CARDSTORAGE_PATH/taxi-cardstorage-stats.py /usr/bin/

    echo "using binary: $CARDSTORAGE_BINARY_PATH"
    ln -sf $CARDSTORAGE_BINARY_PATH /usr/bin/
fi

# TODO: Remove when mockserver will support https connections
sed s/https/http/g -i /etc/yandex/taxi/cardstorage/config_vars.yaml
mkdir -p /var/lib/yandex/taxi-cardstorage/
mkdir -p /var/log/yandex/taxi-cardstorage/
ln -sf /taxi/logs/application-taxi-cardstorage.log /var/log/yandex/taxi-cardstorage/server.log

/taxi/tools/run.py \
    --nginx yandex-taxi-cardstorage \
    --fix-userver-client-timeout /etc/yandex/taxi/cardstorage/config.yaml \
    --wait mongo.taxi.yandex:27017 \
    --run /usr/bin/yandex-taxi-cardstorage \
        --config /etc/yandex/taxi/cardstorage/config.yaml \
        --init-log /var/log/yandex/taxi-cardstorage/server.log
