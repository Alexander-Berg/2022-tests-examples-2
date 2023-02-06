#!/bin/bash

set +e

if [ -f "$TAXIDWH_TEST_RUNNER_OUT_PATH" ]
then
	echo test_kill >> "$TAXIDWH_TEST_RUNNER_OUT_PATH"
else
    echo start -1
	exit 1
fi

if [ -f "$TAXIDWH_TEST_RUNNER_PID_PATH" ]
then
    echo $$ > "$TAXIDWH_TEST_RUNNER_PID_PATH"
    {
      for i in $(seq 1000)
      do
        sleep 0.1
      done
    } 2> /dev/null
else
	exit 1
fi
