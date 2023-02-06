import robot.jupiter.test.common as jupiter_integration
from robot.library.yuppie.modules.environment import Environment
from robot.mercury.cmpy.config.mercury import create_config as create_mercury_config
from robot.mercury.cmpy.config import MEDIUM_DEFAULT
import json

from robot.mercury.test.common import (
    YT_PREFIX,
    start_local_mercury,
    run_rtdups_processing,
    prepare_rtdups_queue,
    restore_rtdups_queue,
    flush_table
)

from os.path import join as pj
import logging
import time

SHUFFLER_QUEUE_PATH = pj(YT_PREFIX, "shuffler_queue/ShufflerQueue")
SHUFFLER_QUEUE_BACKUP_PATH = pj(YT_PREFIX, "shuffler_queue/ShufflerQueueBackup")
FAST_ANNOTATION_DIR_NAME = "fast_annotation"


def prepare_shuffler_queue(lj, env):
    SHUFFLER_QUEUE_PATH = pj(YT_PREFIX, "shuffler_queue/ShufflerQueue")
    lj.get_yt().remove(SHUFFLER_QUEUE_PATH)

    spread_async_path = get_spread_async_path(env.mr_prefix)
    spread_async_states = sorted(lj.get_yt().list(spread_async_path))
    last_spread_async_state = spread_async_states[-1]

    shuffler_queue_in_spread_path = pj(spread_async_path, last_spread_async_state, "shuffler_queue")

    flush_table(lj.get_yt(), shuffler_queue_in_spread_path)
    lj.get_yt().freeze_table(shuffler_queue_in_spread_path, sync=True)
    lj.get_yt().copy(shuffler_queue_in_spread_path, SHUFFLER_QUEUE_PATH)
    logging.info("Copied {} to {}".format(shuffler_queue_in_spread_path, SHUFFLER_QUEUE_PATH))
    lj.get_yt().mount_table(SHUFFLER_QUEUE_PATH, sync=True)
    logging.info("Mounted {}".format(SHUFFLER_QUEUE_PATH))


def flush_tables(yt):
    tables = [
        pj(YT_PREFIX, "UrlInfo"),
        pj(YT_PREFIX, "Duplicates")
    ]

    for table in tables:
        flush_table(yt, table)


def get_spread_async_path(prefix):
    return pj(prefix, "spread_rtdelta_async")


def get_prefixes(config):
    prefixes = dict(config.Prefixes)
    for instance in prefixes:
        prefixes[instance]["tables"] = pj(YT_PREFIX, instance, "jupiter_import_tables")
        prefixes[instance]["fast_annotation"] = pj(YT_PREFIX, instance)
        prefixes[instance]["prefix"] = pj(YT_PREFIX, instance)
        prefixes[instance]["duplicates"] = pj(prefixes[instance]["prefix"], "duplicates")
    return prefixes


def get_bundles(config):
    bundles = dict(config.Bundles)
    for instance in bundles:
        bundles[instance] = "default"
    return bundles


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
        "Bundles": json.dumps(get_bundles(config)),
    }
    return cm_env


def create_fast_annotation_dirs(lm):
    fa_dir_mercury = pj(YT_PREFIX, FAST_ANNOTATION_DIR_NAME)
    fa_dir_callisto = pj(YT_PREFIX, "callisto", FAST_ANNOTATION_DIR_NAME)
    if not lm.yt.exists(fa_dir_mercury):
        lm.yt.create_dir(fa_dir_mercury)
    if not lm.yt.exists(fa_dir_callisto):
        lm.yt.create_dir(fa_dir_callisto)


def create_jupiter_import_dir(lm):
    lm.yt.create_dir(pj(YT_PREFIX, "callisto", "jupiter_import_tables"))


