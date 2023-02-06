#!/usr/bin/env python

import robot.jupiter.test.common as jupiter_integration
from robot.library.yuppie.modules.environment import Environment

from os.path import join as pj

CURRENT_STATE = "20170709-100351"


def process(lj, env):
    lj.get_yt().touch_table("{}/{}".format(env.mr_prefix, "operation_statistics/statistics_requests"))
    lj.set_testing_current_state({"spread_rthub": CURRENT_STATE})
    lj.get_cm().check_call_target("spread_rthub_async.finish", timeout=60 * 60)

    # Sort is required to make stable diff (original table is not sorted by HostStatus and Robots)
    lj.get_yt().sort(pj(env.mr_prefix, "spread_rthub_hosts_async", CURRENT_STATE, "hostdat.delta"),
                     "Host", "LastAccess", "ExportTime", "HostStatus")
    lj.get_yt().sort(pj(env.mr_prefix, "spread_export", CURRENT_STATE, "hostdat_full"),
                     "Host", "LastAccess", "ExportTime", "HostStatus")

    lj.dump_jupiter_table(env.table_dumps_dir, "spread_rthub_hosts_async", CURRENT_STATE, "hostdat.delta")

    for table in ["hostdat", "hostdat_full", "urldat", "urldat_full"]:
        lj.dump_jupiter_table(env.table_dumps_dir, "spread_export", CURRENT_STATE, table)


def test_spread(links):
    env = Environment(diff_test=True)
    with jupiter_integration.launch_local_jupiter(
        env,
        test_data="spread_rthub.tar",
        yatest_links=links,
    ) as local_jupiter:
        return jupiter_integration.call_jupiter(env.hang_test, process, local_jupiter, env)
