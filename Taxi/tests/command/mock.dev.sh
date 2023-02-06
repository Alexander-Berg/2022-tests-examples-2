#!/bin/sh
set -e

ROOT_DIR=$(node -e 'console.log(require("app-root-path").path)')

$ROOT_DIR/tools/command/e2e/run/mock.dev.sh
