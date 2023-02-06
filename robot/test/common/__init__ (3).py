#!/usr/bin/env python

import json
import os

from ads.bsyeti.big_rt.cli.lib import create_queue

from robot.mercury.library.local_mercury import LocalMercury
from robot.mercury.scripts import setup_tables

from robot.jupiter.protos.upload_rules_pb2 import TUploadRuleConfigList
from robot.library.oxygen.base.protos.tier_scheme_pb2 import TTierScheme

import google.protobuf.text_format as pbtext

import yatest.common

import logging
from os.path import join as pj
from os.path import exists
from shutil import copyfile
import yt.wrapper as yt_wrapper
import time


CONFIG_OVERRIDE_SOURCE_FILE = "mercury_test_config_override.pb.txt"
CONFIG_OVERRIDE_PATCHED_FILE = "patched_mercury_test_config_override.pb.txt"

SAMOVAR_CONFIG_SOURCE_FILE = "test_instance_config.pb.txt"
SAMOVAR_CONFIG_PATCHED_FILE = "patched_test_instance_config.pb.txt"

TIER_SCHEME_SOURCE_FILE = "TierSchemeCallisto.pb.txt"
TIER_SCHEME_PATCHED_FILE = "TierSchemeCallistoPatched.pb.txt"

UPLOAD_RULES_PATCHED_FILE = "UploadRulesPatched.pb.txt"

TABLE_FLUSH_PERIOD = 1000  # milliseconds
TABLE_FLUSH_SLEEP = 10     # seconds should be greater than TABLE_FLUSH_PERIOD

YT_PREFIX = "//home/jupiter/mercury"  # make sure to aling with mercury_test_config_override.pb.txt
SAMOVAR_PREFIX = "//home/samovar"
SHUFFLER_QUEUE_PATH = pj(YT_PREFIX, "shuffler_queue/ShufflerQueue")
RTDUPS_QUEUE_PATH = pj(YT_PREFIX, "rtdups_queue/RTDupsQueue")


SMALL_URL_DATA_SCHEMA = {
    'attributes': {'strict': True, 'unique_keys': True},
    'value': [
        {'required': False, 'type': 'uint64', 'name': 'HostHash', 'sort_order': 'ascending'},
        {'required': False, 'type': 'uint64', 'name': 'UrlHashFirst', 'sort_order': 'ascending'},
        {'required': False, 'type': 'uint64', 'name': 'UrlHashSecond', 'sort_order': 'ascending'},
        {'required': False, 'type': 'string', 'name': 'Data'},
    ]
}


def prepare_rtdups_queue(yt):
    yt.remove(RTDUPS_QUEUE_PATH)
    yt.freeze_table(SHUFFLER_QUEUE_PATH, sync=True)
    yt.copy(SHUFFLER_QUEUE_PATH, RTDUPS_QUEUE_PATH)
    logging.info("Copied {} to {}".format(SHUFFLER_QUEUE_PATH, RTDUPS_QUEUE_PATH))
    yt.mount_table(RTDUPS_QUEUE_PATH, sync=True)
    logging.info("Mounted {}".format(RTDUPS_QUEUE_PATH))


def restore_rtdups_queue(yt):
    yt.unmount_table(RTDUPS_QUEUE_PATH, sync=True)
    yt.remove(RTDUPS_QUEUE_PATH)

    yt.copy(SHUFFLER_QUEUE_PATH, RTDUPS_QUEUE_PATH)
    logging.info("Copied {} to {}".format(SHUFFLER_QUEUE_PATH, RTDUPS_QUEUE_PATH))
    yt.mount_table(RTDUPS_QUEUE_PATH, sync=True)
    logging.info("Mounted {}".format(RTDUPS_QUEUE_PATH))


def get_config_dir():
    return yatest.common.binary_path("robot/mercury/test/common/config")


def get_common_exec_config(config_overrides=None):
    config = {
        "config_dir": get_config_dir(),
        "config": "mercury_config.pb.txt",
    }

    resulting_config_overrides = [
        CONFIG_OVERRIDE_PATCHED_FILE
    ]

    if config_overrides:
        resulting_config_overrides += config_overrides

    config["config_overrides"] = resulting_config_overrides

    return config


