#!/usr/bin/env python

import logging
from os.path import join as pj
from os.path import basename
import time

import yatest.common

from robot.jupiter.library.python.dump_shards import dump_shards as jupiter_dump_shards

from robot.library.python.common_test import run_safe
from robot.library.python.build_shards import build_shards as jupiter_build_shards
from robot.library.yuppie.modules.apply_cmd import ApplyCmd
from robot.library.yuppie.modules.environment import Environment

from robot.mercury.test.common import (
    YT_PREFIX,
    TIER_SCHEME_PATCHED_FILE,
    start_local_mercury,
    run_mercury_processing,
    get_config_dir,
    patch_tier_scheme_callisto,
    flush_table
)


BUILD_SHARD_DST_DIRNAME = 'shards'
BUILD_SHARD_LOGS_DIRNAME = '.mkdir'
BUILD_SHARD_PY = 'robot/jupiter/cm/scripts/build_shard.py'

TEST_HOST_CFG = 'HostCfgTest.pb.txt'


def run_callisto_subgraph(lm):
    lm.cm.check_call_target("callisto.finish", timeout=10 * 60)
    lm.cm.wait_target_complete("callisto.pipeline.finish", timeout=10 * 60)

    lm.cm.toggle_target_restarts("cleanup.finish", False)
    lm.cm.check_call_target("cleanup.finish", timeout=10 * 60)

    # Waiting for staging cluster transfers end
    while lm.cm.get_active_targets():
        time.sleep(5)


def flush_callisto_tables(lm):
    tables = [
        pj(YT_PREFIX, "CallistoDoc", "current_delta")
    ]

    for table in tables:
        flush_table(lm.yt, table)


def get_cm_env_config():
    cm_env = {
        "YT_USER": "root",
        "MrPrefix": YT_PREFIX,
        "MrPrefixShardsPrepare": YT_PREFIX,
        "Callisto.HostAttrTablePath": pj(YT_PREFIX, "JupiterHerfSample"),
        "Callisto.JupiterUrlsTablePath": pj(YT_PREFIX, "JupiterUrlsSortedByUrlSample")
    }
    return cm_env


def get_testing_current_state(yt_client):
    return yt_client.get(pj(YT_PREFIX, "@jupiter_meta", "yandex_testing_current_state"))


def build_shards(lm, env):  # noqa
    jupiter_build_shards(
        shard_deploy_bundle_dir=yatest.common.binary_path("robot/jupiter/packages/shard_deploy_bundle"),
        yt_proxy=lm.yt.get_proxy(),
        prefix=pj(YT_PREFIX),
        state=get_testing_current_state(lm.yt),
        build_shards_dst_dir=pj(env.output_path, BUILD_SHARD_DST_DIRNAME),
        tier_scheme_path=pj(get_config_dir(), TIER_SCHEME_PATCHED_FILE),
        callisto_mode=True,
        testing=True,
        build_shards_py=pj(env.arcadia, BUILD_SHARD_PY),
        tier_to_build='WebFreshTier',
        shards_block_fetch="100:100",
        test_buckets_count=1
    )


def dump_shards(env):
    logging.info("Dumping shards")
    jupiter_dump_shards(
        pj(env.output_path, BUILD_SHARD_DST_DIRNAME),
        yatest.common.binary_path("robot/jupiter/packages/printers"),
        check_fails=False,
    )


def dump_serialized_tables(lm, env):
    printers_dir = yatest.common.binary_path("robot/jupiter/packages/printers")
    src_path = pj(YT_PREFIX, "JupiterDoc", "current_delta")
    flush_table(lm.yt, src_path)
    # file name is prepended with "file_sink." just to pass CompareIntegrationTestOutput's filter for files worth checking
    file_path = pj(env.output_path, "file_sink.JupiterDoc.current_delta.json")
    logging.info("Downloading %s as %s", src_path, file_path)
    ApplyCmd(
        [
            pj(printers_dir, "test_table_dump"),
            "DumpJupiterDocData",
            "--server-name", lm.yt.get_proxy(),
            "--src-path", src_path,
            "--file-path", file_path,
        ],
    )


def dump_tables(lm, env):
    logging.info("Dumping tables")
    tables = [
        pj(YT_PREFIX, "CallistoDoc", "current_delta"),
        pj(YT_PREFIX, "UrlsHistoryLog"),
        pj(YT_PREFIX, "RtIndexQueue", "queue"),
    ]

    for path in tables:
        logging.info("Dumping table %s", path)
        assert lm.yt.exists(path), "Table %s doesn't exist" % path
        flush_table(lm.yt, path)
        lm.dump_table(
            path,
            pj(env.output_path, basename(path))
        )


def launch_test(env, links):
    webfreshtier_shards = 10
    # Patch tier scheme before LocalMercury and worker starting
    patch_tier_scheme_callisto(webfreshtier_shards)  # NumShards: 10 for WebFreshTier

    # Starts local mercury and uploads data to YT, so it is to be run prior to mercury processing
    lm = start_local_mercury(
        env=env,
        run_cm=True,
        cm_env=get_cm_env_config(),
        callisto=True,
        webfreshtier_shards=webfreshtier_shards,
    )

    lm.cm.set_var("INCREMENTAL_MODE", "false")
    lm.cm.set_var("VERIFY_HAS_OPERATION_WEIGHT", "true")
    lm.cm.set_var("PudgeEnabled", "false")
    lm.cm.set_var("Callisto.SelectUrlsRowCountThreshold", "10")
    lm.cm.set_var("Callisto.ShardMigrationStepsPerState", "{}".format(webfreshtier_shards / 2))

    lm.yt.create_dir(pj(YT_PREFIX, "sample"))  # for cleanup.cleanup.sample

    # Processes input and writes callisto tables
    run_mercury_processing(lm, worker_config_overrides=["mercury_callistotest_config_override.pb.txt"])

    flush_callisto_tables(lm)

    # Runs callisto's part of shards_prepare
    run_callisto_subgraph(lm)

    # Run shardmerge_utils
    build_shards(lm=lm, env=env)

    # Dump shards
    dump_shards(env)

    # Dump tables
    dump_tables(lm=lm, env=env)
    dump_serialized_tables(lm=lm, env=env)

    return None


def test_entry(links):
    env = Environment()
    return run_safe(env.hang_test, launch_test, env, links)
