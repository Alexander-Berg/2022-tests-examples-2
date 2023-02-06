#!/bin/sh
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd  "$SCRIPT_DIR"/../../../tests/temp/dist
(kill-port 8000 && hermione gui --set webview) &
cd $SCRIPT_DIR

echo "Opening tests report on port 8000"

