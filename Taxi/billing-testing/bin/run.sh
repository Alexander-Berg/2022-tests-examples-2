#!/usr/bin/env bash

/taxi/tools/install_py3.sh

echo "exec /usr/lib/yandex/taxi-py3-2/bin/python /taxi/sibilla/sibilla/app.py ${@} /taxi/tests"
exec /usr/lib/yandex/taxi-py3-2/bin/python /taxi/sibilla/sibilla/app.py ${@} /taxi/tests
