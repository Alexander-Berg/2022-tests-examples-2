#!/bin/sh

make -C function_tests init
sleep 3m
cd function_tests
PYTHONWARNINGS="ignore:Unverified HTTPS request" N=1 FEATURES='function_tests_stable' make t
res=$?
allure generate --clean
mv allure-report stable-allure-report
cd -
exit $res
