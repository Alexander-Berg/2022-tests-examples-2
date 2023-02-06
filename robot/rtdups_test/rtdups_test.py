#!/usr/bin/env python

from robot.library.python.common_test import run_safe
from robot.library.yuppie.modules.environment import Environment

from robot.mercury.test.common import run_rtdups_processing
from robot.mercury.test.common import prepare_rtdups_queue
from robot.mercury.test.common import dump_file_sinks
from robot.mercury.test.common import start_local_mercury


def launch_test(env, links):
    # Starts local mercury and uploads data to YT, so it is to be run prior to mercury processing
    lm = start_local_mercury(env=env)

    prepare_rtdups_queue(lm.yt)
    run_rtdups_processing(lm, config_overrides=["mercury_rtdupstest_config_override.pb.txt"])

    dump_file_sinks()

    return None


def test_entry(links):
    env = Environment()
    return run_safe(env.hang_test, launch_test, env, links)
