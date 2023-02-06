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
    PID=$(ps xw -u $(whoami) | fgrep -v test_tool | grep 'build_root[^ ]*rtyserver_test' | tr -s ' ' | awk '{print $1}' | sort -n | tail -n1 | xargs)
    sleep 1
done

DATA_PATH=$(ps www -p $PID | egrep -o ' -r [^ ]*' | cut -f3 -d ' ')
LOGS_DIR=$(dirname $(find $DATA_PATH/.. -iname rtyserver_test.err | xargs ls -1t | head -1))

function cleanup {
    trap - INT TERM EXIT
    echo "Ctrl-C received, terminating..."
    kill -s TERM 0
}

trap cleanup INT TERM EXIT # this stops tail at exit
tail -n20 -F $LOGS_DIR/rtyserver_test.err $LOGS_DIR/rtyserver_test.out $LOGS_DIR/run.log &

ya tool gdb /proc/$PID/exe $PID -iex 'set print thread-events off' -ex 'b YaDebuggerWait' -ex 'continue' -ex 'set *stop = true'
