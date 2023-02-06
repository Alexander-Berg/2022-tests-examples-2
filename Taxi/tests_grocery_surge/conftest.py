import asyncio
import copy
import json

import pytest


# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from grocery_surge_plugins import *  # noqa: F403 F401

from . import consts


@pytest.fixture(autouse=True)
async def add_depots(grocery_depots):
    grocery_depots.add_depot(
        depot_test_id=1,
        depot_id='store11xx',
        region_id=223,
        location=[10, 10],
        phone_number='+78007700461',
        address='depot address 1',
        company_type='yandex',
        auto_add_zone=False,
    )
    grocery_depots.add_depot(
        depot_test_id=2,
        depot_id='store22xx',
        region_id=223,
        location=[11, 11],
        phone_number='+78007700462',
        address='depot address',
        company_type='yandex',
        auto_add_zone=False,
    )
    grocery_depots.add_depot(
        depot_test_id=100,
        depot_id='store22xx',
        region_id=223,
        location=[11, 11],
        phone_number='+78007700462',
        address='depot address',
        company_type='yandex',
        auto_add_zone=False,
    )
    grocery_depots.add_depot(
        depot_test_id=101,
        depot_id='store22xx',
        region_id=223,
        location=[11, 11],
        phone_number='+78007700462',
        address='depot address',
        company_type='yandex',
        auto_add_zone=False,
    )


@pytest.fixture(name='candidates', autouse=True)
def mock_candidates(mockserver):
    @mockserver.json_handler('/candidates/profiles')
    def _mock_candidates_profiles(request):
        drivers = []
        for driver_id in request.json['driver_ids']:
            parts = driver_id.split('_')
            drivers.append(
                {'dbid': parts[0], 'uuid': parts[1], 'position': [0, 0]},
            )
        return {'drivers': drivers}


@pytest.fixture(name='grocery-orders', autouse=True)
def mock_grocery_orders(mockserver):
    @mockserver.json_handler('/grocery-orders/internal/v1/get-info-bulk')
    def _mock_bulk_info(request):
        orders = []
        for order_id in request.json['order_ids']:
            orders.append(
                {
                    'order_id': order_id,
                    'status': 'assembled',
                    'location': {'lon': 0, 'lat': 0},
                    'cart_id': '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9',
                    'delivery_type': 'pickup',
                    'created': '2020-04-12T11:50:00+03:00',
                },
            )
        return orders


@pytest.fixture(name='grocery-cart-replica', autouse=True)
def mock_grocery_cart_replica(mockserver):
    @mockserver.json_handler(
        'grocery-cart-replica/internal/v1/cart/retrieve/depot/by_ids',
    )
    def _mock_grocery_cart_replica_by_ids(
            request,
    ):  # pylint: disable=unused-variable
        ret = []
        for cart_id in request.json['cart_ids']:
            cart = copy.deepcopy(consts.CART_DATA)
            cart['cart_id'] = cart_id
            ret.append(cart)

        return mockserver.make_response(status=200, json={'items': ret})

    @mockserver.json_handler(
        'grocery-cart-replica/internal/v1/cart/retrieve/depot/non_checkedout',
    )
    def _mock_grocery_cart_replica_non_checkedout(request):
        return mockserver.make_response(
            status=200, json={'items': [consts.CART_DATA_NON_CHECKED]},
        )

    @mockserver.json_handler('grocery-cart-replica/internal/v1/cart/retrieve')
    def _mock_grocery_cart_replica(request):  # pylint: disable=unused-variable
        return mockserver.make_response(
            status=200, json={'items': [consts.CART_DATA]},
        )


@pytest.fixture(name='solomon_agent', autouse=True)
def mock_solomon_agent(mockserver):
    class Context:
        def __init__(self):
            self.expected_request = {
                'commonLabels': {'application': 'grocery-surge'},
                'metrics': [
                    {
                        'labels': {
                            'depot_id': '1',
                            'sensor': 'surge_metrics.calc_surge',
                        },
                        'type': 'DGAUGE',
                        'value': 12.3,
                    },
                ],
            }

        def times_called(self):
            return _solomon_agent_mock.times_called

    @mockserver.json_handler('/solomon-agent/uservices')
    def _solomon_agent_mock(request):
        assert request.json == context.expected_request

        return mockserver.make_response(status=200)

    context = Context()
    return context


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

        async def count(self, alias=None, timeout=5):
            return await asyncio.wait_for(self._wait(alias), timeout)

    return Events()
