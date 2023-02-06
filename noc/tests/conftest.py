import glob
import inspect
import os
import sys
import typing

import pytest
import yaml


def dataglob(globstr: str) -> typing.Iterator[str]:
    testdir = curdir()
    globpath = os.path.join(testdir, globstr)
    found = False
    for fname in glob.glob(globpath):
        yield os.path.relpath(fname, testdir)
        found = True
    if not found:
        pytest.fail(f"Not found files in {globpath}")


def dataparse(fname: str) -> typing.Dict[str, typing.Any]:
    testdir = curdir()
    with open(os.path.join(testdir, fname)) as fh:
        return yaml.load(fh, Loader=yaml.BaseLoader)


def curdir() -> str:
    try:
        import yatest.common
        return yatest.common.test_source_path()
    except ModuleNotFoundError:
        pass
    return os.path.dirname(inspect.getfile(sys.modules[__name__]))


def strip(result: typing.Union[str, typing.Dict]):
    if isinstance(result, str):
        result = result.strip()
    return result
