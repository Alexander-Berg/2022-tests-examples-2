#!FILTER sed -e 's|\$(\(\s*[^(<]\)|$(trap killme ERR; \1|g'
#!FILTER sed -e '/^#NOT-IN-TEST/{N;s/$/\n[ \${TESTING_FLAG:-0\} -ne 0 ] \&\& exit 0/}'
#!FILTER if test ${TESTING_FLAG:-0} -ne 0 ; then sed -e 's/%SHARDED%/SINGLE/'; else sed -e 's/%SHARDED%/SHARDED/'; fi
#!/usr/bin/env bash

#!+INCLUDES

source common/utils.sh

source common/enable_debug.sh

source common/test_variables.sh

source common/common_variables.sh

source common/state.sh

source common/sync.sh

source common/yt.sh

_scenario () {
    source scenario.sh
}

source ack_converter/graph.sh

source delta_converter/graph.sh

source merger/graph.sh

source stats_pusher/graph.sh

source garbage/graph.sh

# This is a test graph to simulate fail (and fail alerts)
source test_fail/graph.sh

#!FILTER ${KWYT_DIR}/bin/cm --config-module robot.kwyt.cm.configuration.production --append-scenario

source common/footer.sh

#!-INCLUDES
