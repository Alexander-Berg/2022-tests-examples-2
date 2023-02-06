#!/bin/sh

make -C function_tests init
sleep 2m
cd function_tests
PYTHONWARNINGS="ignore:Unverified HTTPS request" N=1 FEATURES='api_search_v2' make t
res=$?
allure generate --clean
mv allure-report api-search-allure-report
cd -
exit $res
