#!/bin/sh

set -e

ya make
./changelog run Changelog --input "`cat test_data.json`" --test
