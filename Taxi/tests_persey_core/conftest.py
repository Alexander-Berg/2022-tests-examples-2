# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from persey_core_plugins import *  # noqa: F403 F401
import pytest


class RoutehistoryInternal:
    def __init__(self, taxi_persey_core):
        self.taxi_persey_core = taxi_persey_core

    async def _call(self, op_name, *args):
        return await self.taxi_persey_core.post(
            '/persey-core/internal-control',
            {'op': op_name, 'args': args},
            headers={'X-Token': 'test'},
        )

    async def call(self, op_name, *args):
        result = await self._call(op_name, *args)
        assert result.status_code == 200
        return result.json()

    async def call_exc(self, op_name, *args):
        result = await self._call(op_name, *args)
        assert result.status_code == 500
        return result.json()['message']


@pytest.fixture
def persey_core_internal(taxi_persey_core):
    return RoutehistoryInternal(taxi_persey_core)
