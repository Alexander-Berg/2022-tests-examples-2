#!/usr/bin/env bash
/taxi/loghandler/loghandler.py &
LOGHANDLER_PID=$!

cp /taxi/loghandler/logrotate.conf /etc/logrotate.conf
chmod 600 /etc/logrotate.conf
chown root /etc/logrotate.conf

uid=$(stat -c %u /taxi/logs)
gid=$(stat -c %g /taxi/logs)

groupadd --non-unique --gid $gid local_group
useradd --create-home --no-user-group --non-unique --gid $gid \
        --uid $uid local_user

PERIOD=${LOGROTATE_RUN_PERIOD:-600}
N=0
while true; do
    if [ $N -ge $PERIOD ]; then
        logrotate --log=/taxi/logs/logrotate /etc/logrotate.conf
        N=0
    fi

    if [ -z "$(ps -o pid= $LOGHANDLER_PID)" ]; then
        echo "Loghandler died!" >&2
        exit 1
    fi

    N=$(( N + 1 ))
    sleep 1
done
