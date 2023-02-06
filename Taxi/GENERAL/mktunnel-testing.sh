#!/bin/bash

TEST_SERVER="selfemployed-iva-01.taxi.tst.yandex.net"

SSH_FORWARDINGS=""

# MongoDB
for port in 3017 3018 3019 3020 3021 3023 3024 3025; do
 SSH_FORWARDINGS="$SSH_FORWARDINGS -L $port:localhost:$port"
done

ssh -N $TEST_SERVER $SSH_FORWARDINGS
