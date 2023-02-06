#!/usr/bin/env bash

if [ ! -f /tmp/started ]; then
    "$@" && touch /tmp/started
fi