def prepare_jupiter_cm(lj, env):
    cm = lj.get_cm()

    # Must be CM var, not just environment var
    # We have to disable it because we don't have shards_prepare's walrus in previous state
    cm.set_var("Selectionrank.UpdateTierConfigNoCheck", "true")
    cm.set_var("INCREMENTAL_MODE", "false")
    cm.set_var("VERIFY_HAS_OPERATION_WEIGHT", "true")
    cm.set_var("PudgeEnabled", "false")
    cm.set_var("SpreadRTHub.ProduceShufflerQueue", "true")
    cm.set_var("SpreadRTHub.BertStateTimeLag", 0)
    cm.set_var("OpenFloodgate", "--open-floodgate")
    cm.set_var("DuplicatesMR.UseFastAnnotations", "true")

    cm.toggle_target_restarts("yandex.finish", False)
    cm.toggle_target_restarts("rt_yandex.finish", False)
    cm.toggle_target_restarts("cleanup.finish", False)
    cm.toggle_target_restarts("spread_rthub_async.finish", False)


def run_spread(lj, env):
    yt = lj.get_yt()
    cm = lj.get_cm()

    spread_async_path = get_spread_async_path(env.mr_prefix)
    spread_async_states = sorted(lj.get_yt().list(spread_async_path))

    shuffler_queue_path = None

    for spread_async_state in spread_async_states:
        logging.info("Running convertion for {}".format(spread_async_state))

        if shuffler_queue_path:
            yt.link(shuffler_queue_path, pj(spread_async_path, spread_async_state, "shuffler_queue"))

        lj.set_current_state("spread_rthub", spread_async_state)

        cm.reset_path("spread_rthub_async.finish", timeout=60 * 60)
        cm.forced_run("spread_rthub_async.create_shuffler_queue", timeout=60 * 60)
        cm.check_targets(["spread_rthub_async.create_shuffler_queue"], timeout=60 * 60)

        if shuffler_queue_path is None:
            shuffler_queue_path = pj(spread_async_path, spread_async_state, "shuffler_queue")

    # Used in debug to suspend test after sample convertion
    # cm.wait_active("sample.finish", timeout=60 * 60)


def process(lj, env):
    prepare_jupiter_cm(lj, env)
    jupiter_state = lj.get_testing_current_state()

    run_spread(lj, env)

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
    lm.cm.set_var("RTDupsExpectConsistentDuplicates", "true")
    lm.cm.set_var("UseDuplicatesForVerification", "true")

    create_fast_annotation_dirs(lm)
    create_jupiter_import_dir(lm)
    prepare_shuffler_queue(lj, env)
    prepare_rtdups_queue(lm.yt)

    lj.erase_prev_states()
    lj.set_testing_current_state(jupiter_state)
    lj.get_cm().check_call_targets(
        ["yandex.run_meta.duplicates_mr"],
        timeout=60 * 60,
        ignore_failed_log_re=jupiter_integration.yandex_meta_graph_re()
    )

    lj.get_cm().check_call_target(
        "externaldat_host.finish",
        timeout=60 * 60,
        ignore_failed_log_re=jupiter_integration.yandex_meta_graph_re()
    )

    # Transfer fast annotations from jupiter
    lm.cm.check_call_target("fast_annotation.link_annotation_union_to_mercury", timeout=60 * 60)

    # Place fast annotation union in callisto and mount it
    lm.cm.check_call_targets(
        ["jupiter_import.create_links.callisto.tables", "fast_annotation.finish.transfer.callisto"],
        timeout=60 * 60
    )

    # Useful for viewer when debugging
    lm.yt.link(pj(YT_PREFIX, "callisto/FastAnnotationUnion"), pj(YT_PREFIX, "fast_annotation/FastAnnotationUnion"))

    # First pass
    run_rtdups_processing(lm, config_overrides=["mercury_jupiter_integration_config_override.pb.txt"])

    # Wait for roles release
    time.sleep(5)

    restore_rtdups_queue(lm.yt)

    # Second pass
    run_rtdups_processing(lm, config_overrides=["mercury_jupiter_integration_config_override.pb.txt"])

    flush_tables(lm.yt)

    lm.cm.check_call_target("rtdups.finish", timeout=10 * 60)


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
    ) as local_jupiter:
        return jupiter_integration.call_jupiter(env.hang_test, process, local_jupiter, env)
