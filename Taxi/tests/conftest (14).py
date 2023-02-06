import os

import pytest


@pytest.fixture(scope='session')
def inside_ci() -> bool:
    return bool(os.environ.get('IS_TEAMCITY'))
