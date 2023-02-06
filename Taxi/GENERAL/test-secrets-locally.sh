#!/usr/bin/env bash

BASE_DIR=$(dirname $0)
NODE_ENV=development ${BASE_DIR}/files/prestart_scripts/52_handle_secrets.js
cat .dev/.env
