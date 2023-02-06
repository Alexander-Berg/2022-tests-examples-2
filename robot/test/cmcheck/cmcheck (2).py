import robot.jupiter.test.common as jupiter_integration
from robot.library.yuppie.modules import environment

from library.python.testing.deprecated import setup_environment
import yatest.common

import os


def process(local_jupiter, target_to_dump):
    local_jupiter.get_cm().check_call_target(target_to_dump)


def run_cmcheck(links, jupiter_instance, target_to_dump="yandex.start"):
    os.environ.clear()

    setup_environment.setup_bin_dir()

    env = environment.Environment()
    working_dir = os.path.join(yatest.common.output_path("working_dir"), jupiter_instance)

    cm_env = {
        "CMPY_LOG_FORMAT": "[%(levelname)s]  %(message)-100s"
    }

    with jupiter_integration.launch_local_jupiter(
        env,
        cm_env=cm_env,
        jupiter_instance=jupiter_instance,
        no_yt=True,
        working_dir=working_dir,
        yatest_links=links,
    ) as local_jupiter:
        return jupiter_integration.call_jupiter(env.hang_test, process, local_jupiter, target_to_dump)


def test_production_cmcheck(links):
    return run_cmcheck(links, "production")


def test_beta_cmcheck(links):
    return run_cmcheck(links, "beta")


def test_nightly_cmcheck(links):
    return run_cmcheck(links, "nightly")


def test_nightly2_cmcheck(links):
    return run_cmcheck(links, "nightly2")


def test_nightly3_cmcheck(links):
    return run_cmcheck(links, "nightly3")


def test_rthub_test_cmcheck(links):
    return run_cmcheck(links, "rthub_test")
