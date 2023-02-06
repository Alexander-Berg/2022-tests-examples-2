#!/usr/bin/env python

from robot.cmpy.library.run import BinaryRun
from robot.cmpy.library.utils import read_token_from_file
from robot.library.python.sandbox.client import SandboxClient

from os.path import join as pj
from os import environ as env
import yt.wrapper as yt
import logging
import os
import fileinput
import re
import json

# Various util functions


def get_yt_client(cfg):
    client = yt.client.YtClient(
        proxy=cfg.YT_PROXY,
        config={
            'pickling': {
                'module_filter': lambda module: 'hashlib' not in getattr(module, '__name__', '')
            },
            'token_path': '{}'.format(cfg.YT_TOKEN_PATH)
        }
    )
    return client


def clean_working_dir(cfg, path):
    client = get_yt_client(cfg)
    if client.exists(path):
        work_dir_list = client.list(path, absolute=True)
        if len(work_dir_list) > 0:
            for t in work_dir_list:
                client.remove(t)


def get_state(cfg, prefix, state_name, state_type):
    state = BinaryRun(
        pj(cfg.BinDir, "attrstool"),
        "GetState",
        "--server-name", cfg.YT_PROXY,
        "--prefix", prefix,
        "--state-name", state_name,
        "--state-type", state_type,
    ).do(return_result=True, dry_run=cfg.DryRun)
    return state.stdout


def set_state(cfg, prefix, state_name, state_type, value):
    BinaryRun(
        pj(cfg.BinDir, "attrstool"),
        "SetState",
        "--server-name", cfg.YT_PROXY,
        "--prefix", prefix,
        "--state-name", state_name,
        "--state-type", state_type,
        "--value", value,
    ).do(dry_run=cfg.DryRun)


def set_attr(cfg, prefix, attr_path, value):
    BinaryRun(
        pj(cfg.BinDir, "attrstool"),
        "SetAttr",
        "--server-name", cfg.YT_PROXY,
        "--prefix", prefix,
        "--path", attr_path,
        "--attr-value", value
    ).do(dry_run=cfg.DryRun)


def get_attr(cfg, prefix, attr_path):
    return BinaryRun(
        pj(cfg.BinDir, "attrstool"),
        "GetAttr",
        "--server-name", cfg.YT_PROXY,
        "--prefix", prefix,
        "--path", attr_path,
    ).do(return_result=True, dry_run=cfg.DryRun)


def get_last_delivery_snapshot(cfg):
    client = get_yt_client(cfg)
    snapshots = client.list(pj(cfg.YT_PREFIX, "delivery_snapshot"))
    if len(snapshots) > 1:
        logging.warning("There are %s snapshots. Getting the last one...", len(snapshots))
    return snapshots[-1]


def upload_data_to_kiwi(cfg, kiwi_cluster, input_table, errors_table, kwworm_rate, balance):
    BinaryRun(
        pj(cfg.JupiterScriptsDir, "upload_to_kiwi.py"),
        "--token-path", cfg.YT_TOKEN_PATH,
        "--src-cluster", cfg.YT_PROXY,
        "--input-table", input_table,
        "--dst-cluster", kiwi_cluster,
        "--kiwi-user", "zalivator",
        "--errors-table-path", errors_table,
        "--kwworm-rate", kwworm_rate,
        "--balance", balance
    ).do(dry_run=cfg.DryRun)


def merge_export_tables(cfg, input_dir, regexp, output):
    logging.info("Token path: %s", env['YT_TOKEN_PATH'])
    BinaryRun(
        pj(cfg.JupiterScriptsDir, "merge_export_tables.py"),
        "--proxy", cfg.YT_PROXY,
        "--input-dir", input_dir,
        "--regexp", regexp,
        "--output", output,
        #            "--delete"
    ).do(dry_run=cfg.DryRun)


def get_keys_reduce(key, values):
    yield key


def get_table_keys(cfg, input_table, output_table):
    client = get_yt_client(cfg)

    if client.exists(input_table):
        client.run_sort(
            input_table,
            sort_by=['key'],
            spec={"pool": "jupiter-test"}
        )

        client.run_reduce(
            get_keys_reduce,
            input_table,
            output_table,
            reduce_by=['key'],
            spec={"pool": "jupiter-test"}
        )


