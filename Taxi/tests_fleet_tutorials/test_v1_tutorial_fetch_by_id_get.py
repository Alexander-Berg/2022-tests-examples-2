import json

import pytest

from tests_fleet_tutorials import utils

ENDPOINT = '/v1/tutorials/fetch/by-id'
FLEET_ENDPOINT = '/fleet/tutorials/v1/tutorials/fetch/by-id'
ENDPOINTS = [ENDPOINT, FLEET_ENDPOINT]

SERVICE_CHANNELS = [
    'service;country:rus;position:all',
    'service;city:Москва;position:all',
    'service;park:park_id_1;position:all',
    'user:100',
]


def check_fetch_channels(request):
    assert sorted(
        json.loads(request['request'].get_data())['channels'],
    ) == sorted(SERVICE_CHANNELS)


def build_params(endpoint, tutorial_id, park_id='park_id_1'):
    params = {'tutorial_id': tutorial_id}
    if endpoint == ENDPOINT:
        params['park_id'] = park_id
    return params


def build_headers(endpoint, park_id='park_id_1', headers=None):
    if headers is None:
        headers = utils.HEADERS
    if endpoint == ENDPOINT:
        return headers
    return {**headers, 'X-Park-ID': park_id}


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_ok(
        taxi_fleet_tutorials,
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        endpoint,
):
    response = await taxi_fleet_tutorials.get(
        endpoint,
        params=build_params(endpoint, 'tutorial_1'),
        headers=build_headers(endpoint),
    )

    assert mock_feeds.fetch.has_calls
    check_fetch_channels(mock_feeds.fetch.next_call())

    expected_response = {
        'payloads': [
            {
                'data': {'body': 'Page 1 text'},
                'payload_id': 'feed_id_1_2:1111-111-1111',
                'status': 'new',
            },
            {
                'data': {'body': 'Page 2 text'},
                'payload_id': 'feed_id_1_2:2222-222-2222',
                'status': 'new',
            },
        ],
        'title': 'tutorial_1',
    }
    assert response.status_code == 200, response.text
    assert response.json() == expected_response


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_unknown_tutorial(
        taxi_fleet_tutorials,
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        endpoint,
):

    response = await taxi_fleet_tutorials.get(
        endpoint,
        params=build_params(endpoint, 'tutorial_4'),
        headers=build_headers(endpoint),
    )

    assert mock_feeds.fetch.has_calls
    check_fetch_channels(mock_feeds.fetch.next_call())

    expected_response = {'code': '404', 'message': 'Tutorial not found'}
    assert response.status_code == 404, response.text
    assert response.json() == expected_response
