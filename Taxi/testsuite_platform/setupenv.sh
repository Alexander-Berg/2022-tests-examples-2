#!/bin/sh

PYTHON=$(which python3.11 python3.10 python3.9 python3.8 python3.7 \
               python3 2> /dev/null | head -1)

if [ "x$PYTHON" = "x" ]; then
   exec >&2
   echo "FATAL: No python binary found, sorry"
   exit 1
fi

VENV_DIR=.venv

if [ ! -d "$VENV_DIR" ]; then
    virtualenv --python=$PYTHON "$VENV_DIR"
fi

$VENV_DIR/bin/pip install ../../uservices/submodules/testsuite[postgresql]
$VENV_DIR/bin/pip install -r requirements.txt
