import pathlib

import pytest


@pytest.fixture(scope='session')
def logistic_dispatcher_dir(pytestconfig):
    return pathlib.Path(pytestconfig.rootdir).parent


@pytest.fixture(scope='session')
def logistic_dispatcher_binary(logistic_dispatcher_dir):
    return str(logistic_dispatcher_dir.joinpath('dispatcher/dispatcher'))


@pytest.fixture(scope='session')
def is_arcadia():
    return False
