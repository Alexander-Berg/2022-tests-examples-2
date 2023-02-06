from library.python.testing.deprecated import setup_environment

from robot.library.python.common_test import run_safe
from robot.library.yuppie.modules.environment import Environment

from robot.mercury.test.common import start_local_mercury, prepare_mercury_configs, CONFIG_OVERRIDE_PATCHED_FILE
from robot.mercury.cmpy.config import MEDIUM_DEFAULT
from robot.mercury.cmpy.config.mercury import create_config

import json
import logging
import time
import yatest.common
from os.path import join as pj


SERVICE_NAME = "fast_annotation"
MAIN_DIR_NAME = SERVICE_NAME
TOOL_NAME = SERVICE_NAME

CLEANUP_DIR_NAMES = ["annotations", "delivery_snapshot", "docs", "recrawl"]
REMOTE_DIR_NAME = "data"

GOAL_TABLE_NAME = "FastAnnotationUnion"
RECRAWL_TABLE_NAME = "RecrawlList"

MERCURY_PREFIX = "//home/mercury"
CALLISTO_PREFIX = "//home/callisto"

SAMOVAR_RECRAWL_PREFIX = "//home/lemur-data/mercury_annotations"
MAX_STATES = 2

TEST_DATA_FILENAME_PRIMARY = "test_data_primary.tar"
TEST_DATA_FILENAME_SECONDARY = "test_data_secondary.tar"


def get_prefixes(config):
    prefixes = dict(config.Prefixes)
    for instance in prefixes:
        prefixes[instance][SERVICE_NAME] = pj(MERCURY_PREFIX, instance)
        prefixes[instance]["prefix"] = pj(MERCURY_PREFIX, instance)
        prefixes[instance]["jupiter_urls"] = pj(prefixes[instance]["prefix"], "jupiter_urls")
    return prefixes


def is_full_table(instance):
    # TODO(alexromanov): get it from config, check full table too
    return instance in ["callisto", "main"]


def get_cm_env_config(prefixes):
    cm_env = {
        "Prefixes": json.dumps(prefixes),
        "FastAnnotation.MercuryPrefix": MERCURY_PREFIX,
        "FastAnnotation.CallistoPrefix": CALLISTO_PREFIX,
        "FastAnnotation.MaxStates": str(MAX_STATES),
        "FastAnnotation.SamovarRecrawlPrefix": SAMOVAR_RECRAWL_PREFIX,
        "FastAnnotation.PreparePrimaryMedium": MEDIUM_DEFAULT,
        "FastAnnotation.FilteredUnionTabletCount": str(10),
        "FastAnnotation.FullUnionTabletCount": str(20),
        "CheckTrialInstanceTimeout": str(10),
        "CountCheckTrialInstance": str(2),
        "TransferTimeout": str(10),
        "YT_USER": "root",
        "Recuperation.MercuryConfigOverrides.FastAnnotation": json.dumps([CONFIG_OVERRIDE_PATCHED_FILE])
    }
    return cm_env


def check_clean_up(lm, prefixes, config):
    main_dir = pj(MERCURY_PREFIX, MAIN_DIR_NAME)
    prod_state = lm.secondary_yt.get(main_dir + "/@jupiter_meta/production_current_state")
    prev_state = lm.secondary_yt.get(main_dir + "/@jupiter_meta/production_prev_state")

    def check_states(states, name):
        assert len(states) == MAX_STATES, "Invalid state count ({0}) after clean up for {1}".format(len(states), name)
        assert prod_state in states, "Production state missed: {}".format(name)
        assert prev_state in states, "Previous state missed: {}".format(name)

    for dir_name in CLEANUP_DIR_NAMES:
        path = pj(main_dir, dir_name)
        states = lm.secondary_yt.list(path)
        check_states(states, path)

    for instance, data in prefixes.items():
        if instance not in config.FastAnnotation.Settings:
            continue
        if config.FastAnnotation.Settings[instance].share_with:
            continue
        path = pj(data[SERVICE_NAME], REMOTE_DIR_NAME)
        states = lm.yt.list(path)
        check_states(states, path)


def check_table_entry(lm, mode, path, secondary):
    logging.info("Checking table %s", path)
    exec_args = [
        pj(lm.install_binaries_path, TOOL_NAME),
        mode,
        "--server-name", lm.get_yt(secondary).get_proxy(),
        "--table-path", path,
    ]

    yatest.common.execute(
        exec_args,
        env={
            "YT_USER": "root",
        }
    )


def check_tables(lm, prefixes, config):
    # check union tables
    mercury_union_dumped = False
    for instance, data in prefixes.iteritems():
        if instance not in config.FastAnnotation.Settings:
            continue
        table_yt_path = pj(data[SERVICE_NAME], GOAL_TABLE_NAME)
        assert lm.yt.get(table_yt_path + "/@dynamic"), "Table {} is not dynamic".format(table_yt_path)
        if not is_full_table(instance) and not mercury_union_dumped:
            dumped_table_path = yatest.common.output_path("result_mercury_union")
            lm.dump_table(
                table_yt_path,
                dumped_table_path,
                secondary=False
            )
            mercury_union_dumped = True

        if not is_full_table(instance):  # somebody has full table
            check_table_entry(lm, "CheckMercuryUnionTable", table_yt_path, secondary=False)

    # check recrawl table
    main_dir = pj(MERCURY_PREFIX, MAIN_DIR_NAME)
    prod_state = lm.secondary_yt.get(main_dir + "/@jupiter_meta/production_current_state")

    dumped_recrawl_table_path = yatest.common.output_path("result_recrawl")
    recrawl_yt_path = pj(SAMOVAR_RECRAWL_PREFIX, "{0}_{1}".format(RECRAWL_TABLE_NAME, prod_state))
    check_table_entry(lm, "CheckRecrawlTable", recrawl_yt_path, secondary=True)
    lm.dump_table(
        recrawl_yt_path,
        dumped_recrawl_table_path,
        secondary=True
    )


def start(lm):
    lm.cm.check_call_target(
        "{}.finish".format(SERVICE_NAME),
        timeout=10 * 60)

    # Waiting for staging cluster transfers end
    while lm.cm.get_active_targets():
        time.sleep(5)


def launch_test(env):
    config = create_config(add_cmpy_modules=False, modify_env=False)
    prefixes = get_prefixes(config)
    lm = start_local_mercury(
        env=env,
        run_cm=True,
        run_tm=True,
        run_secondary_yt=True,
        cm_env=get_cm_env_config(prefixes),
        test_data_primary=TEST_DATA_FILENAME_PRIMARY,
        test_data_secondary=TEST_DATA_FILENAME_SECONDARY,
        skip_setup=True
    )

    prepare_mercury_configs(lm, dst_config_dir=lm.install_config_path)

    for instance in config.FastAnnotation.TrialInstances:
        lm.get_yt().set("//home/mercury/{}/@sink_is_in_charge".format(instance), True)  # instance before trial transfer must be in charge

    start(lm)
    check_clean_up(lm, prefixes, config)
    check_tables(lm, prefixes, config)


def test_entry():
    setup_environment.setup_bin_dir()
    env = Environment()
    return run_safe(env.hang_test, launch_test, env)
