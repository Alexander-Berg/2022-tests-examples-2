#!/bin/bash

# "print_tests" returns relative paths to all the tests
TESTS=$(make -s -C ../.. print_tests)

echo "-----------------------------------------------------------------";
echo "Starting tests on $(nproc --all) processors";
echo "Tests found: ${TESTS}";
echo "-----------------------------------------------------------------";

make -f run-tests.mk TEST_LIST=$TESTS

echo "Done running tests!"

