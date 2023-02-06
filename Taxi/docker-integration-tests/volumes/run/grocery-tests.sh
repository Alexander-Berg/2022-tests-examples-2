#!/usr/bin/env bash
set -e

/usr/lib/yandex/taxi-py3-2/bin/py.test \
    ${PYTEST_ARGS_INTEGRATION:--vv -x} grocery-tests/tests
