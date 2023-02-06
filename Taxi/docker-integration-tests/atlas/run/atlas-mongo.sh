#!/usr/bin/env bash
set -e

#/taxi/tools/run_as_user.sh mkdir -p /taxi/logs/

#/taxi/tools/run_as_user.sh /taxi/run/mongo-init.sh

COMMAND="mongod --ipv6 --port 27017 --bind_ip_all"

if [ -n "$MONGO_RAMDISK" ]
then
    COMMAND="$COMMAND --smallfiles --noprealloc --nojournal --dbpath /mnt/ram"
else
    mkdir -p /data/db
fi

 #/taxi/tools/run_as_user.sh 
 $COMMAND
