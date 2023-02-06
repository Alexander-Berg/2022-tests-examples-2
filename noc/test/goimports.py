import difflib
import logging
import os
from typing import Any

import pytest
import yatest.common

ya_bin = yatest.common.binary_path('devtools/ya/bin/ya-bin')


def find_files(path: str, endswith: tuple[str]) -> list[str]:
    res = []
    for root, _, files in os.walk(path):
        for name in files:
            fpath = os.path.join(root, name)
            rel_path = os.path.relpath(fpath, start=path)
            if not rel_path.endswith(endswith):
                continue
            if os.path.isfile(fpath) and os.access(fpath, os.R_OK):
                res.append(fpath)
    res.sort()
    return res


def diff(before: str, after: str) -> str:
    res = []
    for line in difflib.context_diff(before.splitlines(), after.splitlines()):
        res.append(line)
    return "\n".join(res)


def get_goimports_diff(files: list[str]) -> str:
    res = ""
    logging.error("start ya")
    cmd_res = yatest.common.execute([ya_bin, "--precise", "-v", "--no-report", "tool", "yoimports", *files],
                                    cwd=yatest.common.source_path())
    logging.error("done ya")
    if cmd_res.std_out:
        res = "\n".join(cmd_res.std_out.decode().splitlines()[2:])
    return res


def chunks_tuple(in_list: list[Any], n: int) -> list[Any]:
    return [tuple(in_list[i:i + n]) for i in range(0, len(in_list), n)]


def test_goimports():
    files = find_files(os.path.join(yatest.common.source_path(), "noc/metridat"), (".go",))
    files = files[:2]
    logging.error("run %s", files)
    for chunk in chunks_tuple(files, 50):
        data = get_goimports_diff(chunk)
        if data:
            pytest.fail("goimports diff:%s\n" % data)
    logging.error("done yoimports")
