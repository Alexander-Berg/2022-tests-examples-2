# coding: utf-8

import os
import cyson
import subprocess

from connection.yt import get_yt_cluster_token, get_yt_cluster_proxy


aliases = {
    "mkdir": "create map_node",
    "remount": "remount-table",
}


def yt(argv):
    """Utilities for working with YT system."""

    if len(argv) > 0 and argv[0] in aliases:
        argv = aliases[argv[0]].split() + list(argv[1:])

    config = {
        "read_parallel": {
            "max_thread_count": 32,
            "data_size_per_thread": 32 * 1024 * 1024
        }
    }

    subprocess.call(
        ["yt"] + list(argv) + ["--params", cyson.dumps(config)],
        env=dict(
            os.environ.copy(),
            YT_PROXY=get_yt_cluster_proxy(),
            YT_TOKEN=get_yt_cluster_token(),
        )
    )


if __name__ == '__main__':
    subprocess.call(["which", "yt"])
    yt(["list", "//home/taxi-dwh-dev"])
