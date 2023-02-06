import os
import shutil
import subprocess
import yatest.common

from library.python.monlib import encoder as lmee
from library.python import func, json, tskv

import metrika.pylib.clickhouse as mtch


def run_proc(args):
    proc = subprocess.Popen(args, shell=False)
    try:
        proc.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        proc.terminate()
        proc.communicate(timeout=30)

    if proc.returncode != 0:
        raise Exception("command %s returns %d code" % (str(args), proc.returncode))


def ch_output(directories, mtmobproxy_columns, tab_crunch):
    canon_args = tab_crunch + [
        "--columns", mtmobproxy_columns.columns,
        "--group-columns", mtmobproxy_columns.group_columns,
        "--filter-out-columns", mtmobproxy_columns.filter_out_columns,
        "--file-format", "tsv",
    ]

    out_dir = directories.sender_base_dir
    canon_dir = directories.canon_dir
    res = {}
    for i, f_name in enumerate(sorted(os.listdir(out_dir))):
        old_name = os.path.join(out_dir, f_name)
        new_name = os.path.join(canon_dir, str(i))
        if os.path.isfile(old_name):
            print("Copy %s to %s" % (old_name, new_name))
            shutil.copy(old_name, new_name)
            report_name = "ch_output_" + str(i)
            res[report_name] = yatest.common.canonical_file(
                new_name,
                diff_tool=canon_args + ["--output", os.path.join(directories.report_dir, "%s.html" % report_name)],
            )

    return res


def solomon_output(directories):
    out_dir = directories.solomon_base_dir
    canon_dir = directories.canon_dir
    res = {}
    for i, f_name in enumerate(sorted(os.listdir(out_dir))):
        old_name = os.path.join(out_dir, f_name)
        new_name = os.path.join(canon_dir, "solomon_" + str(i))
        if os.path.isfile(old_name):
            with open(old_name) as f:
                d = json.loads(lmee.load(f))

            sensors = [func.flatten_dict(x) for x in d['sensors']]
            tskv_data = sorted([tskv.dumps({k: str(v) for k, v in x.items()}) for x in sensors])
            with open(new_name, 'w') as f:
                for line in tskv_data:
                    f.write(line)
                    f.write("\n")

            report_name = "solomon_output_" + str(i)
            res[report_name] = yatest.common.canonical_file(new_name)

    return res


def ch_data(directories, columns, tab_crunch, clickhouse_client, table):
    canon_args = tab_crunch + [
        "--columns", columns.columns,
        # "--columns", columns.select_columns, TODO: use this
        "--group-columns", columns.group_columns,
        "--filter-out-columns", columns.filter_out_columns,
        "--file-format", "tsv",
    ]

    query = mtch.Query("SELECT %s from %s ORDER BY %s FORMAT TSV" % (columns.select_columns, table, columns.order_by_columns))
    data = clickhouse_client.execute(query)

    ch_data_file = os.path.join(directories.canon_dir, "ch_data")
    with open(ch_data_file, "w") as f:
        for line in data.data:
            f.write(line)

    res = {
        "ch_data": yatest.common.canonical_file(
            ch_data_file,
            diff_tool=canon_args + ["--output", os.path.join(directories.report_dir, "ch_data.html")],
        ),
    }

    return res


class TestSimpleMtmobproxy:

    @staticmethod
    def run_parser():
        os.environ["LOG_PATH"] = str(yatest.common.build_path("metrika/admin/python/logpusher/tests/data/mtmobproxy.log"))

        args = [
            str(yatest.common.build_path("metrika/admin/python/logpusher/bin/parser/logpusher-parser")),
            "-l", "DEBUG",
            "--stdout",
            "-c", str(yatest.common.build_path("metrika/admin/python/logpusher/tests/data/mtmobproxy_simple.yaml")),
        ]

        run_proc(args)

    @staticmethod
    def run_sender():
        args = [
            str(yatest.common.build_path("metrika/admin/python/logpusher/bin/sender/logpusher-sender")),
            "-l", "DEBUG",
            "--stdout",
            "-c", str(yatest.common.build_path("metrika/admin/python/logpusher/tests/data/mtmobproxy_simple.yaml")),
        ]

        run_proc(args)

    @staticmethod
    def test(mtmobproxy_simple_directories, links, mtmobproxy_columns, tab_crunch, clickhouse_client):
        res = {}
        TestSimpleMtmobproxy.run_parser()
        res.update(ch_output(mtmobproxy_simple_directories, mtmobproxy_columns, tab_crunch))
        res.update(solomon_output(mtmobproxy_simple_directories))

        TestSimpleMtmobproxy.run_sender()
        res.update(ch_data(mtmobproxy_simple_directories, mtmobproxy_columns, tab_crunch, clickhouse_client, "mtmobproxy.logs_weekly"))

        links.set("diff report", mtmobproxy_simple_directories.report_dir)

        return res


class TestSimpleQloud:

    @staticmethod
    def run_parser():
        args = [
            str(yatest.common.build_path("metrika/admin/python/logpusher/bin/parser/logpusher-parser")),
            "-l", "DEBUG",
            "--stdout",
            "-c", str(yatest.common.build_path("metrika/admin/python/logpusher/tests/data/qloud_simple.yaml")),
        ]

        run_proc(args)

    @staticmethod
    def run_sender():
        args = [
            str(yatest.common.build_path("metrika/admin/python/logpusher/bin/sender/logpusher-sender")),
            "-l", "DEBUG",
            "--stdout",
            "-c", str(yatest.common.build_path("metrika/admin/python/logpusher/tests/data/qloud_simple.yaml")),
        ]

        run_proc(args)

    @staticmethod
    def test(qloud_simple_directories, links, qloud_columns, tab_crunch, clickhouse_client, logbroker_qloud_data):
        res = {}
        TestSimpleQloud.run_parser()
        res.update(ch_output(qloud_simple_directories, qloud_columns, tab_crunch))
        res.update(solomon_output(qloud_simple_directories))

        TestSimpleQloud.run_sender()
        res.update(ch_data(qloud_simple_directories, qloud_columns, tab_crunch, clickhouse_client, "qloud.logs_weekly"))

        links.set("diff report", qloud_simple_directories.report_dir)

        return res
