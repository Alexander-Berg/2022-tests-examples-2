import json

import pytest

from tests_fleet_tutorials import utils

ENDPOINT = '/v1/tutorials/fetch'
FLEET_ENDPOINT = '/fleet/tutorials/v1/tutorials/fetch'
ENDPOINTS = [ENDPOINT, FLEET_ENDPOINT]

PARK_ID = 'park_id_1'
PAGE_ID = 'page_id_1'
USER_CHANNEL = 'user:100'
CHANNELS = [
    f'park:{PARK_ID};page:all;position:all',
    f'park:{PARK_ID};page:{PAGE_ID};position:all',
    'city:Москва;page:all;position:all',
    f'city:Москва;page:{PAGE_ID};position:all',
    'country:rus;page:all;position:all',
    f'country:rus;page:{PAGE_ID};position:all',
    USER_CHANNEL,
]

SUPERUSER_CHANNELS = CHANNELS + [
    f'park:{PARK_ID};page:all;position:director',
    f'park:{PARK_ID};page:{PAGE_ID};position:director',
    'city:Москва;page:all;position:director',
    f'city:Москва;page:{PAGE_ID};position:director',
    'country:rus;page:all;position:director',
    f'country:rus;page:{PAGE_ID};position:director',
]


def build_headers(endpoint, park_id='park_id_1'):
    if endpoint == ENDPOINT:
        return utils.HEADERS
    return {**utils.HEADERS, 'X-Park-ID': park_id}


def build_json(endpoint, park_id=PARK_ID, page_id=PAGE_ID):
    json_body = {'page_id': page_id}
    if endpoint == ENDPOINT:
        json_body['park_id'] = park_id
    return json_body


def check_fetch_channels(request, channels):
    assert sorted(
        json.loads(request['request'].get_data())['channels'],
    ) == sorted(channels)


def check_log_status_request(request, feed_id, status):
    request_data = json.loads(request['request'].get_data())
    assert request_data['feed_id'] == feed_id
    assert request_data['channel'] == USER_CHANNEL
    assert request_data['status'] == status


EXPECTED_BASIC_RESPONSE = {
    'payloads': [
        {
            'data': {'body': 'Page text'},
            'payload_id': 'feed_id_1:1111-111-1111',
            'status': 'new',
        },
    ],
    'title': 'Basic tutorial',
}


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_basic_tutorial(
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_fleet_tutorials,
        endpoint,
):
    response = await taxi_fleet_tutorials.post(
        endpoint, json=build_json(endpoint), headers=build_headers(endpoint),
    )

    assert mock_fleet_parks_list.times_called == 1
    assert dispatcher_access_control.parks_users_list.times_called == 1
    assert mock_feeds.fetch.times_called == 1
    check_fetch_channels(mock_feeds.fetch.next_call(), CHANNELS)

    assert response.status_code == 200, response.text
    assert response.json() == EXPECTED_BASIC_RESPONSE


EXPECTED_NEW_USER_RESPONSE = {
    'payloads': [
        {
            'data': {
                'body': 'Page text',
                'buttons': [
                    {'action': {'type': 'next'}, 'title': 'Next'},
                    {'action': {'type': 'close'}, 'title': 'Close'},
                ],
            },
            'payload_id': 'feed_id_1:1111-111-1111',
            'status': 'read',
        },
        {
            'data': {
                'body': 'Page text',
                'buttons': [
                    {
                        'action': {'link': 'ya.ru', 'type': 'link'},
                        'title': 'go to',
                    },
                ],
            },
            'payload_id': 'feed_id_1:1111-111-1112',
            'status': 'new',
        },
    ],
    'title': 'Tutorial for new users',
}

TEST_OK_PARAMS = [
    ('dispatcher_access_control_user_created_at.json', CHANNELS),
    (
        'dispatcher_access_control_superuser_created_at.json',
        SUPERUSER_CHANNELS,
    ),
]


@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.parametrize('users_json, channels', TEST_OK_PARAMS)
async def test_new_user(
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_fleet_tutorials,
        load_json,
        endpoint,
        users_json,
        channels,
):
    dispatcher_access_control.set_users(load_json(users_json))
    response = await taxi_fleet_tutorials.post(
        endpoint, json=build_json(endpoint), headers=build_headers(endpoint),
    )

    assert mock_fleet_parks_list.times_called == 1
    assert dispatcher_access_control.parks_users_list.times_called == 1
    assert mock_feeds.fetch.times_called == 1
    check_fetch_channels(mock_feeds.fetch.next_call(), channels)

    assert response.status_code == 200, response.text
    assert response.json() == EXPECTED_NEW_USER_RESPONSE


EXPECTED_EXPERIMENT_RESPONSE = {
    'payloads': [
        {
            'data': {'body': 'Page text'},
            'payload_id': 'feed_id_2:1234-567-8910',
            'status': 'new',
        },
    ],
    'title': 'Experimental tutorial',
}


@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': ['park_id_1'],
                'arg_name': 'park_id',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='test_experiment',
    consumers=['fleet-tutorials/v1_tutorials_fetch'],
    clauses=[],
    default_value=True,
)
@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_experiment_tutorial(
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_fleet_tutorials,
        endpoint,
):
    response = await taxi_fleet_tutorials.post(
        endpoint, json=build_json(endpoint), headers=build_headers(endpoint),
    )

    assert mock_fleet_parks_list.times_called == 1
    assert dispatcher_access_control.parks_users_list.times_called == 1
    assert mock_feeds.fetch.times_called == 1
    check_fetch_channels(mock_feeds.fetch.next_call(), CHANNELS)

    assert response.status_code == 200, response.text
    assert response.json() == EXPECTED_EXPERIMENT_RESPONSE


EXPECTED_NO_CONFIRM_RESPONSE = {
    'payloads': [
        {
            'data': {'body': 'Page text'},
            'payload_id': 'feed_id_1:1111-111-1111',
            'status': 'new',
        },
    ],
    'title': 'No confirm tutorial',
}


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_no_confirm_tutorial(
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_fleet_tutorials,
        load_json,
        endpoint,
):
    mock_feeds.set_feeds(load_json('feeds_no_confirm.json'))

    response = await taxi_fleet_tutorials.post(
        endpoint, json=build_json(endpoint), headers=build_headers(endpoint),
    )

    assert mock_fleet_parks_list.times_called == 1
    assert dispatcher_access_control.parks_users_list.times_called == 1
    assert mock_feeds.fetch.times_called == 1
    check_fetch_channels(mock_feeds.fetch.next_call(), CHANNELS)
    assert mock_feeds.log_status.times_called == 1
    check_log_status_request(
        mock_feeds.log_status.next_call(), 'feed_id_1', 'read',
    )

    assert response.status_code == 200, response.text
    assert response.json() == EXPECTED_NO_CONFIRM_RESPONSE


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_uber(
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_fleet_tutorials,
        load_json,
        endpoint,
):

    mock_feeds.set_feeds(load_json('feeds_no_confirm.json'))

    response = await taxi_fleet_tutorials.post(
        endpoint,
        json=build_json(endpoint, park_id='park_id_uber'),
        headers=build_headers(endpoint, 'park_id_uber'),
    )

    assert mock_fleet_parks_list.times_called == 1

    assert response.status_code == 200, response.text
    assert response.json() == {'payloads': [], 'title': ''}
