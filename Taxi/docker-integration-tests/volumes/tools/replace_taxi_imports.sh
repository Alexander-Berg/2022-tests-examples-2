#!/usr/bin/env bash
set -e

PREFIX=/taxi/backend

if [ -f /taxi/backend/debian/changelog ]; then
    grep /usr/lib/yandex/taxi-import $PREFIX/debian/yandex-taxi-import.install | \
        while read src dst
        do
            dst=$(echo $dst | sed 's/-${PACKAGE_VERSION}//')
            rm -rf $dst/$(basename $src)
            ln -s $PREFIX/$src $dst/
        done

    rm -f /usr/lib/yandex/taxi-import/taxi_settings.py
    ln -s /taxi/backend/debian/settings.production.py \
        /usr/lib/yandex/taxi-import/taxi_settings.py
fi
