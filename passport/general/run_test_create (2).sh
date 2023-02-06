#!/bin/sh

set -e

ya make
./startrek run CreateIssue --input "`cat test_data_create.json`" --local
echo
echo "Please close this startrek issue manually"
