#!/bin/bash

#
# Usage:
#     Session 1 - run test and make Worker stop at main():
#         ya make -tA --test-param GDB:WorkerMain=1 --test-debug --test-log-level=debug
#     Session 2 - wait for worker to start and attach:
#         ./gdb_attach_worker.sh
#

SELF_PATH=$( cd $( dirname ${BASH_SOURCE[0]}) && pwd )

PID=""

while [ -z $PID ]; do
    PID=$(ps xw -u $(whoami) | grep 'build_root[^ ]*/worker --config' | tr -s ' ' | awk '{print $1}')
    sleep 1
done

DATA_PATH=$(ps www -p $PID | egrep -o 'data-dir [^ ]*' | cut -f2 -d ' ')
LOGS_DIR=$(dirname $(find $DATA_PATH -iname worker.err | xargs ls -1t | head -1))
tail -n20 -F $LOGS_DIR/worker.err $LOGS_DIR/worker.out $DATA_PATH/debug.log &

ya tool gdb /proc/$PID/exe $PID -iex 'set print thread-events off' -ex 'b YaDebuggerWait' -ex 'continue' -ex 'set *stop = true'
