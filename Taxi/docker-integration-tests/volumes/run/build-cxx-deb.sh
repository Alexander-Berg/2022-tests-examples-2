#!/usr/bin/env bash

chmod 777 "$CCACHE_DIR"
NPROCS=${NPROCS:-$(nproc)}
export DUPLOAD_DISABLE=1  # todo(seanchaidh): delete
export DEB_BUILD_OPTIONS="parallel=$NPROCS $DEB_BUILD_OPTIONS"
export DEBUILD_COMMAND="debuild --preserve-envvar CC \
                                --preserve-envvar CXX \
                                --preserve-envvar CCACHE_DIR
                                --preserve-envvar NPROCS \
                                --preserve-envvar CLICOLOR_FORCE \
                                --no-tgz-check --no-lintian -sa -b"

/taxi/tools/run_as_user.sh ccache -M ${CCACHE_SIZE:-40G}
/taxi/tools/run_as_user.sh python3 /usr/lib/yandex/taxi-buildagent/run_build.py
