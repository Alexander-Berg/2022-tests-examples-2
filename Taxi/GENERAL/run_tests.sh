#!/bin/bash

set -e
set -v
cd /taxi/repo

yarn prettier --check .
yarn tsc -b
yarn jest --testResultsProcessor=jest-teamcity-reporter
yarn stylelint '**/*.css'
yarn eslint --quiet .
