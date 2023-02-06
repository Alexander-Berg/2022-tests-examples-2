#!/bin/bash

EXIT_CODE=0
ARTIFACTS_DIR=$1
TEST_MODE=${2-normal}
TEST_FILE=$3

export SCREENSHOTS_DIR=./screenshots/
export SCREENSHOTS_AFTER=none

list_tests() {
    find tests -type f -name '*.yml' | sort
}

list_dir_tests() {
    find tests -type d | sort
}

if ! test -z "$ARTIFACTS_DIR"; then
    mkdir -p $SCREENSHOTS_DIR
    # сохраняем скриншоты только для заданной директории артефактов
    # shellcheck disable=SC2034
    export SCREENSHOTS_AFTER=all
fi

if test -z $TEST_FILE; then

    TESTS=`list_tests`
    COUNT=`echo $TESTS| wc -w`

    NO=1
    ERRORS=0

    if test $TEST_MODE = 'parallel'; then
        pahtest --strict-mode-file --jobs 8 --headless tests/
        EXIT_CODE=$?
    elif test $TEST_MODE = 'parallel-dir'; then
        list_dir_tests | parallel -j 8 bash scripts/ci/run_one.sh
        EXIT_CODE=$?
    else
        for test_file in $TESTS; do
            echo "+ [$NO из $COUNT ] pahtest $test_file"
            NO=$(($NO + 1))
            pahtest $test_file
            if test $? -eq 0; then
                echo "PASSED ($ERRORS ошибок)"
            else
                ERRORS=$(($ERRORS + 1))
                EXIT_CODE=1
                echo "FAILED ($ERRORS ошибок)"
            fi
        done
    fi
else
    bash scripts/ci/run_one.sh $TEST_FILE
    EXIT_CODE=$?
fi

if ! test -z $ARTIFACTS_DIR; then
  tar -czf $ARTIFACTS_DIR/front_test_screens.tar.gz $SCREENSHOTS_DIR
  chmod 666 $ARTIFACTS_DIR/front_test_screens.tar.gz
  ls -lh $ARTIFACTS_DIR
  rm -rf $SCREENSHOTS_DIR
fi
echo "Return code $EXIT_CODE"
exit $EXIT_CODE
