#!/usr/bin/env bash
set -e
SERVICES=$(scripts/get_services.py)
PLATFORM=xenial docker-compose pull --parallel --ignore-pull-failures $SERVICES 2>&1 | grep -i error

make docker-cleanup >/dev/null 2>&1
