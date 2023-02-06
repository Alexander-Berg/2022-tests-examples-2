from robot.blrt.library.local_blrt import start_local_blrt
from robot.blrt.test.common.dump_tables import dump_state_tables
from robot.blrt.test.common.queue_helpers import wait_queue_fully_consumed

from robot.library.python.common_test import run_safe
from robot.library.yuppie.modules.environment import Environment
from os.path import join as pj


def build_preview_worker_test_local_blrt_config():
    return {
        "task_type": "preview",
        "yt": {
            "test_data": pj("sample", "blrt_preview.tar")
        },
        "preview_worker": {
            "enable": True
        }
    }


def launch_test(local_blrt):
    with local_blrt.run_workers():
        wait_queue_fully_consumed(local_blrt, "input_queue", "worker")
    dump_state_tables(local_blrt)


def test_entry(links):
    env = Environment()
    local_blrt_config = build_preview_worker_test_local_blrt_config()
    with start_local_blrt(local_blrt_config, for_tests=True) as local_blrt:
        run_safe(env.hang_test, launch_test, local_blrt)
