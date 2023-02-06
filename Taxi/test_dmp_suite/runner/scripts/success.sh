#!/bin/bash

if [ -f "$TAXIDWH_TEST_RUNNER_OUT_PATH" ]
then
    if [ $# -eq 0 ]; then
	    echo success >> "$TAXIDWH_TEST_RUNNER_OUT_PATH"
	else
	    echo success $#>> "$TAXIDWH_TEST_RUNNER_OUT_PATH"
    fi
else
	exit 1
fi
