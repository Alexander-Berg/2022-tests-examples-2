#!/bin/sh

set -e

ya make
./sandbox run SetSandboxResourceAttribute --input "`cat test_data_set_attribute.json`" --local
echo
