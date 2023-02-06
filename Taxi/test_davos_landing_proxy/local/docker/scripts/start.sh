#!/usr/bin/env bash
set -e

DOMAINS=$(grep -R server_name /etc/nginx/sites-enabled/*.production | awk '{print $3}' | sed 's/;//g' | grep -vE "(\~|\*)" | awk -F'.' '{print $F}' | sort | uniq)

for d in $DOMAINS; do
    echo "address=/$d/127.0.0.1" >> /etc/dnsmasq.conf
done

dnsmasq

nginx -t
nginx

py.test-3 /tests/*.py
