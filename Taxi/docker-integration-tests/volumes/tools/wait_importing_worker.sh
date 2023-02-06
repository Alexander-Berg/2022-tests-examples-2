#!/usr/bin/env bash

if [ ! "$1" ]
then
    exit 1
fi
echo "param is "$1
taxi-${1}-stats.py 2>/dev/null | fgrep full-updates-count | egrep -v " 0$"
