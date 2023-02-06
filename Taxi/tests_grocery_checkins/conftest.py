# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import asyncio
import json

import pytest

from grocery_checkins_plugins import *  # noqa: F403 F401

from tests_grocery_checkins import const


@pytest.fixture(name='add_depots', autouse=True)
async def add_depots(grocery_depots):
    grocery_depots.add_depot(
        depot_test_id=int(const.DEPOT_ID),
        region_id=const.REGION_ID,
        auto_add_zone=False,
    )


@pytest.fixture(name='published_events')
async def _published_events(testpoint):
    """Wait and return events published to logbroker."""

    @testpoint('logbroker_publish')
    def publish_event(request):
        pass

    class Events:
        async def _wait_next(self):
            request = (await publish_event.wait_call())['request']
            return request['name'], json.loads(request['data'])

        async def _wait(self, alias=None):
            while True:
                event_alias, event = await self._wait_next()
                if alias is None or event_alias == alias:
                    return event_alias, event

        async def wait(self, alias=None, timeout=5):
            return await asyncio.wait_for(self._wait(alias), timeout)

    return Events()
