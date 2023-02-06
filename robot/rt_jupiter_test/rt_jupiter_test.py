#!/usr/bin/env python

import logging
from os.path import join as pj
from shutil import copyfile

from robot.library.python.common_test import run_safe
from robot.library.yuppie.modules.environment import Environment

from robot.mercury.test.common import start_local_mercury, run_mercury_processing
from robot.mercury.test.common import YT_PREFIX as CALLISTO_YT_PREFIX
from robot.mercury.test.common import get_config_dir as get_mercury_config_dir

from robot.jupiter.test.common import launch_local_jupiter
from robot.jupiter.cmpy.library import state
from robot.jupiter.library.python import yt_utils


def setup_local_jupiter_cm(lj):
    lj.get_cm().set_var("YT_USER", "root")
    lj.get_cm().set_var("INCREMENTAL_MODE", "false")
    lj.get_cm().set_var("PudgeEnabled", "false")
    lj.get_cm().set_var("SearchTiers", '["WebTier0", "WebTier0Mini"]')
    lj.get_cm().set_var("RtYandex.SkipRemergeTables", "true")
    lj.get_cm().set_var("RtYandex.SkipSpreadJupiterDoc", "false")
    lj.get_cm().set_var("RtYandex.SkipRtDeltaTables", "false")

    lj.get_cm().set_var("RtYandex.CallistoPrefix", CALLISTO_YT_PREFIX)

    lj.get_cm().toggle_target_restarts("rt_yandex.finish", False)
    lj.get_cm().toggle_target_restarts("cleanup_sp.finish", False)


def setup_local_mercury_cm(lm):
    lm.cm.set_var("YT_USER", "root")
    lm.cm.set_var("MrPrefix", CALLISTO_YT_PREFIX)
    lm.cm.set_var("CompositeTable.AutoReshardPeriod", "5")
    lm.cm.set_var("CompositeTable.SleepBeforeUnmount", "5")


def cleanup_jupiter_prefix(lj):
    for subdir in lj.get_yt().list(lj.get_prefix()):
        if subdir != "mercury":
            lj.get_yt().remove(pj(lj.get_prefix(), subdir), recursive=True)
    yt_utils.clear_user_attributes(lj.get_yt().create_yt_client(), lj.get_prefix())


def cleanup_prev_states(lj):
    lj.erase_prev_states()
    lj.set_current_state("production", state.EMPTY_STATE)


def make_jupiter_backup(lj):
    lj.get_yt().move("//home/jupiter/delivery", "//home/delivery_backup")
    lj.get_yt().move("//home/jupiter/bert_async/export", "//home/bert_async_export_backup")

    lj.get_yt().create_dir("//home/jupiter_attributes_backup")
    yt_utils.copy_user_attributes(lj.get_yt().create_yt_client(), lj.get_prefix(), "//home/jupiter_attributes_backup")


def restore_jupiter_backup(lj):
    lj.get_yt().move("//home/delivery_backup", "//home/jupiter/delivery")
    lj.get_yt().move("//home/bert_async_export_backup", "//home/jupiter/bert_async/export", recursive=True)
    yt_utils.clear_user_attributes(lj.get_yt().create_yt_client(), lj.get_prefix())
    yt_utils.copy_user_attributes(lj.get_yt().create_yt_client(), "//home/jupiter_attributes_backup", lj.get_prefix())

    # TODO: remove once SkipRemerge is false and acceptance, export are built
    lj.get_yt().create_dir("//home/jupiter/acceptance")
    lj.get_yt().create_dir("//home/jupiter/export")
    lj.get_yt().create_dir("//home/jupiter/srpool")
    lj.get_yt().create_dir("//home/jupiter/sample")


def copy_patched_tier_scheme_from_jupiter(lj, lm):
    jupiter_path = lj.tier_scheme_path
    mercury_path = pj(get_mercury_config_dir(), "TierSchemeJupiterPatched.pb.txt")
    copyfile(jupiter_path, mercury_path)


def create_local_jupiter_and_mercury(env, links):
    lj = launch_local_jupiter(env, test_data="integration.tar", yatest_links=links)
    setup_local_jupiter_cm(lj)

    make_jupiter_backup(lj)
    cleanup_jupiter_prefix(lj)

    lm = start_local_mercury(env=env, yt=lj.get_yt(), callisto=True, configuration="callisto_jupiter_beta",
                             run_cm=True, cm_working_dir=pj(env.output_path, "mercury_cm"),
                             webfreshtier_shards=2)
    setup_local_mercury_cm(lm)

    copy_patched_tier_scheme_from_jupiter(lj, lm)
    return lj, lm


def launch_test(env, links):
    logging.info("Creating local Jupiter and local Mercury..")
    lj, lm = create_local_jupiter_and_mercury(env, links)

    logging.info("Running Callisto..")
    run_mercury_processing(lm, worker_config_overrides=["mercury_rtjupitertest_config_override.pb.txt"])
    lm.cm.check_call_target("composite_table.finish.JupiterDoc", timeout=10 * 60)

    logging.info("Cleaning up Jupiter prefix after Callisto finish..")
    cleanup_jupiter_prefix(lj)
    restore_jupiter_backup(lj)
    cleanup_prev_states(lj)

    logging.info("Running RT Jupiter..")
    lj.get_cm().check_call_target("rt_yandex.finish", timeout=60 * 60)
    lj.get_cm().check_call_target("cleanup_sp.finish", timeout=10 * 60)

    # TODO: Enable building shards when fixed
    # logging.info("Building shards..")
    # lj.build_shards(tier_to_build="WebTier1", state=lj.get_prev_state("shards_prepare"))

    logging.info("Dumping results..")
    lj.dump_jupiter_table(env.table_dumps_dir, "selectionrank", lj.get_current_state("rt_yandex"), "url_to_shard",
                          bucketed=True, sort_by=["Host", "Path", "Shard"])
    # lj.dump_shards()


def test_entry(links):
    env = Environment()
    return run_safe(env.hang_test, launch_test, env, links)
