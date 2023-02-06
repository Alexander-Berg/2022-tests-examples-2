#!/usr/bin/env bash

chmod 777 "$CCACHE_DIR"
chmod 777 "$CORES_DIR"
/taxi/tools/run_as_user.sh ccache -M ${CCACHE_SIZE:-40G}
export CMAKE_OPTS=${CMAKE_OPTS:--DUSE_CCACHE=1}
/taxi/tools/run_as_user.sh make