def get_worker_exec_config(config_overrides=None):
    config = get_common_exec_config(config_overrides)
    config["worker_binary"] = yatest.common.binary_path("robot/mercury/packages/worker/worker")
    return config


def get_rtdups_exec_config(config_overrides=None):
    config = get_common_exec_config(config_overrides)
    config["rtdups_binary"] = yatest.common.binary_path("robot/mercury/packages/rtdups/rtdups")
    return config


def get_logfetcher_exec_config(logfetcher_config_overrides=None):
    config = {
        "config_dir": get_config_dir(),
        "logfetcher_binary": yatest.common.binary_path("robot/mercury/packages/logfetcher/logfetcher"),
        "logfetcher_config": "mercury_config.pb.txt",
    }

    logfetcher_overrides = [
        CONFIG_OVERRIDE_PATCHED_FILE
    ]

    if logfetcher_config_overrides:
        logfetcher_overrides += logfetcher_config_overrides

    config["logfetcher_config_overrides"] = logfetcher_overrides

    return config


def start_local_mercury(
        env,
        cluster=None,
        prefix=YT_PREFIX,
        run_cm=False,
        run_tm=False,
        run_secondary_yt=False,
        cm_env=None,
        cm_working_dir=None,
        mercury_packages="robot/mercury/packages",
        test_data_primary="mercury3.tar",
        test_data_secondary=None,
        skip_setup=False,
        aux_args=None,
        callisto=False,
        samovar_prefix=SAMOVAR_PREFIX,
        yt=None,
        secondary_yt=None,
        webfreshtier_shards=None,
        **kwargs
):
    lm_args = {
        "working_dir": env.output_path,
        "cluster": cluster or env.cluster,
        "prefix": "//home" if prefix == YT_PREFIX else prefix,
        "test_data": test_data_primary,
        "ram_drive_path": env.ram_drive_path,
        "yt": yt,
        "secondary_yt": secondary_yt,
        "cm_working_dir": cm_working_dir
    }

    if run_cm:
        cm_config_path = yatest.common.binary_path(pj(mercury_packages, "configs"))
        patched_tier_scheme_path = pj(get_config_dir(), TIER_SCHEME_PATCHED_FILE)
        if exists(patched_tier_scheme_path):
            copyfile(patched_tier_scheme_path, pj(cm_config_path, TIER_SCHEME_PATCHED_FILE))

        patched_upload_rules_path = pj(get_config_dir(), UPLOAD_RULES_PATCHED_FILE)
        if exists(patched_upload_rules_path):
            copyfile(patched_upload_rules_path, pj(cm_config_path, UPLOAD_RULES_PATCHED_FILE))

        lm_args.update({
            "cm_bin_dir": env.get_cm_bin_dir(),
            "no_cm": False,
            "cm_env": cm_env,
            "cm_binaries_path": yatest.common.binary_path(pj(mercury_packages, "binaries")),
            "cm_cmpy_path": yatest.common.binary_path(pj(mercury_packages, "cmpy")),
            "cm_config_path": cm_config_path,
            "disable_restart": True,
        })

    if run_tm:
        lm_args.update({"no_tm": False})

    if run_secondary_yt:
        lm_args.update({
            "no_secondary_yt": False,
            "secondary_prefix": "//home",
            "secondary_test_data": test_data_secondary
        })

    if aux_args:
        lm_args.update(aux_args)

    lm_args.update(kwargs)

    lm = LocalMercury(**lm_args)

    if not skip_setup:
        setup_tables.update_tables_for_callisto()  # we use CallistoTablesRoot for ShufflerQueue, it creates all callisto tables in TTableLayout
        setup_tables.update_descriptors_for_local_yt()
        setup_tables.setup_tables(lm.yt.get_proxy(), prefix, modify=True, create=True, reshard=True)
        # creates QYT to store links to favicons for urls
        create_queue(pj(prefix, "FaviconsLinks"), 64, "default", None, "weak", False, lm.yt.yt_client)
        if callisto:
            assert isinstance(webfreshtier_shards, int)
            rt_index_queue_shards = webfreshtier_shards
        else:
            rt_index_queue_shards = 64
        create_queue(pj(prefix, "RtIndexQueue"), rt_index_queue_shards, "default", None, "weak", False, lm.yt.yt_client)

        lm.yt.set(prefix + "/@worker_is_in_charge", True)
        lm.yt.set(prefix + "/@sink_is_in_charge", True)
        lm.yt.set(prefix + "/@suppressor_limit_multiplier", 2**32)  # disable suppression
        for i in xrange(16):
            lm.yt.link(pj(prefix, "SamovarUrlSample"), pj(samovar_prefix, "url_data_parts/url_data_part.{:03d}".format(i)))

        lm.yt.link(pj(prefix, "SamovarHostSample"), pj(samovar_prefix, "host_data"))
        lm.yt.set(samovar_prefix + "/@is_in_charge", True)
        # TODO: move it somewhere in proper place (JUPITER-1376)
        for i in xrange(16):
            table_path = pj(samovar_prefix, "small_url_data_parts", "small_url_data_part.{:03d}".format(i))
            lm.yt.yt_client.create('table', table_path, recursive=True)
            lm.yt.yt_client.alter_table(table_path, schema=yt_wrapper.yson.to_yson_type(SMALL_URL_DATA_SCHEMA['value'], attributes=SMALL_URL_DATA_SCHEMA['attributes']), dynamic=True)
            lm.yt.yt_client.mount_table(table_path)

    return lm


