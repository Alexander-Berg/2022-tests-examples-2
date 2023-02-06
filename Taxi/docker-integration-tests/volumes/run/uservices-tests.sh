#!/usr/bin/env bash

chmod 777 "$CORES_DIR"
echo "$CORES_DIR/core-%e-%s-%u-%g-%p-%t" > /proc/sys/kernel/core_pattern
/taxi/tools/run_as_user.sh bash -c 'ulimit -c unlimited; export TESTSUITE_DEBUG=1; make test'
