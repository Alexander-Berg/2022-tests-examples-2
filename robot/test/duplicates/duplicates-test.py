#!/usr/bin/env python

import logging

from library.python.testing.deprecated import setup_environment
import robot.jupiter.test.common as jupiter_integration
from robot.library.yuppie.modules.environment import Environment

from robot.jupiter.library.python import ytcpp
from robot.jupiter.cmpy.library import state
import robot.jupiter.test.common.constellations as constellations


def process(lj, env):
    input_data = constellations.InputData()

    logging.info("Collecting test cases...")
    checks = constellations.add_tests(input_data)

    input_data.log_urldat()

    logging.info("Writing and sorting tables...")
    yt = ytcpp.YtCppClient(config=ytcpp.YtCppConfig(Cluster=lj.yt_proxy))

    input_data.finish(yt)
    lj.set_current_state("yandex", constellations.CURRENT_STATE)
    yt.set("//home/jupiter/@rt_yandex_state_to_snapshot", state.EMPTY_STATE)
    yt.set("//home/jupiter/@async_states_meta", {"yandex": {constellations.CURRENT_STATE: {}}})

    logging.info("Starting constellations...")
    lj.get_cm().check_call_target("duplicates.finish", timeout=60 * 60)

    logging.info("Reading outputs...")
    output_data = constellations.OutputData("//home/jupiter/duplicates/{state}/Duplicates")
    output_data.read(yt)
    output_data.log_duplicates()

    logging.info("Checking outputs...")
    constellations.check_results(checks, output_data)


def test_diff(links):
    setup_environment.setup_bin_dir()
    env = Environment(diff_test=True)

    with jupiter_integration.launch_local_jupiter(
        env,
        test_data="constellations.tar",
        yatest_links=links,
        cm_env={"MrPrefixRemerge": "//home/jupiter"},
    ) as local_jupiter:
        return jupiter_integration.call_jupiter(env.hang_test, process, local_jupiter, env)
