# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
import asyncio
import json

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from grocery_dispatch_plugins import *  # noqa: F403 F401

from tests_grocery_dispatch import constants as const


@pytest.fixture(name='add_depots', autouse=True)
async def add_depots(grocery_depots):
    grocery_depots.add_depot(
        depot_test_id=int(const.DEPOT_ID), auto_add_zone=False,
    )


@pytest.fixture(name='yamaps_local', autouse=True)
def mock_yamaps_local(mockserver, load_json, yamaps):
    class Context:
        def __init__(self):
            self.uri = None
            self.location = None
            self.lang = None
            self.country = None
            self.city = None
            self.street = None
            self.house = None
            self.text_addr = None
            self.place_id = None

        def set_data(
                self,
                uri=None,
                location=None,
                country=None,
                city=None,
                street=None,
                house=None,
                text_addr=None,
                place_id=None,
                lang=None,
        ):
            if uri is not None:
                self.uri = uri
            if location is not None:
                self.location = location
            if country is not None:
                self.country = country
            if city is not None:
                self.city = city
            if street is not None:
                self.street = street
            if house is not None:
                self.house = house
            if text_addr is not None:
                self.text_addr = text_addr
            if place_id is not None:
                self.place_id = place_id
            if lang is not None:
                self.lang = lang

        def create_geo_object(self):
            geo_object = load_json('geocoder-response.json')
            addr = geo_object['geocoder']['address']
            if self.country is not None:
                addr['country'] = self.country
            if self.city is not None:
                addr['locality'] = self.city
            if self.street is not None:
                addr['street'] = self.street
            if self.house is not None:
                addr['house'] = self.house
            if self.place_id is not None:
                geo_object['uri'] = self.place_id
            if self.location:
                geo_object['geometry'] = [
                    float(value) for value in self.location.split(',')
                ]
            return geo_object

        def times_called(self):
            return yamaps.times_called()

    context = Context()

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        if context.uri:
            assert request.args['uri'] == context.uri
        if context.location:
            if 'ull' in request.args:
                assert request.args['ull'] == context.location
            elif 'll' in request.args:
                assert request.args['ll'] == context.location
            else:
                assert False  # no coordinates in response
        if context.text_addr:
            assert request.args['text'] == context.text_addr
        if context.lang:
            assert request.args['lang'] == context.lang
        return [context.create_geo_object()]

    return context


@pytest.fixture(name='test_dummy_dispatch_cfg')
def _test_dummy_dispatch_cfg(experiments3):
    experiments3.add_config(
        consumers=['grocery_dispatch/dispatch'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='grocery_dispatch_priority',
        default_value={'dispatches': ['test']},
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
            skipped_events = []
            while True:
                event_alias, event = await self._wait_next()
                if alias is None or event_alias == alias:
                    return event_alias, event, skipped_events
                skipped_events.append((event_alias, event))

        async def wait(self, alias=None, timeout=5):
            return (await asyncio.wait_for(self._wait(alias), timeout))[0:2]

        async def wait_until(self, alias=None, timeout=5):
            return await asyncio.wait_for(self._wait(alias), timeout)

    return Events()
