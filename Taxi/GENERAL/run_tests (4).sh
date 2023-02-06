#!/bin/bash

EXIT_CODE=0
ARTIFACTS_DIR=$1
TEST_MODE=${2-normal}
TEST_FILE=$3

export SCREENSHOTS_DIR=./screenshots/
export SCREENSHOTS_AFTER=none

if ! test -z "$ARTIFACTS_DIR"; then
    mkdir -p $SCREENSHOTS_DIR
    # сохраняем скриншоты только для заданной директории артефактов
    # shellcheck disable=SC2034
    export SCREENSHOTS_AFTER=all
fi

pahtest --strict-mode-file --jobs 4 --headless pahtests/
EXIT_CODE=$?

if ! test -z $ARTIFACTS_DIR; then
  tar -czf $ARTIFACTS_DIR/front_test_screens.tar.gz $SCREENSHOTS_DIR
  chmod 666 $ARTIFACTS_DIR/front_test_screens.tar.gz
  ls -lh $ARTIFACTS_DIR
  rm -rf $SCREENSHOTS_DIR
fi
echo "Return code $EXIT_CODE"
exit $EXIT_CODE
