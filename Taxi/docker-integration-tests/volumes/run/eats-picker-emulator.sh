#!/usr/bin/env bash
set -e
if [ -f /taxi/taximeter-emulator/debian/control ]; then
    rm -rf /usr/lib/yandex/taximeter-emulator/*
    ln -s /taxi/taximeter-emulator/run.py /usr/lib/yandex/taximeter-emulator
    ln -s /taxi/taximeter-emulator/taximeter_emulator /usr/lib/yandex/taximeter-emulator
fi

/taxi/tools/run.py \
    --syslog \
    --wait \
        http://eats-picker-orders.eda.yandex.net/ping \
    --run \
        /usr/lib/yandex/taxi-py3-2/bin/python3 /usr/lib/yandex/taximeter-emulator/run.py --port 80 --host 0.0.0.0
