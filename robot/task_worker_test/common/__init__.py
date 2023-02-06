from robot.blrt.test.common.dump_tables import dump_task_tables
from robot.blrt.test.common.queue_helpers import wait_queue_fully_consumed
from robot.blrt.test.common.testing_current_state import set_testing_current_state
from robot.blrt.library.local_blrt import start_local_blrt
from robot.library.python.common_test import run_safe
from robot.library.yuppie.modules.environment import Environment
from os.path import join as pj


CAESAR_QYT_CONSUMER = "blrt-task-resharder"
RESHARDER_QYT_CONSUMER = "blrt-task-worker"
TEST_STATE = "20200101-120000"


def _build_task_worker_test_local_blrt_config(task_type):
    return {
        "task_type": task_type,
        "perl_env": {
            "enable": False
        },
        "task_worker": {
            "enable": True
        },
        "yt": {
            "test_data": pj("sample", "blrt_task_{}.tar".format(task_type))
        },
        "setup_yt_env": {
            "queue_shards": 1
        }
    }


def _launch_task_worker_test(local_blrt):
    with local_blrt.run_workers():
        wait_queue_fully_consumed(local_blrt, pj("external_data", "caesar", "BannerLandTaskOrderLog"), CAESAR_QYT_CONSUMER)
        wait_queue_fully_consumed(local_blrt, pj("external_data", "caesar", "BannerLandTaskBannerLog"), CAESAR_QYT_CONSUMER)
        wait_queue_fully_consumed(local_blrt, pj("resharder", local_blrt.task_type, "task_order_queue"), RESHARDER_QYT_CONSUMER)
        wait_queue_fully_consumed(local_blrt, pj("resharder", local_blrt.task_type, "task_banner_queue"), RESHARDER_QYT_CONSUMER)

    set_testing_current_state(local_blrt, {"blrt_task_export": TEST_STATE})
    local_blrt.cm.check_call_targets([
        "trim_resharder_queue.trim.task_order." + local_blrt.task_type,
        "trim_resharder_queue.trim.task_banner." + local_blrt.task_type,
        "trim_resharder_queue.trim.task_feeds_to_resend." + local_blrt.task_type,
        "cm_stats.blrt_task_worker." + local_blrt.task_type,
        "task_export.finish." + local_blrt.task_type
    ], timeout=10 * 60)

    dump_task_tables(local_blrt)


def run_task_worker_test(task_type):
    env = Environment()
    local_blrt_config = _build_task_worker_test_local_blrt_config(task_type)
    with start_local_blrt(local_blrt_config, for_tests=True) as local_blrt:
        run_safe(env.hang_test, _launch_task_worker_test, local_blrt)
