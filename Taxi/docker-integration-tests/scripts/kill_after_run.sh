#!/bin/bash

"$@" 2>&1
RESULT=$?
docker-compose kill 2>&1 ||:
exit $RESULT
