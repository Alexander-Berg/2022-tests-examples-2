#!/usr/bin/env bash
set -e

USERVICES_PATH=/arcadia/taxi/uservices
PILORAMA_PATH=$USERVICES_PATH/build-integration/services/pilorama
PILORAMA_ARCADIA_PATH=$USERVICES_PATH/build-integration/taxi/uservices/services/pilorama
PILORAMA_DEB_PATH=$USERVICES_PATH/services/pilorama/debian

PILORAMA_BINARY_PATH=
if [ -f "$PILORAMA_PATH/yandex-taxi-pilorama" ]; then
  PILORAMA_BINARY_PATH="$PILORAMA_PATH/yandex-taxi-pilorama"
elif [ -f "$PILORAMA_ARCADIA_PATH/yandex-taxi-pilorama" ]; then
  PILORAMA_BINARY_PATH="$PILORAMA_ARCADIA_PATH/yandex-taxi-pilorama"
fi

if [ -f "$PILORAMA_BINARY_PATH" ]; then
    echo "pilorama update package"
    mkdir -p /etc/yandex/taxi/pilorama/
    rm -rf /etc/yandex/taxi/pilorama/* ||:
    mkdir -p /var/log/yandex/taxi-pilorama/
    mkdir -p /var/cache/taxi-pilorama/
    ln -sf $PILORAMA_PATH/configs/* /etc/yandex/taxi/pilorama/
    cp $PILORAMA_PATH/config.yaml /etc/yandex/taxi/pilorama/
    ln -sf $PILORAMA_PATH/taxi_config_fallback.json /etc/yandex/taxi/pilorama/
    ln -sf $USERVICES_PATH/scripts/templates/taxi_config_bootstrap.json /etc/yandex/taxi/pilorama/
    ln -sf config_vars.production.yaml /etc/yandex/taxi/pilorama/config_vars.yaml

    ln -sf $PILORAMA_DEB_PATH/yandex-taxi-pilorama.nginx /etc/nginx/sites-available/yandex-taxi-pilorama
    ln -sf $PILORAMA_DEB_PATH/yandex-taxi-pilorama.upstream_list /etc/nginx/conf.d/

    ln -sf $PILORAMA_PATH/taxi-pilorama-stats.py /usr/bin/

    echo "using binary: $PILORAMA_BINARY_PATH"
    ln -sf $PILORAMA_BINARY_PATH /usr/bin/
fi

# disabling internal pilorama log as useless
mkdir -p /var/lib/yandex/taxi-pilorama/
sed -i 's/file_path:.*\/pilorama.log/file_path: \/dev\/null/g' /etc/yandex/taxi/pilorama/config.yaml


/taxi/tools/run.py \
    --fix-userver-client-timeout /etc/yandex/taxi/pilorama/config.yaml \
    --run /usr/bin/yandex-taxi-pilorama \
        --config /etc/yandex/taxi/pilorama/config.yaml \
        --init-log /taxi/logs/application-taxi-pilorama.log
