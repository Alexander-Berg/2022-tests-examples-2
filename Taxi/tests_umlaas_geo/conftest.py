# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import datetime

import pytest
# pylint: disable=no-name-in-module
from routehistory.handlers.routehistory_shuttle_order_pb2 import (
    RouteHistoryShuttleOrdersResponse,
)
from umlaas_geo_plugins import *  # noqa: F403 F401


@pytest.fixture
def _mock_userplaces(mockserver, load_json):
    @mockserver.json_handler('/userplaces/userplaces/list')
    def _get_response(request):
        return load_json('userplaces_list_response.json')

    return _get_response


@pytest.fixture
def _mock_routehistory(mockserver, load_json):
    @mockserver.json_handler('/routehistory/routehistory/get')
    def _get_response(request):
        return load_json('routehistory_get_response.json')

    return _get_response


@pytest.fixture
def _mock_routehistory_grocery(mockserver, load_json):
    @mockserver.json_handler('/routehistory/routehistory/grocery-get')
    def _get_response(request):
        return load_json('routehistory_grocery_get_response.json')

    return _get_response


@pytest.fixture
def _mock_pickup_points_manager(mockserver, load_json):
    @mockserver.json_handler('/pickup-points-manager/v1/points/')
    def _get_response(request):
        return load_json('pickup_points_manager_response.json')

    return _get_response


@pytest.fixture
def _mock_yaga_adjust(mockserver, load_json):
    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _get_response(request):
        return load_json('yaga_adjust_position_response.json')

    return _get_response


@pytest.fixture
def _mock_searchhistory(mockserver, load_json):
    @mockserver.json_handler('/routehistory/routehistory/search-get')
    def _get_response(request):
        return load_json('searchhistory_get_response.json')

    return _get_response


@pytest.fixture
def _mock_shuttlehistory(mockserver, load_json):
    @mockserver.json_handler('/routehistory/routehistory/shuttle-get')
    def _get_response(request):
        resp_json = load_json('shuttle_get_response.json')
        response = RouteHistoryShuttleOrdersResponse()
        for res in resp_json['results']:
            result = response.result.add()
            result.yandex_uid = res['yandex_uid']
            result.order_id = res['order_id']
            result.created.FromDatetime(
                datetime.datetime.strptime(
                    res['created'], '%Y-%m-%dT%H:%M:%S.%fZ',
                ),
            )
            result.source.text = res['source']['text']
            result.source.uri = res['source']['uri']
            result.source.position.lon = res['source']['position'][0]
            result.source.position.lat = res['source']['position'][1]
            result.destination.text = res['destination']['text']
            result.destination.uri = res['destination']['uri']
            result.destination.position.lon = res['destination']['position'][0]
            result.destination.position.lat = res['destination']['position'][1]

        return mockserver.make_response(
            response.SerializeToString(),
            content_type='application/x-protobuf',
        )

    return _get_response


@pytest.fixture
def _mock_eats_ordershistory(mockserver, load_json):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _get_response(request):
        return load_json('eats_ordershistory_get_response.json')

    return _get_response
