import robot.jupiter.test.common as jupiter_integration
from robot.library.yuppie.modules.environment import Environment
from robot.mercury.cmpy.config.mercury import create_config as create_mercury_config
from robot.mercury.cmpy.config import MEDIUM_DEFAULT
import json
from os.path import join as pj

from robot.mercury.test.common import (
    YT_PREFIX,
    start_local_mercury,
    run_mercury_processing,
    flush_table
)


def flush_tables(yt):
    tables = [
        pj(YT_PREFIX, "UrlInfo"),
        pj(YT_PREFIX, "Duplicates")
    ]

    for table in tables:
        flush_table(yt, table)


def get_prefixes(config):
    prefixes = dict(config.Prefixes)
    for instance in prefixes:
        prefixes[instance]["fast_annotation"] = pj(YT_PREFIX, instance)
        prefixes[instance]["prefix"] = pj(YT_PREFIX, instance)
        prefixes[instance]["duplicates"] = pj(prefixes[instance]["prefix"], "duplicates")
    return prefixes


def get_mercury_cm_env_config():
    config = create_mercury_config(add_cmpy_modules=False, modify_env=False)
    cm_env = {
        "YT_USER": "root",
        "MrPrefix": pj(YT_PREFIX, "callisto"),
        "MrPrefixShardsPrepare": pj(YT_PREFIX, "callisto"),
        "SamplePrefix": pj(YT_PREFIX, "sample"),
        "TestWorkerMrPrefix": YT_PREFIX,
        "Prefixes": json.dumps(get_prefixes(config)),
        "FastAnnotation.MercuryPrefix": YT_PREFIX,
        "FastAnnotation.CallistoPrefix": pj(YT_PREFIX, "callisto"),
        "FastAnnotation.PreparePrimaryMedium": MEDIUM_DEFAULT,
        "FastAnnotation.MaxStates": str(3),
        "CheckTrialInstanceTimeout": str(10),
        "CountCheckTrialInstance": str(2),
        "TransferTimeout": str(10),
        "Injector.Urldat.UseImportedOnly": str(True),
        "Injector.Urldat.MissedDocumentMaxAge": str(86400 * 365 * 30),  # big enough to not depend from TInstant::Now()
        "Injector.Injector.TableSwitchTimeout": str(1),
    }
    return cm_env


def process(lj, env):
    # Must be CM var, not just environment var
    # We have to disable it because we don't have shards_prepare's walrus in previous state
    lj.get_cm().set_var("INCREMENTAL_MODE", "false")
    lj.get_cm().set_var("VERIFY_HAS_OPERATION_WEIGHT", "true")
    lj.get_cm().set_var("PudgeEnabled", "false")
    lj.get_cm().set_var("OpenFloodgate", "--open-floodgate")
    lj.get_cm().toggle_target_restarts("yandex.finish", False)
    lj.get_cm().toggle_target_restarts("rt_yandex.finish", False)
    lj.get_yt().create_dir(pj(env.mr_prefix, "remerge"))
    jupiter_state = lj.get_testing_current_state()

    # Starts local mercury and uploads data to YT, so it is to be run prior to mercury processing
    lm = start_local_mercury(
        env=env,
        run_cm=True,
        run_tm=True,
        cm_env=get_mercury_cm_env_config(),
        cm_working_dir=pj(env.output_path, "mercury_cm"),
        yt=lj.get_yt(),
        run_secondary_yt=True,
    )
    lm.cm.set_var("JupiterServer", lm.yt.get_proxy())
    lm.cm.set_var("UseDuplicatesForVerification", "true")

    lj.set_testing_current_state(jupiter_state)
    lj.get_cm().check_call_targets(
        ["yandex.run_meta.duplicates_mr"],
        timeout=60 * 60,
        ignore_failed_log_re=jupiter_integration.yandex_meta_graph_re()
    )
    lj.set_prev_state("yandex", lj.get_current_state("yandex"))

    lm.yt.create_dir(pj(YT_PREFIX, "callisto"))
    lm.cm.check_call_target("injector.finish", timeout=10 * 60)
    lm.cm.check_call_target("injector_urldat.finish", timeout=10 * 60)

    flush_tables(lm.yt)

    lm.cm.check_call_target("rtdups.finish", timeout=10 * 60)

    # First pass
    run_mercury_processing(lm, worker_config_overrides=["mercury_injectortest_config_override.pb.txt"])


def test_diff(links):
    env = Environment(diff_test=True)
    cm_env = {
        "DeletionMode": "aggressive",
        "Feedback.DupGroupLimit": "3",
    }
    with jupiter_integration.launch_local_jupiter(
            env,
            cm_env=cm_env,
            test_data=["integration.tar"],
            yatest_links=links,
            cm_bin_dir=env.get_cm_bin_dir()
    ) as local_jupiter:
        return jupiter_integration.call_jupiter(env.hang_test, process, local_jupiter, env)