def patch_mercury_config_override(lm, source_path, patched_path):
    logging.info("Patching mercury override configs")
    with open(source_path) as config_override_source_file:
        config_override = config_override_source_file.read()
    with open(patched_path, "w") as config_override_file:
        config_override_patched = config_override.replace("{{yt_proxy}}", lm.yt.get_proxy())
        config_override_file.write(config_override_patched)


def patch_tier_scheme_callisto(num_shards):
    assert isinstance(num_shards, int), "Invalid num_shards type"
    logging.info("Patching callisto tier scheme")
    tier_scheme = TTierScheme()

    source_path = pj(get_config_dir(), TIER_SCHEME_SOURCE_FILE)
    with open(source_path) as source_file:
        pbtext.Parse(source_file.read(), tier_scheme)

    was_web_fresh_tier = False
    for tier_config in tier_scheme.TierConfig:
        if tier_config.TierName == "WebFreshTier":
            assert len(tier_config.GroupConfig) == 1, "Unsupported callisto tier scheme config"
            tier_config.GroupConfig[0].NumShards = num_shards
            was_web_fresh_tier = True
            break

    assert was_web_fresh_tier, "Can't find WebFreshTier in TierScheme " + source_path

    patched_path = pj(get_config_dir(), TIER_SCHEME_PATCHED_FILE)
    with open(patched_path, "w") as patched_file:
        pbtext.PrintMessage(tier_scheme, patched_file)


def patch_upload_rules(source_filename, freshness_days):
    # you should specify source_filename because it could be used in comparsion_indexer_test too
    assert isinstance(freshness_days, int), "Invalid freshness_days type"
    logging.info("Patching upload rules")
    upload_rules = TUploadRuleConfigList()

    source_path = pj(get_config_dir(), source_filename)
    with open(source_path) as source_file:
        pbtext.Parse(source_file.read(), upload_rules)

    for upload_rule in upload_rules.UploadRules:
        condition = upload_rule.Condition
        if condition.HasField("UploadFilter") and condition.UploadFilter.HasField("FreshnessDays"):
            condition.UploadFilter.FreshnessDays = freshness_days

    patched_path = pj(get_config_dir(), UPLOAD_RULES_PATCHED_FILE)
    with open(patched_path, "w") as patched_file:
        pbtext.PrintMessage(upload_rules, patched_file)


