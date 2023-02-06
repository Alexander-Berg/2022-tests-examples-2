#!/bin/sh

make -C function_tests init
sleep 2m
cd function_tests
PYTHONWARNINGS="ignore:Unverified HTTPS request" N=1 FEATURES='function_test_yaml' RETRY_COUNT=5 make t
res=$?
allure generate --clean
mv allure-report kote-allure-report
cd -
exit $res
