#!/bin/bash

TEST_SERVER="taximeter-basis-minor-sas-01.taxi.tst.yandex.net"

scp $TEST_SERVER:/etc/yandex/taximeter-secdist/taximeter.json $(dirname $0)/../ && \
    sed -i -e 's/pgaas\.mail\.yandex\.net/pgaas-test.mail.yandex.net/g' $(dirname $0)/../taximeter.json

SSH_FORWARDINGS=""

# MongoDB, TVM
for port in 3017 3018 3019 3020 3021 3024 3026 3028 7020; do
    SSH_FORWARDINGS="$SSH_FORWARDINGS -L $port:localhost:$port"
done

# Redis (via haproxy)
for base_port in 20001 21001 25001 26001 30001 31001 32001 33001; do
    end_port=$((base_port + 15))

    # Surge Redis has only 8 masters
    if [ "$base_port" == 32001 ] || [ "$base_port" == 33001 ] ; then
        end_port=$((base_port + 7))
    fi

    for port in $(seq $base_port $end_port); do
        SSH_FORWARDINGS="$SSH_FORWARDINGS -L $port:localhost:$port"
    done
done

ssh -N $TEST_SERVER $SSH_FORWARDINGS
