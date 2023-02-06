#!/bin/bash

set -e

ya make
./passport-autotests run --enable-taskbox --type=PASSPORT_AUTOTESTS --owner PASSPORT "`cat test_data.json`"
