from robot.library.python.common_test import run_safe
from robot.blrt.library.local_blrt import start_local_blrt
from robot.blrt.test.worker_test.common import get_worker_test_local_blrt_config, run_worker_over_pocket, POCKET_STATE
from robot.blrt.test.common.dump_tables import dump_pocket_tables, dump_state_tables
from robot.blrt.test.common.testing_current_state import set_testing_current_state
from robot.jupiter.library.python.jupiter_util import add_time_to_state

from robot.library.yuppie.modules.environment import Environment

from yt.wrapper.http_helpers import get_proxy_url
from os.path import join as pj

import yatest.common

SAMPLE_STATE = "20200101-120000"


def build_sample_test_local_blrt_config():
    local_blrt_config = get_worker_test_local_blrt_config("perf")
    local_blrt_config.update({
        "worker_configs": {
            "external_config_override_files": [yatest.common.source_path("robot/blrt/test/common/blrt_config_override_worker_test_perf.pb.txt")]
        },
        "cm": {
            "configuration": "blrt_prestable"
        }
    })
    return local_blrt_config


def build_sample_test_acceptance_blrt_config(local_blrt):
    acceptance_blrt_config = get_worker_test_local_blrt_config("perf")
    acceptance_blrt_config.update({
        "worker_configs": {
            "external_config_override_files": [yatest.common.source_path("robot/blrt/test/common/blrt_config_override_worker_test_perf.pb.txt")]
        },
        "yt": {
            "cluster": get_proxy_url(client=local_blrt.yt_client),
            "prefix": "//home/acceptance",
            "test_data": None
        },
        "cm": {
            "working_dir": yatest.common.output_path("cm_acceptance_working_dir"),
            "install_dir": yatest.common.output_path("cm_acceptance_install_dir"),
            "configuration": "blrt_acceptance"
        }
    })
    return acceptance_blrt_config


def make_sample(local_blrt):
    local_blrt.cm.set_var("MakeSample.SkipTaskAndOffer.Dyn", "True")
    set_testing_current_state(local_blrt, {"sample": SAMPLE_STATE})
    local_blrt.cm.check_call_target("make_sample.finish", timeout=5 * 60)
    local_blrt.yt_client.set(pj(local_blrt.yt_prefix, "sample", SAMPLE_STATE, "@jupiter_meta", "yandex_testing_current_state"), ({"blrt_make_pocket": POCKET_STATE}))


def deploy_sample(acceptance_blrt):
    acceptance_blrt.cm.set_var("DeploySample.SkipTaskAndOffer.Dyn", "True")
    acceptance_blrt.cm.set_var("DeploySample.SamplePrefix", "//home/blrt")
    acceptance_blrt.cm.check_call_target("deploy_sample.finish", timeout=15 * 60)


def run_test_on_acceptance_blrt(acceptance_blrt):
    deploy_sample(acceptance_blrt)

    acceptance_blrt.cm.check_call_target("import_to_pocket.finish." + acceptance_blrt.task_type, timeout=10 * 60)
    with acceptance_blrt.run_workers():
        set_testing_current_state(acceptance_blrt, {"blrt_make_pocket": add_time_to_state(POCKET_STATE, 1)})
        acceptance_blrt.cm.check_call_target("rotate_pocket.finish." + acceptance_blrt.task_type, reset_path=True, timeout=45 * 60)


def launch_sample_test(local_blrt):
    run_worker_over_pocket(local_blrt)
    make_sample(local_blrt)
    with start_local_blrt(build_sample_test_acceptance_blrt_config(local_blrt), for_tests=True) as acceptance_blrt:
        run_test_on_acceptance_blrt(acceptance_blrt)
        dump_pocket_tables(acceptance_blrt)
        dump_state_tables(acceptance_blrt)


def test_entry(links):
    env = Environment()
    with start_local_blrt(build_sample_test_local_blrt_config(), for_tests=True) as local_blrt:
        run_safe(env.hang_test, launch_sample_test, local_blrt)
