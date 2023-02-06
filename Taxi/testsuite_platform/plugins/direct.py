import pathlib

import pytest


@pytest.fixture(scope='session')
def logistic_platform_dir(pytestconfig):
    return pathlib.Path(pytestconfig.rootdir).parent


@pytest.fixture(scope='session')
def logistic_platform_binary(logistic_platform_dir):
    return str(logistic_platform_dir.joinpath('dispatcher/dispatcher'))


@pytest.fixture(scope='session')
def is_arcadia():
    return False
