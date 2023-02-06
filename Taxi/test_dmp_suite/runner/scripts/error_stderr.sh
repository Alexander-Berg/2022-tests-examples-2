#!/bin/bash

if [ -f "$TAXIDWH_TEST_RUNNER_OUT_PATH" ]
then
	echo error_stderr >> "$TAXIDWH_TEST_RUNNER_OUT_PATH"
else
	exit 1
fi

(>&2 echo "Write to stderr and exit with fail")

exit 1
