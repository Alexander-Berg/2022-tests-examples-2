#!/bin/bash

PATH=$PATH:/usr/sbin:/sbin
START_STOP_DAEMON=$(which start-stop-daemon 2>/dev/null)

die() {
    echo "$@" >&2
    exit 1
}

if [ "x$TESTSUITE_DEBUG" != "x" ]; then
    set -x
fi

if [ "x$TAXI_BUILD_DIR" = "x" ]; then
    die "TAXI_BUILD_DIR must be set"
fi

if [ "x$TAXI_TESTSUITE_DIR" = "x" ]; then
    die "TAXI_TESTSUITE_DIR must be set"
fi

TESTSUITE_TMPDIR=$TAXI_BUILD_DIR/testsuite/tmp
TESTSUITE_BUILD_DIR=$TAXI_BUILD_DIR/testsuite

ulimit_files() {
    local current=$(ulimit -n)
    local limit

    if [ "$current" != "unlimited" -a "$current" -lt "16384" ]; then
        for limit in 4096 8192 16384; do
            if ! ulimit -n $limit 2> /dev/null; then
                break
            fi
        done
    fi
    echo "ulimit -n is set to $(ulimit -n)"
}

stop_daemon() {
    local binary=$1
    local pidfile=$2

    if [ "x$START_STOP_DAEMON" != "x" ]; then
        $START_STOP_DAEMON --stop --retry TERM/5/KILL/3 \
                           -p $pidfile $binary 2> /dev/null >&2
    else
        # MacOS X workaround
        for i in `seq 10`; do
            if [ -f "$pidfile" ]; then
                if [ $i == "1" ]; then
                    kill -TERM $(cat "$pidfile")
                else
                    kill -TERM $(cat "$pidfile") 2> /dev/null >&2
                fi
            else
                break
            fi
            sleep 0.1
        done

        if [ -f "$pidfile" ]; then
            kill -KILL $(cat "$pidfile") 2> /dev/null >&2
            rm -f "$pidfile"
        fi
    fi
}

script_main() {
    case "$1" in
        start)
            start
            ;;
        stop)
            stop || true
            ;;
        *)
            echo "Usage: $0 <start|stop>"
    esac
}

# Returns an absolute path to a file in /tmp subdirectory
# The parent directory is created for the returned path
get_pidfile() {
    local service="$(basename $0)"
    local path=/tmp/taxi-testsuite-$USER/run/$service/${WORKER_SUFFIX}/$1.pid
    mkdir -p "$(dirname "$path")"
    echo $path
}
