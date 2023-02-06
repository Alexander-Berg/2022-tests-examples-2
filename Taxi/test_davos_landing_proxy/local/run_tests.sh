#!/usr/bin/env bash
BE_PY3_SERVICE="$(pwd)/services/davos-landing-proxy"

docker build -t config-nginx-davos-landing-proxy-tests:latest "$BE_PY3_SERVICE/test_davos_landing_proxy/local/docker"

NGINX_CONFIGS="$BE_PY3_SERVICE/nginx/conf.d"
NGINX_SITES_CONFIGS="$BE_PY3_SERVICE/nginx/sites-enabled"
TESTS="$BE_PY3_SERVICE/test_davos_landing_proxy/local"

docker run --rm -it \
    -v $NGINX_SITES_CONFIGS:/etc/nginx/sites-enabled:ro \
    -v $TESTS:/tests:ro \
    -v $TESTS/.cache:/tests/.cache:rw \
    --add-host lpc-internal.yandex.net:127.0.0.1 \
    --add-host webauth.yandex-team.ru:127.0.0.1 \
    --add-host frontend-vezet.taxi.yandex.net:127.0.0.1 \
    --dns 127.0.0.1 \
    --dns 192.168.65.5 \
    config-nginx-davos-landing-proxy-tests:latest
