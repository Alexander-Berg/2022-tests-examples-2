#!/usr/bin/env python

import logging
import json
import os
import shutil
import yatest.common
from yatest.common.network import PortManager

from os.path import join as pj
from robot.jupiter.library.python.dump_shards import dump_shards as jupiter_dump_shards
from robot.jupiter.library.python.dump_shards import get_dump_mode_list
from robot.library.python.common_test import run_safe
from robot.library.yuppie.modules.environment import Environment

from robot.mercury.test.common import start_local_mercury
from robot.mercury.test.common import run_mercury_processing

YT_PREFIX = "//home/jupiter/mercury"  # make sure to aling with mercury_test_config_override.pb.txt

RTY_BINARY = yatest.common.binary_path("saas/rtyserver_test/jupi_dump_test/jupi_dump_test")

JUPITER_PRINTERS = yatest.common.binary_path("robot/jupiter/packages/printers")


def get_test_param(name, default):
    result = yatest.common.get_param(name, None)
    if result is None:
        env_name = name.replace(":", "_")
        result = os.getenv(env_name, default)

    return result


def get_rty_configs_path():
    env_path = os.getenv("RTY_CONFIGS_PATH")
    if env_path:
        return yatest.common.source_path(env_path)
    else:
        return yatest.common.test_source_path("saas_configs")


def get_default_test_name():
    test_name = os.getenv("RTY_DEFAULT_TEST_NAME")
    if not test_name:
        logging.info("RTY_DEFAULT_TEST_NAME is not set, using TestRtyJupiIndexDump")
        return 'TestRtyJupiIndexDump'
    logging.info("RTY_DEFAULT_TEST_NAME is set to " + test_name)
    return test_name


def run_mercury_to_saas_dump(env):
    lm = start_local_mercury(env)

    run_mercury_processing(lm, worker_config_overrides=["mercury_indexertest_config_override.pb.txt"])

    protobin = yatest.common.work_path("messages.protobin")
    assert os.path.isfile(protobin)
    return protobin


def run_saas_to_shard(protobin, rty_wd, links, env):
    if os.path.isdir(rty_wd):
        shutil.rmtree(rty_wd)
    os.makedirs(rty_wd)

    protobin_file = yatest.common.work_path("messages.protobin")
    if os.path.realpath(protobin) != os.path.realpath(protobin_file):
        shutil.copyfile(protobin, protobin_file)

    rtymodels_path = yatest.common.work_path("models")
    rtymodels_new_path = yatest.common.work_path("oxy_data")
    if os.path.isdir(rtymodels_path) and not os.path.isdir(rtymodels_new_path):
        os.rename(rtymodels_path, rtymodels_new_path)

    rty_method_name = get_test_param("RTY:Method", get_default_test_name())
    rty_configs_path = get_rty_configs_path()

    logging.info("Starting RTYServer indexing")
    with PortManager() as portman:
        port = portman.get_port(3000)
        logging.info("Using port %i as RTY_TESTS_START_PORT" % port)
        yatest.common.execute(
            [
                RTY_BINARY,
                "-k", "off",
                "-t", rty_method_name,
                "-r", rty_wd,
                "-g", pj(rty_configs_path, "test_local_clusterconf.json"),
                "-d", yatest.common.work_path(),
                "-V", "CONF_PATH={}".format(rty_configs_path)],
            env={
                "GDB:RtyJupiTest": get_test_param("GDB:RtyJupiTest", ""),
                "RTY_TESTS_START_PORT": "%i" % port}
        )

    with open(pj(rty_wd, "test_result.json")) as f:
        json_report = json.load(f)

    final_index = json_report.get("shard", None)
    assert final_index is not None
    logging.info("Finished RTYServer indexing")
    return final_index


def dump_shard(shard_path):
    logging.info("Dumping shard %s", shard_path)

    # please, do not add new index types here
    dump_modes = set([
        'refinv',
        'refarc',
        'linkanndir',
        'frq',

        # Canonized in Freshness only, for the moment
        'docurl',       # Freshness only, will stay
        'herf',         # legacy configuration
        'omniwad',      # legacy configuration
        'cat_c2p',
        'cat_c2s',
        'dmoz_c2p',
        'geoa_c2p',
        'geobase_c2cr',
        'geo_c2cc',
        'geo_c2p',
        'geo_c2s',
        'genre_c2p',
        'onl_c2p',
        'src_c2p',
        'xxx_c2p'
    ])

    dump_modes.update(get_dump_mode_list())

    return jupiter_dump_shards(shard_path, JUPITER_PRINTERS, dump_modes=list(dump_modes), single_shard=True, check_fails=False)


def launch_test(env, links):
    #
    # if no "TEST:*" params are given, the full test is executed (mercury.tar -> protobin -> shard -> index/.dumps)
    #
    # When debugging, it is possible to run the stages one at a time
    # For Step 1 only: --test-param TEST:Target=protobin
    #     Step 2 only: --test-param TEST:Target=shard --test-param TEST:protobin:output=$HOME/mydocs
    #     Step 3 only: --test-param TEST:Target=dump --test-param TEST:shard:output=$HOME/index_00000000000_0000000123
    partial_target = get_test_param("TEST:Target", "all")  # values: "protobin", "shard", "dump", "canon", "canon_sandbox"
    existing_saas_protobin = get_test_param("TEST:protobin:output", None)
    existing_saas_shard = get_test_param("TEST:shard:output", None)
    if partial_target == "protobin":
        existing_saas_protobin = None
    elif partial_target == "shard":
        existing_saas_shard = None
    elif partial_target == "dump" and existing_saas_shard is not None:
        existing_saas_protobin = ""    # not None

    rty_wd = yatest.common.work_path("rty_wd")

    if existing_saas_protobin is None:
        saas_protobin = run_mercury_to_saas_dump(env)
        if partial_target == "protobin":
            shutil.copyfile(saas_protobin, yatest.common.output_path("messages.protobin"))
            return None
    else:
        saas_protobin = existing_saas_protobin

    if existing_saas_shard is None:
        shard_path = run_saas_to_shard(saas_protobin, rty_wd, links, env)
        output_shard_path = yatest.common.output_path("index")
        shutil.copytree(shard_path, output_shard_path)
        shard_path = output_shard_path
        if partial_target == "shard":
            return None
    else:
        shard_path = existing_saas_shard

    if partial_target in ["dump", "all", "canon", "canon_sandbox"]:
        dump = dump_shard(shard_path)
        logging.info("Dump completed to %s", dump)

    if partial_target in ["canon"]:
        return [yatest.common.canonical_file(pj(dump, filename), local=True) for filename in os.listdir(dump)]

    if partial_target in ["canon_sandbox"]:
        return yatest.common.canonical_dir(dump)

    return None


def test_entry(links):
    env = Environment()
    return run_safe(env.hang_test, launch_test, env, links)
