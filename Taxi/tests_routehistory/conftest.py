# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bson import json_util
import pytest
from routehistory_plugins import *  # noqa: F403 F401


@pytest.fixture(name='tz_hook')
def _tz_hook():
    def hook(dct):
        return json_util.object_hook(
            dct, json_options=json_util.JSONOptions(tz_aware=False),
        )

    return hook


class RoutehistoryInternal:
    def __init__(self, taxi_routehistory):
        self.routehistory = taxi_routehistory

    async def _call(self, op_name, *args):
        return await self.routehistory.post(
            '/routehistory/internal-control',
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
def routehistory_internal(taxi_routehistory):
    return RoutehistoryInternal(taxi_routehistory)
