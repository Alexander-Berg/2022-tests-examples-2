#!/bin/sh

set -e

ya make
./startrek run TransitIssues --input "`cat test_data_transit.json`" --local
