#!/bin/sh

if [ ! -d .venv ]; then
    virtualenv --python=python3 .venv
fi

. .venv/bin/activate
pip install -r requirements.txt
