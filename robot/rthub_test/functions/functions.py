#!/usr/bin/env python

from robot.cmpy.library.run import BinaryRun
from robot.cmpy.library.cmapi import CmApi
from robot.cmpy.library.utils import read_token_from_file
from robot.library.python.sandbox.client import SandboxClient

from os.path import join as pj
import os
import shutil
import rthub_test_util as rt_util


# CM Targets
def get_platinum_urls_hosts_from_nightly(cfg):
    sample_path = cfg.SampleDir
    BinaryRun(
        pj(cfg.BinDir, 'sampler'),
        'filter',
        '--server', 'banach',
        '--sample', 'nightly',
        '--pool', cfg.YT_POOL,
        '//home/jupiter', sample_path
    ).do()


def clean_cmpy_tmp(cfg):
    for the_file in os.listdir(cfg.CmpyTmp):
        file_path = pj(cfg.CmpyTmp, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except BaseException as e:
            print e


def build_test_triggers(cfg):
    rt_util.build_triggers(
        cfg,
        cfg.BranchesArcPath,
        cfg.TestKiwiBranch,
        cfg.TestBuildTaskIdPath,
        "yweb/robot/kiwi_queries/robot/packages/main"
    )


def build_prev_triggers(cfg):
    rt_util.build_triggers(
        cfg,
        cfg.BranchesArcPath,
        cfg.PrevKiwiBranch,
        cfg.PrevBuildTaskIdPath,
        "yweb/robot/kiwi_queries/robot/packages/main"
    )


def build_aspam_pack(cfg):
    rt_util.build_triggers(
        cfg,
        cfg.TrunkArcPath,
        "trunk",
        cfg.AspamPackTaskIdPath,
        "yweb/robot/kiwi_queries/antispam/packages/rules"
    )


def build_triggers(cfg):
    return True


# def calc_triggers_performance(cfg):
#    test_perf_task_id = BinaryRun(
#        pj(cfg.JupiterScriptsDir, "sbclient.py"),
#        "--author-token", cfg.SandboxToken,
#        "RunTask",
#        "--task-name", "CALC_KIWI_TRIGGERS_PERFOMANCE",
#        "--task-params", json.dumps({
#            "aspam_pack": cfg.AspamPackResId,
#            "test_data": cfg.TestDataResId,
#            "trig_pack": prev_trig_res_id}),
#        "--task-descr", "Calculate performance for {}".format(cfg.PrevKiwiBranch),
#        "--task-priority", "NORMAL",
#        "--wait-success",
#    ).do(return_result=True, dry_run=cfg.DryRun)


def download_triggers_build(cfg):
    if os.path.exists("/var/tmp/kiwi_queries"):
        shutil.rmtree("/var/tmp/kiwi_queries")

    with open(cfg.BuildTaskIdPath) as f:
        task_id = f.read()

    sandbox = SandboxClient(token=read_token_from_file(cfg.SandboxTokenPath))
    res_info = sandbox.get_resource_info_by_task(
        resource_name="KWTRIGGER_FOLDER",
        task_id=task_id)

    sandbox.download_resource(
        dst_dir="/var/tmp",
        tmp_dir="/var/tmp",
        resource_info=res_info,
        skynet=True,
    )


def set_desc_and_format(cfg):
    BinaryRun(
        pj(cfg.CmpyBin, "mq_util"),
        "-p", "/var/tmp/kiwi_queries",
        "--set-description", "test_{}".format(cfg.KiwiBranch.replace("-", "_")),
        "--set-format", 99
    ).do(return_result=False, dry_run=cfg.DryRun)

    rt_util.prepare_test_exports(cfg, "/var/tmp/kiwi_queries")


# TODO: write ya update routine
def get_ya_tool(cfg):
    return True


def deploy_test_triggers(cfg):
    BinaryRun(
        pj(cfg.CmpyBin, "ya"),
        "kiwi",
        "deploy", "triggers",
        "--queries-dir", "/var/tmp/kiwi_queries",
        "-c", "kiwi1500.search.yandex.net",
        "-u", "zagevalo",
    ).do(return_result=False, dry_run=cfg.DryRun)
    BinaryRun(
        pj(cfg.CmpyBin, "ya"),
        "kiwi",
        "enable", "triggers",
        "--queries-dir", "/var/tmp/kiwi_queries",
        "-c", "kiwi1500.search.yandex.net",
        "-u", "zagevalo",
    ).do(return_result=False, dry_run=cfg.DryRun)


def deploy_test_procedures(cfg):
    BinaryRun(
        pj(cfg.CmpyBin, "ya"),
        "kiwi",
        "deploy", "procedures",
        "enable", "procedures",
        "--queries-dir", "/var/tmp/kiwi_queries",
        "-c", "kiwi1500.search.yandex.net",
        "-u", "zagevalo",
    ).do(return_result=False, dry_run=cfg.DryRun)


def deploy_test_exports(cfg):
    for exp in cfg.TestExports:
        BinaryRun(
            pj(cfg.CmpyBin, "ya"),
            "kiwi",
            "run", "exports",
            "--queries-dir", "/var/tmp/kiwi_queries/{}".format(exp),
            "-c", "kiwi1500.search.yandex.net",
            "-u", "zagevalo",
        ).do(return_result=False, dry_run=cfg.DryRun)


# Graph to get urls/hosts from nightly and mark them as IsPlatinum on kiwi_main

def init_update_initial_data(cfg):
    rt_util.clean_working_dir(cfg, pj(cfg.DataPrepareDir, "nightly_data"))


def get_nightly_urls(cfg):
    client = rt_util.get_yt_client(cfg)
    sample_state = rt_util.get_state(cfg, cfg.PROD_PREFIX, "sample", "current")
    nightly_sample_prefix = pj(cfg.PROD_PREFIX, "sample", sample_state, "nightly")
    if client.exists(pj(cfg.DataPrepareDir, "nightly_data/nightly_urls_{}".format(sample_state))):
        client.remove(pj(cfg.DataPrepareDir, "nightly_data/nightly_urls_{}".format(sample_state)))
    BinaryRun(
        pj(cfg.CmpyBin, "get_nightly_data"),
        "GetNightlyUrls",
        "--server-name", cfg.YT_PROXY,
        "--mr-prefix", nightly_sample_prefix,
        "--current-state", sample_state,
        "--buckets-count", 14,
        "--operation-weight", 10,
        "--output-table", pj(cfg.DataPrepareDir, "nightly_data/nightly_urls_{}".format(sample_state))
    ).do(dry_run=cfg.DryRun)
    if client.exists(pj(cfg.YT_PREFIX, "delivery")):
        client.remove(pj(cfg.YT_PREFIX, "delivery"), recursive=True)
    client.copy(pj(nightly_sample_prefix, "delivery"), pj(cfg.YT_PREFIX, "delivery"))


def get_nightly_hosts(cfg):
    client = rt_util.get_yt_client(cfg)
    sample_state = rt_util.get_state(cfg, cfg.PROD_PREFIX, "sample", "current")
    nightly_sample_prefix = pj(cfg.PROD_PREFIX, "sample", sample_state, "nightly")
    if client.exists(pj(cfg.DataPrepareDir, "nightly_data/nightly_hosts_{}".format(sample_state))):
        client.remove(pj(cfg.DataPrepareDir, "nightly_data/nightly_hosts_{}".format(sample_state)))
    BinaryRun(
        pj(cfg.CmpyBin, "get_nightly_data"),
        "GetNightlyHosts",
        "--server-name", cfg.YT_PROXY,
        "--mr-prefix", nightly_sample_prefix,
        "--current-state", sample_state,
        "--buckets-count", 14,
        "--operation-weight", 10,
        "--output-table", pj(cfg.DataPrepareDir, "nightly_data/nightly_hosts_{}".format(sample_state))
    ).do(dry_run=cfg.DryRun)


def upload_isPlatinum_url_to_kiwi_main(cfg):
    sample_state = rt_util.get_state(cfg, cfg.PROD_PREFIX, "sample", "current")
    rt_util.upload_data_to_kiwi(
        cfg,
        "kiwi_main",
        pj(cfg.DataPrepareDir, "nightly_data/nightly_urls_{}".format(sample_state)),
        pj(cfg.DataPrepareDir, "nightly_data/{}_urls_upload_errors".format(sample_state)),
        6000,
        "fast")


def upload_isPlatinum_hosts_to_kiwi_main(cfg):
    sample_state = rt_util.get_state(cfg, cfg.PROD_PREFIX, "sample", "current")
    rt_util.upload_data_to_kiwi(
        cfg,
        "kiwi_main",
        pj(cfg.DataPrepareDir, "nightly_data/nightly_hosts_{}".format(sample_state)),
        pj(cfg.DataPrepareDir, "nightly_data/{}_hosts_upload_errors".format(sample_state)),
        6000,
        "fast")


def update_initial_data(cfg):
    return True


# END Graph to get urls/hosts from nightly and mark them as IsPlatinum on kiwi_main


# Graph to upload results of IsPlat exports to Apteryx

def init_update_apteryx_data(cfg):
    rt_util.clean_working_dir(cfg, pj(cfg.DataPrepareDir, "apteryx_upload"))


def merge_urls_IsPlat_export_tables(cfg):
    rt_util.merge_export_tables(
        cfg=cfg,
        input_dir=pj(cfg.KIWI_DATA_PATH, "platinum_doc_attrs/final"),
        regexp="IsPlatDocExport-[0-9].*",
        output=pj(cfg.DataPrepareDir, "apteryx_upload/IsPlatDocExportMerged"),
    )


def merge_hosts_IsPlat_export_tables(cfg):
    rt_util.merge_export_tables(
        cfg=cfg,
        input_dir=pj(cfg.KIWI_DATA_PATH, "platinum_host_attrs/final"),
        regexp="IsPlatHostExport-[0-9].*",
        output=pj(cfg.DataPrepareDir, "apteryx_upload/IsPlatHostExportMerged"),
    )


def clean_urls_table(cfg):
    BinaryRun(
        pj(cfg.CmpyBin, "clean_exports"),
        "CleanExports",
        "--server-name", cfg.YT_PROXY,
        "--input-table", pj(cfg.DataPrepareDir, "apteryx_upload/IsPlatDocExportMerged"),
        "--output-table", pj(cfg.DataPrepareDir, "apteryx_upload/IsPlatDocExportFinal"),
        "--tuples-type", "50"
    ).do(dry_run=cfg.DryRun)


def clean_hosts_table(cfg):
    BinaryRun(
        pj(cfg.CmpyBin, "clean_exports"),
        "CleanExports",
        "--server-name", cfg.YT_PROXY,
        "--input-table", pj(cfg.DataPrepareDir, "apteryx_upload/IsPlatHostExportMerged"),
        "--output-table", pj(cfg.DataPrepareDir, "apteryx_upload/IsPlatHostExportFinal"),
        "--tuples-type", "10"
    ).do(dry_run=cfg.DryRun)


def upload_urls_to_apteryx(cfg):
    rt_util.upload_data_to_kiwi(cfg, "kiwi_tokoeka", pj(cfg.DataPrepareDir, "apteryx_upload/IsPlatDocExportFinal"),
                                pj(cfg.DataPrepareDir, "apteryx_upload/urls_apteryx_upload_errors"), 100, "back")


def upload_hosts_to_apteryx(cfg):
    rt_util.upload_data_to_kiwi(cfg, "kiwi_tokoeka", pj(cfg.DataPrepareDir, "apteryx_upload/IsPlatHostExportFinal"),
                                pj(cfg.DataPrepareDir, "apteryx_upload/hosts_apteryx_upload_errors"), 200, "back")


def update_apteryx_data(cfg):
    return True


# END Graph to upload results of IsPlat exports to Apteryx


def cleanup_working_dir(cfg):
    rt_util.clean_working_dir(cfg, pj(cfg.DataPrepareDir, "exports_prepare/baseline"))
    rt_util.clean_working_dir(cfg, pj(cfg.DataPrepareDir, "exports_prepare/test"))


def merge_baseline_aspam_exports(cfg):
    rt_util.merge_export_tables(
        cfg=cfg,
        input_dir=pj(cfg.KIWI_DATA_PATH, "baseline/JupiterAspamExport/final"),
        regexp="JupiterAspamExportPlatinum-[0-9].*",
        output=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterAspamExportPlatinum_merged"),
    )


def merge_baseline_host_exports(cfg):
    rt_util.merge_export_tables(
        cfg=cfg,
        input_dir=pj(cfg.KIWI_DATA_PATH, "baseline/JupiterHostExport/final"),
        regexp="JupiterHostExportPlatinumRT",
        output=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterHostExportPlatinumRT_merged"),
    )


def merge_baseline_nocontent_exports(cfg):
    rt_util.merge_export_tables(
        cfg=cfg,
        input_dir=pj(cfg.KIWI_DATA_PATH, "baseline/JupiterNoContentExport/final"),
        regexp="JupiterNoContentExportPlatinumRT",
        output=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterNoContentExportPlatinumRT_merged"),
    )


def merge_baseline_content_exports(cfg):
    rt_util.merge_export_tables(
        cfg=cfg,
        input_dir=pj(cfg.KIWI_DATA_PATH, "baseline/JupiterContentExport/final"),
        regexp="JupiterContentExportPlatinumRT",
        output=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterContentExportPlatinumRT_merged"),
    )


def merge_test_aspam_exports(cfg):
    rt_util.merge_export_tables(
        cfg=cfg,
        input_dir=pj(cfg.KIWI_DATA_PATH, "test/JupiterAspamExport/final"),
        regexp="JupiterAspamExportPlatinum2-[0-9].*",
        output=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterAspamExportPlatinum2_merged"),
    )


def merge_test_host_exports(cfg):
    rt_util.merge_export_tables(
        cfg=cfg,
        input_dir=pj(cfg.KIWI_DATA_PATH, "test/JupiterHostExport/final"),
        regexp="JupiterHostExportPlatinumRT2",
        output=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterHostExportPlatinumRT2_merged"),
    )


def merge_test_nocontent_exports(cfg):
    rt_util.merge_export_tables(
        cfg=cfg,
        input_dir=pj(cfg.KIWI_DATA_PATH, "test/JupiterNoContentExport/final"),
        regexp="JupiterNoContentExportPlatinumRT2",
        output=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterNoContentExportPlatinumRT2_merged"),
    )


def merge_test_content_exports(cfg):
    rt_util.merge_export_tables(
        cfg=cfg,
        input_dir=pj(cfg.KIWI_DATA_PATH, "test/JupiterContentExport/final"),
        regexp="JupiterContentExportPlatinumRT2",
        output=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterContentExportPlatinumRT2_merged"),
    )


def get_urls_from_baseline_aspam_exports(cfg):
    rt_util.get_table_keys(
        cfg,
        input_table=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterAspamExportPlatinum_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterAspamExportPlatinum_urls")
    )


def get_hosts_from_baseline_host_exports(cfg):
    rt_util.get_table_keys(
        cfg,
        input_table=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterHostExportPlatinumRT_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterHostExportPlatinumRT_hosts")
    )


def get_urls_from_baseline_nocontent_exports(cfg):
    rt_util.get_table_keys(
        cfg,
        input_table=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterNoContentExportPlatinumRT_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterNoContentExportPlatinumRT_urls")
    )


def get_urls_from_baseline_content_exports(cfg):
    rt_util.get_table_keys(
        cfg,
        input_table=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterContentExportPlatinumRT_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterContentExportPlatinumRT_urls")
    )


def get_urls_from_test_aspam_exports(cfg):
    rt_util.get_table_keys(
        cfg,
        input_table=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterAspamExportPlatinum2_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterAspamExportPlatinum2_urls")
    )


def get_hosts_from_test_host_exports(cfg):
    rt_util.get_table_keys(
        cfg,
        input_table=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterHostExportPlatinumRT2_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterHostExportPlatinumRT2_hosts")
    )


def get_urls_from_test_nocontent_exports(cfg):
    rt_util.get_table_keys(
        cfg,
        input_table=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterNoContentExportPlatinumRT2_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterNoContentExportPlatinumRT2_urls")
    )


def get_urls_from_test_content_exports(cfg):
    rt_util.get_table_keys(
        cfg,
        input_table=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterContentExportPlatinumRT2_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterContentExportPlatinumRT2_urls")
    )


def intersect_aspam_urls(cfg):
    rt_util.intersect_tables(
        cfg,
        input_table0=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterAspamExportPlatinum_urls"),
        input_table1=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterAspamExportPlatinum2_urls"),
        output_tables=[
            pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterAspamExport_common_urls"),
            pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterAspamExport_common_urls")
        ]
    )


def intersect_hosts(cfg):
    rt_util.intersect_tables(
        cfg,
        input_table0=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterHostExportPlatinumRT_hosts"),
        input_table1=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterHostExportPlatinumRT2_hosts"),
        output_tables=[
            pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterHostExport_common_hosts"),
            pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterHostExport_common_hosts")
        ]
    )


def intersect_nocontent_urls(cfg):
    rt_util.intersect_tables(
        cfg,
        input_table0=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterNoContentExportPlatinumRT_urls"),
        input_table1=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterNoContentExportPlatinumRT2_urls"),
        output_tables=[
            pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterNoContentExport_common_urls"),
            pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterNoContentExport_common_urls")
        ]
    )


def intersect_content_urls(cfg):
    rt_util.intersect_tables(
        cfg,
        input_table0=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterContentExportPlatinumRT_urls"),
        input_table1=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterContentExportPlatinumRT2_urls"),
        output_tables=[
            pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterContentExport_common_urls"),
            pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterContentExport_common_urls")
        ]
    )


def get_final_baseline_aspam_data(cfg):
    rt_util.get_final_exports(
        cfg,
        input_table0=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterAspamExport_common_urls"),
        input_table1=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterAspamExportPlatinum_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterAspamExportPlatinum_final")
    )


def get_final_baseline_host_data(cfg):
    rt_util.get_final_exports(
        cfg,
        input_table0=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterHostExport_common_hosts"),
        input_table1=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterHostExportPlatinumRT_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterHostExportPlatinumRT_final")
    )


def get_final_baseline_nocontent_data(cfg):
    rt_util.get_final_exports(
        cfg,
        input_table0=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterNoContentExport_common_urls"),
        input_table1=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterNoContentExportPlatinumRT_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterNoContentExportPlatinumRT_final")
    )


def get_final_baseline_content_data(cfg):
    rt_util.get_final_exports(
        cfg,
        input_table0=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterContentExport_common_urls"),
        input_table1=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterContentExportPlatinumRT_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/baseline/JupiterContentExportPlatinumRT_final")
    )


def get_final_test_aspam_data(cfg):
    rt_util.get_final_exports(
        cfg,
        input_table0=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterAspamExport_common_urls"),
        input_table1=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterAspamExportPlatinum2_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterAspamExportPlatinum2_final")
    )


def get_final_test_host_data(cfg):
    rt_util.get_final_exports(
        cfg,
        input_table0=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterHostExport_common_hosts"),
        input_table1=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterHostExportPlatinumRT2_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterHostExportPlatinumRT2_final")
    )


def get_final_test_nocontent_data(cfg):
    rt_util.get_final_exports(
        cfg,
        input_table0=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterNoContentExport_common_urls"),
        input_table1=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterNoContentExportPlatinumRT2_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterNoContentExportPlatinumRT2_final")
    )


def get_final_test_content_data(cfg):
    rt_util.get_final_exports(
        cfg,
        input_table0=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterContentExport_common_urls"),
        input_table1=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterContentExportPlatinumRT2_merged"),
        output_table=pj(cfg.DataPrepareDir, "exports_prepare/test/JupiterContentExportPlatinumRT2_final")
    )


def prepare_kiwi_data_for_bases(cfg):
    return True


def update_z2_configuration(cfg):
    return True


def update_kiwi_triggers_jupiter_cm(cfg):
    cm_api = CmApi(server_address=cfg.CmAddress)
    cm_api.launch_target("deploy.finish", sync=True)


def copy_baseline_kiwi_data(cfg):
    client = rt_util.get_yt_client(cfg)
    for exp in [
            'JupiterHostExport',
            'JupiterNoContentExport',
            'JupiterContentExport'
    ]:
        client.copy(
            pj(cfg.DataPrepareDir, "exports_prepare/baseline/{0}PlatinumRT_final".format(exp)),
            pj(cfg.KIWI_DATA_PATH, "{0}/final/{0}_final".format(exp))
        )
    client.write_table(
        '<sorted_by=[key;]>' + pj(cfg.KIWI_DATA_PATH, "JupiterAspamExport/final/JupiterAspamExport_final"), [])


def run_baseline_spread(cfg):
    cm_api = CmApi(server_address=cfg.CmAddress)
    cm_api.launch_target("spread-finish", sync=True)


def run_baseline_base_build(cfg):
    rt_util.set_attr(cfg, cfg.YT_PREFIX, "@jupiter_meta/yandex_prev_state", "\"empty_state\"")
    rt_util.set_attr(cfg, cfg.YT_PREFIX, "@jupiter_meta/yandex_prev_prev_state", "\"empty_state\"")
    cm_api = CmApi(server_address=cfg.CmAddress)
    cm_api.launch_target("yandex.run.deploy", sync=True)


def finish_baseline_base_build(cfg):
    current_state = rt_util.get_state(cfg, cfg.YT_PREFIX, "yandex", "current")
    bundle_id = rt_util.get_attr(
        cfg,
        cfg.YT_PREFIX,
        pj("shards_prepare", current_state, "@jupiter_meta/bundle")
    )
    rt_util.set_attr(
        cfg,
        cfg.INDEX_DEPLOY_PREFIX,
        "kiwi_triggers_baseline/@deploy_params/jupiter_bundle_id",
        "\"{}\"".format(bundle_id)
    )
    rt_util.set_attr(
        cfg,
        cfg.INDEX_DEPLOY_PREFIX,
        "kiwi_triggers_baseline/@deploy_params/state",
        "\"{}\"".format(current_state)
    )
    rt_util.set_attr(
        cfg,
        cfg.YT_PREFIX,
        "@jupiter_meta/deploy_prev_state",
        "\"{}\"".format(current_state)
    )


def copy_test_kiwi_data(cfg):
    client = rt_util.get_yt_client(cfg)
    for exp in [
            'JupiterHostExport',
            'JupiterNoContentExport',
            'JupiterContentExport'
    ]:
        client.copy(
            pj(cfg.DataPrepareDir, "exports_prepare/test/{0}PlatinumRT2_final".format(exp)),
            pj(cfg.KIWI_DATA_PATH, "{0}/final/{0}_final".format(exp))
        )
    client.write_table(
        '<sorted_by=[key;]>' + pj(cfg.KIWI_DATA_PATH, "JupiterAspamExport/final/JupiterAspamExport_final"), [])


def run_test_spread(cfg):
    cm_api = CmApi(server_address=cfg.CmAddress)
    cm_api.launch_target("spread-finish", sync=True)


def prepare_test_base_build(cfg):
    rt_util.set_attr(cfg, cfg.YT_PREFIX, "@jupiter_meta/yandex_prev_state", "\"empty_state\"")
    rt_util.set_attr(cfg, cfg.YT_PREFIX, "@jupiter_meta/yandex_prev_prev_state", "\"empty_state\"")


def run_test_base_build(cfg):
    cm_api = CmApi(server_address=cfg.CmAddress)
    cm_api.launch_target("yandex.run.deploy", sync=True)


def finish_test_base_build(cfg):
    current_state = rt_util.get_state(cfg, cfg.YT_PREFIX, "yandex", "current")
    bundle_id = rt_util.get_attr(
        cfg,
        cfg.YT_PREFIX,
        pj("shards_prepare", current_state, "@jupiter_meta/bundle")
    )
    rt_util.set_attr(
        cfg,
        cfg.INDEX_DEPLOY_PREFIX,
        "kiwi_triggers_test/@deploy_params/jupiter_bundle_id",
        "\"{}\"".format(bundle_id)
    )
    rt_util.set_attr(
        cfg,
        cfg.INDEX_DEPLOY_PREFIX,
        "kiwi_triggers_test/@deploy_params/state",
        "\"{}\"".format(current_state)
    )
    rt_util.set_attr(
        cfg,
        cfg.YT_PREFIX,
        "test_beta/@jupiter_meta/deploy_current_state",
        "\"{}\"".format(current_state)
    )


def build_bases(cfg):
    return True


def run_fml_task(cfg):
    cm_api = CmApi(server_address=cfg.CmAddress)
    cm_api.launch_target("quality-acceptance-finish", sync=True)
# END CM Targets
