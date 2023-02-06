#!/bin/sh

make -C function_tests init
cd function_tests
PYTHONWARNINGS="ignore:Unverified HTTPS request" N=1 D='tests/schema' make t
res=$?
allure generate --clean
mv allure-report schema-allure-report
cd -
exit $res
