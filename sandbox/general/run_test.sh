#!/bin/bash

set -e

ya make
cat ./test_data.json | ./build_tvmauth_pypi run --enable-taskbox --type BUILD_TVM_AUTH_PYPI --owner PASSPORT -
