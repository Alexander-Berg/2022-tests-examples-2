#!/usr/bin/env bash
set -e

nginx -t
nginx

py.test-3 /tests/*.py