def intersect_reduce(key, rows):
    hasLeft = False
    hasRight = False
    row = None
    for r in rows:
        if r["@table_index"] == 0:
            row = r
            hasLeft = True
        elif r["@table_index"] == 1:
            row = r
            hasRight = True
    if hasLeft and hasRight:
        row["@table_index"] = 0
        yield row


def final_intersect_reduce(key, rows):
    hasLeft = False
    hasRight = False
    final_rows = []
    for r in rows:
        if r["@table_index"] == 0:
            hasLeft = True
        elif r["@table_index"] == 1:
            final_rows.append(r)
            hasRight = True
    if hasLeft and hasRight:
        for row in final_rows:
            row["@table_index"] = 0
            yield row


def intersect_tables(cfg, input_table0, input_table1, output_tables):
    client = get_yt_client(cfg)
    client.run_sort(
        input_table0,
        sort_by=['key'],
        spec={"pool": "jupiter-test"})

    client.run_sort(
        input_table1,
        sort_by=['key'],
        spec={"pool": "jupiter-test"})

    client.run_reduce(
        intersect_reduce,
        source_table=[
            input_table0,
            input_table1
        ],
        destination_table=output_tables[0],
        reduce_by=['key'],
        spec={"pool": "jupiter-test"},
        format=yt.YsonFormat(control_attributes_mode="row_fields")
    )
    for tbl in output_tables[1:len(output_tables)]:
        client.copy(
            output_tables[0],
            tbl
        )


def get_final_exports(cfg, input_table0, input_table1, output_table):
    client = get_yt_client(cfg)

    client.run_sort(
        input_table0,
        sort_by=['key'],
        spec={"pool": "jupiter-test"})

    client.run_reduce(
        final_intersect_reduce,
        source_table=[
            input_table0,
            input_table1
        ],
        destination_table=output_table,
        reduce_by=['key'],
        spec={"pool": "jupiter-test"},
        format=yt.YsonFormat(control_attributes_mode="row_fields")
    )


def prepare_test_exports(cfg, path_to_package):
    for exp in cfg.TestExports:
        for entry in os.listdir(pj(path_to_package, exp)):
            f = fileinput.FileInput(pj(path_to_package, exp, entry), inplace=True)
            for line in f:
                if 'baseline' in line:
                    line = re.sub(r'baseline', 'test', line)
                if 'PlatinumRTSubscriber' in line:
                    line = re.sub(r'PlatinumRTSubscriber', 'PlatinumRTSubscriber2', line)
                if 'ExportPlatinumRT' in line:
                    line = re.sub(r'ExportPlatinumRT', 'ExportPlatinumRT2', line)
                if 'LastJupiterHostLastAccess' in line:
                    line = re.sub(r'LastJupiterHostLastAccess', 'LastJupiterHostLastAccess2', line)
                if 'LastJupiterHttpResponseTimestamp' in line:
                    line = re.sub(r'LastJupiterHttpResponseTimestamp', 'LastJupiterHttpResponseTimestamp2', line)
                if 'JupiterAspamLastExportedRev1' in line:
                    line = re.sub(r'JupiterAspamLastExportedRev1', 'JupiterAspamLastExportedRev2', line)

                print line,
            f.close()


def build_triggers(cfg, arcadia_path, kiwi_branch, build_task_id_file, target_path):
    arc_path = pj(arcadia_path, kiwi_branch, "arcadia")
    sandbox = SandboxClient(token=read_token_from_file(cfg.SandboxTokenPath))
    task_id_request = sandbox.run_task(
        name="BUILD_KIWI_TRIGGERS",
        params=json.dumps({
            "build_triggers_arcadia_url": "arcadia:" + arc_path,
            "build_type": "release",
            "targets_str": target_path,
            "task_mode": "use_ya_impl"}),
        descr="Build Release robot triggers from " + kiwi_branch,
        wait_success=True,
        owner="KWYT",
    )
    with open(build_task_id_file, "w") as build_task_id:
        build_task_id.write(task_id_request.stdout.strip("\n"))

# END Various util functions
