#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yatest.common as yatest
from os.path import join as pj

from library.python.testing.deprecated import setup_environment

from robot.library.yuppie.modules.environment import Environment
from robot.library.yuppie.modules.cm import Cm
from robot.library.yuppie.modules.yt_mod import LocalYtHolder


def test_sd():
    work_dir = yatest.work_path("")

    setup_environment.setup_bin_dir()

    env = Environment()  # required

    with LocalYtHolder(yt_work_dir=pj(work_dir, "yt_wd")) as yt:
        yt_prefix = "//home/superdups/sd_mr"
        yt_sd_db = pj(yt_prefix, "sd_db")

        conf_dir = yatest.binary_path("robot/superdups/packages/conf")
        bin_dir = env.binary_path
        cm = Cm(
            bin_dir=bin_dir,
            cm_sh=yatest.binary_path("robot/superdups/packages/binaries/main.sh"),
            hostlist=pj(conf_dir, "hostlist"),
            env_args={
                "BIN_DIR": yatest.binary_path("robot/superdups/packages/binaries"),
                "CLOUD_HOME": work_dir,
                "CONFIGS": conf_dir,
                "CURRENT_TIME": "1539950667",
                "EXPORT_PATH": pj(yt_prefix, "export/rthub/superdups"),
                "HISTORY_DIR": pj(yt_prefix, "history"),
                "JUPITER_TABLES_PREFIX": "//home/jupiter",
                "MR_SERVER": yt.get_proxy(),
                "RECRAWL_PERIOD": "20",
                "ROT_PERIOD": "30",
                "STATBOX_MR_SERVER": yt.get_proxy(),
                "STATBOX": "//statbox/reqans-log",
                "SUPERDUPS_DB": yt_sd_db,
                "SERP_HYPS_ENABLED": "true",
                "TESTING_FLAG": "true"
            }
        )

        yt.upload(pj(work_dir, "test_resource"), "//", write_format="yson")

        cm.check_call_target("main.finish", timeout=999999)

        result_state = yt.get(pj(yt_prefix, "delivery", "@for_production"))
        yt_result = pj(yt_prefix, "delivery", result_state, "SuperDups")
        result_table = list(yt.yt_client.read_table(yt_result, raw=True, format="dsv"))
        result_table.sort()

        # resolve_hosts/run_spider are skipped in tests, so their input has to be checked as well
        yt_hosts = pj(yt_prefix, "unique_hosts")
        hosts_table = list(yt.yt_client.read_table(yt_hosts, raw=True, format="dsv"))
        hosts_table.sort()

        result = pj(work_dir, "sd_db.result")
        with open(result, "w") as result_file:
            result_file.writelines(result_table)
            result_file.writelines(hosts_table)

        return yatest.canonical_file(result)
