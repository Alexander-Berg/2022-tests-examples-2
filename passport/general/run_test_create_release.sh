#!/bin/sh

set -e

ya make
./startrek run CreateReleaseIssue --input "`cat test_data_create_release.json`" --local
echo
echo "Please close this startrek issue manually"
