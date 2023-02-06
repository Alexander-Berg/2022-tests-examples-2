from robot.library.python.common_test import run_safe
from robot.blrt.library.local_blrt import start_local_blrt
from robot.blrt.test.worker_test.common import get_worker_test_local_blrt_config, run_worker_over_pocket
from robot.blrt.test.common.dump_tables import dump_pocket_tables, dump_state_tables

from robot.library.yuppie.modules.environment import Environment

import yatest.common


def test_entry(links):
    env = Environment()
    local_blrt_config = get_worker_test_local_blrt_config("perf")
    local_blrt_config.setdefault("worker_configs", {})["external_config_override_files"] = [yatest.common.source_path("robot/blrt/test/common/blrt_config_override_worker_test_perf.pb.txt")]
    with start_local_blrt(local_blrt_config, for_tests=True) as local_blrt:
        run_safe(env.hang_test, run_worker_over_pocket, local_blrt)
        dump_pocket_tables(local_blrt)
        dump_state_tables(local_blrt)
