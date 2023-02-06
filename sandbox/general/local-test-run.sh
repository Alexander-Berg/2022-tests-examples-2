#!/bin/sh -E

RDBMS_KIND=psql \
RESULT_FILE=geodata6.bin \
CURR_DIR_PATH=. \
RAM_DRIVE_PATH=. \
bash ../common/geodata6-balancer-stable.sh
