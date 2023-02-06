#!/usr/bin/env python

import logging
import os.path

import yatest.common

from robot.mercury.test.common import YT_PREFIX
from robot.mercury.test.common import flush_table
from robot.mercury.test.common import start_local_mercury
from robot.mercury.test.common import run_mercury_processing
from robot.mercury.test.common import run_logfetcher
from robot.mercury.test.common import dump_file_sinks

from robot.library.python.common_test import run_safe
from robot.library.yuppie.modules.environment import Environment


def dump_tables(local_mercury, dst_dir):
    table_paths = [os.path.join(YT_PREFIX, "FactorsDump")]
    yt = local_mercury.get_yt()
    logging.info("Flushing and freezing tables")
    for table_path in table_paths:
        flush_table(yt, table_path)
        yt.freeze_table(table_path, sync=True)
    logging.info("Downloading tables into %s", dst_dir)
    yt.download(table_paths, dst_dir)


def launch_test(env, links):
    lm = start_local_mercury(env)

    aux_args = [
        "--log-dir", yatest.common.work_path("logging"),
        "--log-prefix", yatest.common.output_path("worker_log_")
    ]

    run_mercury_processing(lm, aux_args=aux_args, worker_config_overrides=["mercury_workertest_config_override.pb.txt"])

    run_logfetcher(lm)

    dump_file_sinks()
    dump_tables(lm, yatest.common.output_path("table_dumps"))  # this dirname is expected in the CompareIntegrationTestOutput task


def test_entry(links):
    env = Environment()
    return run_safe(env.hang_test, launch_test, env, links)
