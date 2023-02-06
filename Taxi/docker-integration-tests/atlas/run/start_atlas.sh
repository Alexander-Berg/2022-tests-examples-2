#!/bin/bash

export ENV_PATH=/usr/lib/yandex/taxi-atlas-backend-deps/bin
. $ENV_PATH/activate && \
exec gunicorn \
    --reload \
    --log-level debug \
    --pythonpath='/usr/lib/yandex/taxi-atlas-backend-router' \
    atlas.app:app \
    -c atlas_gunicorn.conf

