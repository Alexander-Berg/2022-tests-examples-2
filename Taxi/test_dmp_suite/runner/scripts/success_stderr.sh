#!/bin/bash

if [ -f "$TAXIDWH_TEST_RUNNER_OUT_PATH" ]
then
	echo success_stderr >> "$TAXIDWH_TEST_RUNNER_OUT_PATH"
else
	exit 1
fi

(>&2 echo "Write to stderr and exit success")
