import pathlib

import pytest

import yatest.common


@pytest.fixture
def static_dir(request):
    # TODO: fix me
    return pathlib.Path(
        yatest.common.source_path(
            'taxi/logistic-dispatcher/testsuite_platform/static/',
        ),
    )


@pytest.fixture(scope='session')
def logistic_platform_dir():
    return pathlib.Path(yatest.common.source_path('taxi/logistic-dispatcher'))


@pytest.fixture(scope='session')
def logistic_platform_binary():
    return yatest.common.binary_path(
        'taxi/logistic-dispatcher/dispatcher/dispatcher',
    )


@pytest.fixture(scope='session')
def is_arcadia():
    return True
