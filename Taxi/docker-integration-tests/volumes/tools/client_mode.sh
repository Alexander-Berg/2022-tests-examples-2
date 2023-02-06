#!/bin/bash

set -e

/taxi/tools/replace_taxi_imports.sh
/taxi/tools/configure_client_mode.py
