#!FILTER ./rthub_test --config-module robot.rthub.cmpy.rthub_test.config --append-scenario
#!/usr/bin/env bash

#!+INCLUDES

set -uxe

_scenario () {
    MAIN = !hostlist:MAIN res=mem:0,cpu:0
    MAIN_CLUSTERED = !hostlist:MAIN 000..031
}

#!-INCLUDES

# YT env params
export YT_POOL=${YT_POOL:-kwyt-test}
export YT_LOG_LEVEL=DEBUG

export CMPY_DIR=${CMPY_DIR:-cmpy/rthub_test_cmpy}

${CMPY_DIR}/rthub_test  --config-module "robot.rthub.cmpy.rthub_test.config" "$@"
