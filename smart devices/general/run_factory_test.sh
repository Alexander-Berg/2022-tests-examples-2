#!/bin/sh

set -e  # exit on uncaught errors

cd /system/vendor/quasar

export LD_LIBRARY_PATH=/system/vendor/quasar/libs

nohup /system/workdir/bin/factory_test &> /data/factory_test.log &

sleep 1
