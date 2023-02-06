#!/usr/bin/env bash
set -e

REPO_DIR=/taxi/backend-py3
TRANSACTIONS_DIR=$REPO_DIR/services/transactions
TRANSACTIONS_GENERATED_DIR=${TRANSACTIONS_DIR}/transactions/generated/
SETTINGS_PROD=$TRANSACTIONS_GENERATED_DIR/service/settings/settings.production
if [ -d "$TRANSACTIONS_GENERATED_DIR" ]; then
    echo "transactions update package"
    mkdir -p /var/cache/yandex/taxi/configs/
    mkdir -p /etc/yandex/taxi-transactions-web/
    chown -R www-data:www-data /var/cache/yandex/taxi/configs
    mkdir -p /usr/lib/yandex/taxi-transactions-web/ \
           /etc/yandex/taxi-transactions-web/
    rm -rf /usr/lib/yandex/taxi-transactions-web/* \
           /etc/yandex/taxi-transactions-web/*
    mkdir -p /var/cache/yandex/taxi/transactions/files/

    ln -s $REPO_DIR/taxi /usr/lib/yandex/taxi-transactions-web/taxi
    if [ -d $REPO_DIR/generated ]; then
      ln -s $REPO_DIR/generated /usr/lib/yandex/taxi-transactions-web/generated
    fi
    for LIB_DIR in $REPO_DIR/libraries/*; do
        DIR_NAME=$(basename $LIB_DIR)
        PACKAGE_NAME=${DIR_NAME//-/_}
        PACKAGE_DIR=$LIB_DIR/$PACKAGE_NAME
        if [ -d $PACKAGE_DIR ]; then
            ln -s $PACKAGE_DIR /usr/lib/yandex/taxi-transactions-web/$PACKAGE_NAME
        fi
    done
    ln -s $TRANSACTIONS_DIR/transactions \
          /usr/lib/yandex/taxi-transactions-web/transactions
    ln -sf $TRANSACTIONS_DIR/debian/yandex-taxi-transactions-web.nginx \
           /etc/nginx/sites-available/yandex-taxi-transactions-web
    ln -sf $TRANSACTIONS_DIR/debian/yandex-taxi-transactions-web.upstream_list.production \
           /etc/nginx/conf.d/99-yandex-taxi-transactions-web-upstream
    if [ -f $SETTINGS_PROD ]; then
        ln -s $SETTINGS_PROD /etc/yandex/taxi-transactions-web/settings.yaml
    fi
fi

for num in {01..16}; do
    ln -sf yandex_taxi_transactions_web_00.sock /tmp/yandex_taxi_transactions_web_${num}.sock
done

/taxi/tools/run.py \
    --syslog \
    --wait \
      mongo.taxi.yandex:27017 \
      http://configs.taxi.yandex.net/ping \
    --nginx yandex-taxi-transactions-web \
    --run su www-data -s /bin/bash -c "/usr/lib/yandex/taxi-py3-2/bin/python3.7 \
          -m transactions.generated.web.run_web --path=/tmp/yandex_taxi_transactions_web_00.sock \
          --instance=00"
