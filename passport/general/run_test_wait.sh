#!/bin/sh

set -e

ya make
./conductor run WaitForConductorTicket --input "`cat test_data_wait.json`" --local
