import pathlib

import pytest

from taxi_testsuite.plugins.databases.yt import discover


_YT_SCHEMAS = pathlib.Path(__file__).parent.joinpath('schemas')


@pytest.fixture(scope='session')
def yt_service_schemas():
    return discover.find_schemas([_YT_SCHEMAS])