def prepare_mercury_configs(lm, dst_config_dir=None):
    patch_mercury_config_override(
        lm,
        pj(get_config_dir(), CONFIG_OVERRIDE_SOURCE_FILE),
        pj(dst_config_dir or get_config_dir(), CONFIG_OVERRIDE_PATCHED_FILE)
    )

    patch_mercury_config_override(
        lm,
        pj(get_config_dir(), SAMOVAR_CONFIG_SOURCE_FILE),
        pj(dst_config_dir or get_config_dir(), SAMOVAR_CONFIG_PATCHED_FILE)
    )


def run_mercury_processing(lm, worker_config_overrides=None, aux_args=None):
    exec_config = get_worker_exec_config(config_overrides=worker_config_overrides)

    prepare_mercury_configs(lm)

    exec_args = [
        exec_config["worker_binary"],
        "--config-file", exec_config["config"],
        "--data-dir", yatest.common.work_path(),
        "--config-dir", exec_config["config_dir"]
    ]

    for override_file in exec_config["config_overrides"]:
        exec_args += ["--config-override-file", override_file]

    if aux_args:
        exec_args += aux_args

    logging.info("Starting Mercury processing")
    yatest.common.execute(
        exec_args,
        env={
            "YT_USER": "root",
            "YT_TOKEN": "itdoesnotmatter",  # required by abs/bsyeti/libs/ytex/client
            "GDB:WorkerMain": yatest.common.get_param("GDB:WorkerMain", "")}
    )
    logging.info("Finished Mercury processing")


def run_rtdups_processing(lm, config_overrides=None, aux_args=None):
    exec_config = get_rtdups_exec_config(config_overrides=config_overrides)

    prepare_mercury_configs(lm)

    exec_args = [
        exec_config["rtdups_binary"],
        "--config-file", exec_config["config"],
        "--data-dir", yatest.common.work_path(),
        "--config-dir", exec_config["config_dir"]
    ]

    for override_file in exec_config["config_overrides"]:
        exec_args += ["--config-override-file", override_file]

    if aux_args:
        exec_args += aux_args

    logging.info("Starting RTDups processing")
    yatest.common.execute(
        exec_args,
        env={
            "YT_USER": "root",
            "YT_TOKEN": "itdoesnotmatter",  # required by abs/bsyeti/libs/ytex/client
            "GDB:RTDupsMain": yatest.common.get_param("GDB:RTDupsMain", "")}
    )
    logging.info("Finished RTDups processing")


def run_logfetcher(lm, logfetcher_config_overrides=None, aux_args=None):
    exec_config = get_logfetcher_exec_config(logfetcher_config_overrides=logfetcher_config_overrides)

    prepare_mercury_configs(lm)

    exec_args = [
        exec_config["logfetcher_binary"],
        "--config-file", exec_config["logfetcher_config"],
        "--config-dir", exec_config["config_dir"],
        "--log-dir", yatest.common.work_path("logging"),
        "--do-once",
    ]

    for override_file in exec_config["logfetcher_config_overrides"]:
        exec_args += ["--config-override-file", override_file]

    if aux_args:
        exec_args += aux_args

    logging.info("Starting logfetcher")
    yatest.common.execute(
        exec_args,
        env={
            "YT_USER": "root",
        }
    )


def sort_file_sink(src, dst):
    data = sorted(json.loads(open(src).read().decode('utf-8', 'replace')), key=lambda x: x.get('SaasUrl'))
    open(dst, 'w').write(json.dumps(data, indent=4, ensure_ascii=False, sort_keys=True).encode('utf-8'))


def dump_file_sinks():
    for fname in sorted(os.listdir(yatest.common.work_path())):
        if fname.startswith("file_sink."):
            out_path = yatest.common.output_path(fname)
            sort_file_sink(yatest.common.work_path(fname), out_path)


def flush_table(yt, path):
    logging.info("Flushing {}".format(path))
    yt.set(path + "/@forced_compaction_revision", 1)
    yt.set(path + "/@dynamic_store_auto_flush_period", TABLE_FLUSH_PERIOD)
    yt.remount_table(path)
    time.sleep(TABLE_FLUSH_SLEEP)
