import pytest

import metrika.pylib.state as mstate


@pytest.fixture
def base_state():
    return mstate.BaseState()


@pytest.fixture(scope='session')
def temp_dir(tmpdir_factory):
    yield str(tmpdir_factory.mktemp("temp_dir", numbered=False))
