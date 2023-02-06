import pytest

import abt.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from test_abt.helpers import builders
from test_abt.helpers import chyt
from test_abt.helpers import facade
from test_abt.helpers import state


pytest_plugins = ['abt.generated.service.pytest_plugins']


@pytest.fixture
async def set_configs(taxi_config):
    async def _wrapper(**kwargs):
        taxi_config.set_values(kwargs)

    return _wrapper


@pytest.fixture(name='abt')
async def abt_fixture(web_context):
    class Ctx:
        def __init__(self, context):
            self.pg = facade.PgFacade(context)  # pylint: disable=invalid-name
            self.builders = builders.Builders()
            self.state = state.StateHelper(self.pg, self.builders)

    return Ctx(web_context)


@pytest.fixture()
def chyt_clients_mock():
    return chyt.ChytClientsMock()
