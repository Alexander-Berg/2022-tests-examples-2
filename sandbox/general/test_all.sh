#!/usr/bin/env bash
set -xe
ya make -A
python2 __init__.py tests/data/test1.txt
python3 __init__.py tests/data/test1.txt
python2 __init__.py tests/data/test2.txt -f
python3 __init__.py tests/data/test2.txt -f

