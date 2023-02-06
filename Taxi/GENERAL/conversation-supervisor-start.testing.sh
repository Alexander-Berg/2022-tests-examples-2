#!/bin/bash

/conversation/bin/conversation-start.sh --environment=testing --httpport=8080 --logdir=/var/log/yandex/conversation --debug='-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:8000' --cpu-count=2
