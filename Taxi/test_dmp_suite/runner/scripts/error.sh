#!/bin/bash

if [ -f "$TAXIDWH_TEST_RUNNER_OUT_PATH" ]
then
	echo error >> "$TAXIDWH_TEST_RUNNER_OUT_PATH"
else
	exit 1
fi

exit 1
