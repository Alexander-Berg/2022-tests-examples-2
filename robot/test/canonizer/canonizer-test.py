#!/usr/bin/env python

from os.path import join as pj

from robot.jupiter.test.common import launch_local_jupiter
from robot.library.yuppie.modules.cmd import Cmd
import yatest.common
from robot.library.yuppie.modules.environment import Environment


def _get_production_state(yt):
    return yt.get("//home/jupiter/@jupiter_meta/production_current_state")


def test_canonizer():
    env = Environment()
    with launch_local_jupiter(
        env,
        test_data="canonizer_test_data.tar.gz",
        no_cm=True
    ) as lj:
        yt = lj.get_yt()
        canonizer_dir = "//home/canonizer"
        Cmd([
            yatest.common.binary_path("robot/jupiter/tools/canonizer/canonizer"),
            "--server-name", yt.get_proxy(),
            "--mr-prefix", env.mr_prefix,
            "--current-state", _get_production_state(yt),
            "--buckets-count", "2",
            "--input-table", "//home/jupiter/input",
            "--input-columns", "Host,Path",
            "--output", canonizer_dir,
            "--fill-shards"
        ])

        return yatest.common.canonical_file(
            lj.get_yt().download(pj(canonizer_dir, "canonized"), env.table_dumps_dir, yt_format="dsv"))


def test_mirror_and_rfl_canonizer():
    env = Environment()
    with launch_local_jupiter(
            env,
            test_data="canonizer_test_data.tar.gz",
            no_cm=True
    ) as lj:
        yt = lj.get_yt()
        canonizer_dir = "//home/canonizer"
        Cmd([
            yatest.common.binary_path("robot/jupiter/tools/canonizer/canonizer"),
            "--server-name", yt.get_proxy(),
            "--mr-prefix", env.mr_prefix,
            "--current-state", _get_production_state(yt),
            "--buckets-count", "2",
            "--input-table", "//home/jupiter/input",
            "--input-columns", "Host,Path",
            "--output", canonizer_dir,
            "--select-one",
            "--first-canonization", "mirror_and_rfl"
        ])

        return yatest.common.canonical_file(
            lj.get_yt().download(pj(canonizer_dir, "canonized"), env.table_dumps_dir, yt_format="dsv"))


def test_canonizer_snapshot():
    env = Environment()
    with launch_local_jupiter(
        env,
        test_data="canonizer_test_data.tar.gz",
        no_cm=True
    ) as lj:
        yt = lj.get_yt()
        snapshot_dir = "//home/snapshot"
        canonizer_dir = "//home/canonizer"
        Cmd([
            yatest.common.binary_path("robot/jupiter/tools/canonizer/canonizer"),
            "--server-name", yt.get_proxy(),
            "--mr-prefix", env.mr_prefix,
            "--current-state", _get_production_state(yt),
            "--buckets-count", "2",
            "--input-table", "//home/jupiter/input",
            "--input-columns", "Host,Path",
            "--output", snapshot_dir,
            "--make-snapshot"
        ])
        Cmd([
            yatest.common.binary_path("robot/jupiter/tools/canonizer/canonizer"),
            "--server-name", yt.get_proxy(),
            "--use-snapshot", snapshot_dir,
            "--input-table", "//home/jupiter/input",
            "--input-columns", "Host,Path",
            "--output", canonizer_dir,
            "--fill-shards"
        ])

        return yatest.common.canonical_file(
            lj.get_yt().download(pj(canonizer_dir, "canonized"), env.table_dumps_dir, yt_format="dsv"))


def test_canonizer_full_snapshot():
    env = Environment()
    with launch_local_jupiter(
        env,
        test_data="canonizer_test_data.tar.gz",
        no_cm=True,
    ) as lj:
        yt = lj.get_yt()
        snapshot_dir = "//home/snapshot"
        canonizer_dir = "//home/canonizer"
        Cmd([
            yatest.common.binary_path("robot/jupiter/tools/canonizer/canonizer"),
            "--server-name", yt.get_proxy(),
            "--mr-prefix", env.mr_prefix,
            "--current-state", _get_production_state(yt),
            "--buckets-count", "2",
            "--output", snapshot_dir,
            "--make-full-snapshot"
        ])
        Cmd([
            yatest.common.binary_path("robot/jupiter/tools/canonizer/canonizer"),
            "--server-name", yt.get_proxy(),
            "--use-snapshot", snapshot_dir,
            "--input-table", "//home/jupiter/input",
            "--input-columns", "Host,Path",
            "--output", canonizer_dir,
            "--fill-shards"
        ])

        return yatest.common.canonical_file(
            lj.get_yt().download(pj(canonizer_dir, "canonized"), env.table_dumps_dir, yt_format="dsv"))
