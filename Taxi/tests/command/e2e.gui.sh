#!/bin/sh
set -e

ROOT_DIR=$(node -e 'console.log(require("app-root-path").path)')

export PROJECT_NAME=website

$ROOT_DIR/tools/command/e2e/run/e2e.gui.sh
