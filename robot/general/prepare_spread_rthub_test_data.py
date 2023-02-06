#!/usr/bin/env python

import argparse
import os
import shutil
import tempfile
import yt.wrapper as yt
import tarfile

from os.path import join as pj
from yt.wrapper import ypath_join as ypj


DIRS = [
    ["kiwi_export"],
    ["kiwi_export", "rthub"],
    ["kiwi_export", "rthub", "hosts"],
    ["shuffler_export"]
]
SHUFFLER_EXPORT_JUPITER_PATH = ["shuffler_export"]
KIWI_EXPORT_HOSTS_PATH = ["kiwi_export", "rthub", "hosts"]


def collect_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proxy", default="arnold")
    parser.add_argument("--prefix", default="//home/jupiter/")
    parser.add_argument("--tables-limit", type=int, default=5)
    parser.add_argument("--rows-limit", type=int, default=300,
                        help="maximum number of rows per table")
    parser.add_argument("--yt-token-file", type=argparse.FileType())

    return parser.parse_args()


def create_yt_client(args):
    token = None

    if args.yt_token_file:
        token = args.yt_token_file.readline().strip()
        args.yt_token_file.close()
    else:
        token = os.getenv("YT_TOKEN", "")

    return yt.YtClient(proxy=args.proxy, config={
        "token": token
    })


def cleanup(temp_dir):
    shutil.rmtree(temp_dir)


def prepare_dirs():
    temp_dir = tempfile.mkdtemp()
    try:
        for path in DIRS:
            os.mkdir(pj(*([temp_dir] + path)))
    except:
        cleanup(temp_dir)
        raise
    return temp_dir


def sample_tables(client, local_path, yt_path, tables_limit, rows_limit):
    print(yt_path)
    tables = client.list(yt_path, sort=True)[-tables_limit:]
    for table in tables:
        with open(pj(local_path, table), 'w') as f:
            yt_table_path = yt.TablePath(yt_path.join(table), end_index=rows_limit)
            f.write(client.read_table(yt_table_path,
                                      format=yt.YsonFormat(),
                                      raw=True).read())


def archive(path):
    with tarfile.open("spread_rthub.tar", "w:gz") as tar:
        for filename in os.listdir(path):
            tar.add(pj(path, filename), arcname=filename)


def main():
    args = collect_args()
    client = create_yt_client(args)
    yt_prefix = yt.YPath(args.prefix.rstrip("/"))
    temp_dir = prepare_dirs()
    try:
        sample_tables(
            client,
            pj(*([temp_dir] + KIWI_EXPORT_HOSTS_PATH)),
            yt_prefix.join(ypj(*KIWI_EXPORT_HOSTS_PATH)),
            args.tables_limit,
            args.rows_limit)
        sample_tables(
            client,
            pj(*([temp_dir] + SHUFFLER_EXPORT_JUPITER_PATH)),
            yt_prefix.join(ypj(*SHUFFLER_EXPORT_JUPITER_PATH)),
            args.tables_limit,
            args.rows_limit)
        archive(temp_dir)
    finally:
        cleanup(temp_dir)


if "__main__" == __name__:
    main()
