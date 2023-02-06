from robot.blrt.test.common.run_imports import run_imports
from robot.blrt.test.common.testing_current_state import set_testing_current_state
from robot.jupiter.library.python.jupiter_util import add_time_to_state
from robot.blrt.test.common.queue_helpers import wait_queue_fully_consumed
from robot.cmpy.library.utils import snake_to_camel

from os.path import join as pj

POCKET_STATE = "20200101-120000"
FUNNEL_STATE = "20200101-120000"

SR_BANNER_QUEUE_CONSUMER = "blrt-selection-rank-worker"
CLIENT_LIMIT_QUEUE_CONSUMER = "blrt-sr-worker-client-limit"
DOMAIN_LIMIT_QUEUE_CONSUMER = "blrt-sr-worker-domain-limit"


def get_worker_test_local_blrt_config(task_type):
    return {
        "task_type": task_type,
        "yt": {
            "test_data": pj("sample", "blrt_{}.tar".format(task_type))
        },
        "resharder": {
            "enable": True
        },
        "worker": {
            "enable": True
        },
        "selection_rank_worker": {
            "enable": True
        }
    }


def run_worker_over_pocket(local_blrt):
    run_imports(local_blrt)

    local_blrt.cm.set_var("ImportToPocket.TaoTablesSourceDir." + snake_to_camel(local_blrt.task_type), pj(local_blrt.yt_prefix, "external_data", "tasks_and_offers"))
    set_testing_current_state(local_blrt, {"blrt_make_pocket": POCKET_STATE})
    local_blrt.cm.check_call_target("rotate_pocket.finish." + local_blrt.task_type, timeout=5 * 60)
    local_blrt.cm.check_call_target("import_to_pocket.finish." + local_blrt.task_type, timeout=5 * 60)
    set_testing_current_state(local_blrt, {
        "blrt_make_pocket": add_time_to_state(POCKET_STATE, 1),
        "blrt_funnel": FUNNEL_STATE,
    })

    with local_blrt.run_workers():
        local_blrt.cm.check_call_target("rotate_pocket.finish." + local_blrt.task_type, reset_path=True, timeout=45 * 60)
        wait_queue_fully_consumed(local_blrt, pj("selection_rank", local_blrt.task_type, "sr_banner_queue"), SR_BANNER_QUEUE_CONSUMER)
        wait_queue_fully_consumed(local_blrt, pj("selection_rank", local_blrt.task_type, "client_limit_queue"), CLIENT_LIMIT_QUEUE_CONSUMER)
        wait_queue_fully_consumed(local_blrt, pj("selection_rank", local_blrt.task_type, "domain_limit_queue"), DOMAIN_LIMIT_QUEUE_CONSUMER)

    local_blrt.cm.check_call_targets([
        "trim_resharder_queue.trim.sr_banner." + local_blrt.task_type,
        "cm_stats.blrt_worker." + local_blrt.task_type,
        "cm_stats.blrt_selection_rank_worker." + local_blrt.task_type,
    ], timeout=15 * 60)
