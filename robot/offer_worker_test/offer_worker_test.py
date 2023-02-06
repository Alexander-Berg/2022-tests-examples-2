from robot.blrt.library.local_blrt import start_local_blrt
from robot.blrt.library.python.bindings.selection_rank_limits_handler import TLimitHandler
from robot.blrt.test.common.dump_tables import dump_funnel_tables, dump_state_tables
from robot.blrt.test.common.queue_helpers import wait_queue_fully_consumed
from robot.blrt.test.common.cs_helpers import wait_consuming_system_fully_consumed
from robot.blrt.test.common.testing_current_state import set_testing_current_state
from robot.blrt.test.common.run_imports import run_imports

from robot.library.python.common_test import run_safe
from robot.library.yuppie.modules.environment import Environment

import yatest.common
from os.path import join as pj


WORKER_DATACAMP_OFFER_QYT_CONSUMER = "worker"
OFFER_WORKER_CONSUMER = "offer-worker"
SR_BANNER_QUEUE_CONSUMER = "blrt-selection-rank-worker"
CLIENT_LIMIT_QUEUE_CONSUMER = "blrt-sr-worker-client-limit"
DOMAIN_LIMIT_QUEUE_CONSUMER = "blrt-sr-worker-domain-limit"

FUNNEL_STATE = "20200101-120000"
TASK_EXPORT_STATE = "20200101-120000"


def build_offer_worker_test_local_blrt_config():
    return {
        "task_type": "perf",
        "yt": {
            "test_data": pj("sample", "blrt_offer_perf.tar")
        },
        "worker_configs": {
            "config_override_files": ["blrt_config_override_datacamp.pb.txt", "blrt_config_override_test.pb.txt"],
            "external_config_override_files": [yatest.common.source_path("robot/blrt/test/common/blrt_config_override_worker_test_perf.pb.txt")]
        },
        "resharder": {
            "enable": True
        },
        "offer_worker": {
            "enable": True
        },
        "worker": {
            "enable": True
        },
        "selection_rank_worker": {
            "enable": True
        },
        #  Should fix configuration for offer_worker_test
        #  "cm": {
        #  "configuration": "blrt_multidc"
        #  }
    }


def launch_test(local_blrt):
    run_imports(local_blrt)
    client_limit_handler = TLimitHandler(local_blrt.cluster, local_blrt.yt_prefix, local_blrt.task_type, "client")
    order_limit_hander = TLimitHandler(local_blrt.cluster, local_blrt.yt_prefix, local_blrt.task_type, "order")
    client_limit_handler.set_limit(9833597, 10)
    order_limit_hander.set_limit(158750797, 8)
    with local_blrt.run_workers():
        wait_consuming_system_fully_consumed(local_blrt, pj("resharder", local_blrt.task_type, "big_rt", "datacamp_offer"))
        wait_queue_fully_consumed(local_blrt, pj("resharder", local_blrt.task_type, "datacamp_offer_queue"), OFFER_WORKER_CONSUMER)
        wait_queue_fully_consumed(local_blrt, pj("offer_worker", local_blrt.task_type, "offer_storage_queue"), WORKER_DATACAMP_OFFER_QYT_CONSUMER)
        wait_queue_fully_consumed(local_blrt, pj("selection_rank", local_blrt.task_type, "sr_banner_queue"), SR_BANNER_QUEUE_CONSUMER)
        wait_queue_fully_consumed(local_blrt, pj("selection_rank", local_blrt.task_type, "client_limit_queue"), CLIENT_LIMIT_QUEUE_CONSUMER)
        wait_queue_fully_consumed(local_blrt, pj("selection_rank", local_blrt.task_type, "domain_limit_queue"), DOMAIN_LIMIT_QUEUE_CONSUMER)

    set_testing_current_state(local_blrt, {
        "blrt_funnel": FUNNEL_STATE,
        "blrt_task_export": TASK_EXPORT_STATE,
    })
    local_blrt.cm.check_call_target("task_export.finish." + local_blrt.task_type, timeout=15 * 60)

    local_blrt.cm.check_call_targets([
        "funnel.finish." + local_blrt.task_type,
        "trim_resharder_queue.trim.datacamp_offer." + local_blrt.task_type,
        "trim_resharder_queue.trim.sr_banner." + local_blrt.task_type,
        "cm_stats.blrt_resharder." + local_blrt.task_type,
        "cm_stats.blrt_worker." + local_blrt.task_type,
        "cm_stats.blrt_selection_rank_worker." + local_blrt.task_type,
    ], timeout=15 * 60)

    dump_state_tables(local_blrt)
    dump_funnel_tables(local_blrt)


def test_entry(links):
    env = Environment()
    local_blrt_config = build_offer_worker_test_local_blrt_config()
    with start_local_blrt(local_blrt_config, for_tests=True) as local_blrt:
        run_safe(env.hang_test, launch_test, local_blrt)
