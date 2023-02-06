#!/usr/bin/env python

from os.path import join as pj

import yatest.common

from robot.library.python.common_test import run_safe
from robot.library.python.build_shards import build_shards as jupiter_build_shards
from robot.library.yuppie.modules.environment import Environment

from robot.mercury.test.common import (
    YT_PREFIX,
    TIER_SCHEME_PATCHED_FILE,
    start_local_mercury,
    run_mercury_processing,
    get_config_dir,
    patch_tier_scheme_callisto,
    patch_upload_rules
)

from robot.mercury.test.comparsion_callisto_test.callisto_test import (
    dump_shards,
    dump_tables,
    get_testing_current_state,
    get_cm_env_config,
    flush_callisto_tables,
    run_callisto_subgraph,
    BUILD_SHARD_PY,
    BUILD_SHARD_DST_DIRNAME,
)


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


def launch_test(env, links):
    webfreshtier_shards=1
    # Patch tier scheme before LocalMercury and worker starting
    patch_tier_scheme_callisto(webfreshtier_shards)  # NumShards: 1 to simplify comparison of inverted indexes in JUPITER_COMPARE_INDEX
    patch_upload_rules("UploadRulesCallisto.pb.txt", 3)  # Set FreshnessDays to 3 like indexer_test has

    # Starts local mercury and uploads data to YT, so it is to be run prior to mercury processing
    lm = start_local_mercury(
        env=env,
        run_cm=True,
        cm_env=get_cm_env_config(),
        callisto=True,
        webfreshtier_shards=webfreshtier_shards,
    )

    lm.cm.set_var("INCREMENTAL_MODE", "false")
    lm.cm.set_var("PudgeEnabled", "false")

    lm.yt.create_dir(pj(YT_PREFIX, "sample"))  # for cleanup.cleanup.sample

    # Processes input and writes callisto tables
    run_mercury_processing(lm, worker_config_overrides=["mercury_comparsion_callistotest_config_override.pb.txt"])

    flush_callisto_tables(lm)

    # Runs callisto's part of shards_prepare
    run_callisto_subgraph(lm)

    # Run shardmerge_utils
    build_shards(lm=lm, env=env)

    # Dump shards
    dump_shards(env)

    # Dump tables
    dump_tables(lm=lm, env=env)

    return None


def test_entry(links):
    env = Environment()
    return run_safe(env.hang_test, launch_test, env, links)
