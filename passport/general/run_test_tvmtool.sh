#!/bin/bash

mkdir -p ./.tvmtool/tests-tvm-cache

#openssl rand -hex 16 > ./.tvmtool/token
#export TVMTOOL_LOCAL_AUTHTOKEN="$(cat ./.tvmtool/token)"
export TVMTOOL_LOCAL_AUTHTOKEN='tvmtool-development-access-token'

set -ex
echo "$(date) - starting tvmtool"

node ./tools/load-test-tvm-config.js

tvmtool --cache-dir ./.tvmtool/tests-tvm-cache --port 11111 --config ./.tvmtool/config.json
