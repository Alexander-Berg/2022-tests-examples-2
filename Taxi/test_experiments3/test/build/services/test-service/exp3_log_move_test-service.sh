#!/bin/bash

set -ex

ls -lahR /var/log/yandex/taxi-test-service

mkdir -p /var/log/yandex/taxi-test-service/exp3
chmod 0755 /var/log/yandex/taxi-test-service/exp3
chown -R www-data:www-data /var/log/yandex/taxi-test-service/exp3
old_files=$(find /var/log/yandex/taxi-test-service -maxdepth 1 -name "exp3-matched.log*")

for old_file in $old_files; do
new_file=/var/log/yandex/taxi-test-service/exp3/$(basename $old_file)
    if [ -f $new_file ]; then
        echo "$new_file already exists" >&2
        rm $old_file
    else
        mv $old_file $new_file
    fi
done
