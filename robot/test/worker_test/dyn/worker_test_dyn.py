from robot.library.python.common_test import run_safe
from robot.blrt.library.local_blrt import start_local_blrt
from robot.blrt.test.worker_test.common import get_worker_test_local_blrt_config, run_worker_over_pocket
from robot.blrt.test.common.dump_tables import dump_pocket_tables

from robot.library.yuppie.modules.environment import Environment


def test_entry(links):
    env = Environment()
    local_blrt_config = get_worker_test_local_blrt_config("dyn")
    with start_local_blrt(local_blrt_config, for_tests=True) as local_blrt:
        run_safe(env.hang_test, run_worker_over_pocket, local_blrt)
        dump_pocket_tables(local_blrt)
        # we do not dump state and funnel tables for dyn because it's broken unless we have unique OfferId
