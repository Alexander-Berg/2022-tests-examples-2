#!/bin/bash
set -e
docker build --build-arg UNPAB_OAUTH=${UNPAB_OAUTH} -t qatestserver .
