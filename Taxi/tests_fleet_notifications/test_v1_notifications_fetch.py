import json

import pytest

from tests_fleet_notifications import utils

ENDPOINT = '/v1/notifications/fetch'
FLEET_ENDPOINT = '/fleet/notifications/v1/notifications/fetch'
ENDPOINTS = [ENDPOINT, FLEET_ENDPOINT]
DISPATCHER_ACCESS_CONTROL_ENDPOINT = (
    '/dispatcher-access-control/v1/parks/users/list'
)


def build_params(endpoint, park_id='park_valid'):
    if endpoint == ENDPOINT:
        return {'park_id': park_id}
    return {}


def build_headers(endpoint, park_id='park_valid'):
    if endpoint == ENDPOINT:
        return utils.HEADERS
    return {**utils.HEADERS, 'X-Park-ID': park_id}


def check_fetch_request(request, is_superuser=False, cursor=None):
    request_data = json.loads(request['request'].get_data())
    channels = [
        'city:Москва',
        'city:Москва:specification:delivery',
        'city:Москва:specification:taxi',
        'country:rus',
        'country:rus:specification:delivery',
        'country:rus:specification:taxi',
        'park:park_valid',
        'park:park_valid:group:group_valid',
        'park:park_valid:user:100',
        'park:park_valid:user:id',
    ]
    if is_superuser:
        channels.extend(
            [
                'country:rus:position:director',
                'country:rus:position:director:specification:delivery',
                'country:rus:position:director:specification:taxi',
                'city:Москва:position:director',
                'city:Москва:position:director:specification:delivery',
                'city:Москва:position:director:specification:taxi',
                'park:park_valid:position:director',
            ],
        )
    assert sorted(request_data['channels']) == sorted(channels)
    if cursor:
        assert request_data['cursor'] == cursor


def build_expected_notifications(forced_open):
    return {
        'cursor': '2019-01-01T23:59:59+0000',
        'forced_open': forced_open,
        'has_more': False,
        'notifications': [
            {
                'created_at': '2019-01-02T23:59:59+0000',
                'id': '1',
                'payload': {
                    'entity': {'id': 'news_id', 'type': 'news'},
                    'text': 'text_1',
                    'title': 'title_1',
                },
                'status': 'new',
            },
            {
                'created_at': '2019-01-01T23:59:59+0000',
                'id': '2',
                'payload': {
                    'entity': {'type': 'external', 'url': 'https://ya.ru'},
                    'text': 'text_2',
                    'title': 'title_2',
                },
                'status': 'read',
            },
        ],
    }


OK_PARAMS = [{}, {'cursor': '2019-01-04T23:59:59+0000'}]


@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.parametrize('body', OK_PARAMS)
async def test_success(
        taxi_fleet_notifications,
        mock_fleet_parks_list,
        dispatcher_access_control,
        mock_feeds,
        endpoint,
        body,
):

    response = await taxi_fleet_notifications.post(
        endpoint,
        params=build_params(endpoint),
        json=body,
        headers=build_headers(endpoint),
    )

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert dispatcher_access_control.parks_users_list.times_called == 1
    assert mock_feeds.fetch.times_called == 1
    check_fetch_request(mock_feeds.fetch.next_call())

    assert response.status_code == 200, response.text
    assert response.json() == build_expected_notifications(forced_open=False)


@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='test_experiment',
    consumers=['fleet-notifications/v1_notifications_fetch'],
    clauses=[],
    default_value={'forced_open': True},
)
async def test_forced_open(
        taxi_fleet_notifications,
        mock_fleet_parks_list,
        dispatcher_access_control,
        mock_feeds,
        endpoint,
):

    response = await taxi_fleet_notifications.post(
        endpoint,
        params=build_params(endpoint),
        json={},
        headers=build_headers(endpoint),
    )

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert dispatcher_access_control.parks_users_list.times_called == 1
    assert mock_feeds.fetch.times_called == 1
    check_fetch_request(mock_feeds.fetch.next_call())

    assert response.status_code == 200, response.text
    assert response.json() == build_expected_notifications(forced_open=True)


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_superuser(
        taxi_fleet_notifications,
        mock_fleet_parks_list,
        dispatcher_access_control,
        mock_feeds,
        endpoint,
):

    dispatcher_access_control.set_users(
        [
            {
                'group_id': 'group_valid',
                'id': 'id',
                'is_confirmed': True,
                'is_enabled': True,
                'is_superuser': True,
                'is_usage_consent_accepted': False,
                'park_id': 'park_valid',
            },
        ],
    )

    response = await taxi_fleet_notifications.post(
        endpoint,
        params=build_params(endpoint),
        headers=build_headers(endpoint),
    )

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert dispatcher_access_control.parks_users_list.times_called == 1
    assert mock_feeds.fetch.times_called == 1
    check_fetch_request(mock_feeds.fetch.next_call(), is_superuser=True)

    assert response.status_code == 200, response.text
    assert response.json() == build_expected_notifications(forced_open=False)


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_no_feeds(
        taxi_fleet_notifications,
        mock_fleet_parks_list,
        dispatcher_access_control,
        mock_feeds,
        load_json,
        endpoint,
):

    mock_feeds.set_feeds([])

    response = await taxi_fleet_notifications.post(
        endpoint,
        params=build_params(endpoint),
        headers=build_headers(endpoint),
    )

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert dispatcher_access_control.parks_users_list.times_called == 1
    assert mock_feeds.fetch.times_called == 1
    check_fetch_request(mock_feeds.fetch.next_call())

    assert response.status_code == 200, response.text
    assert response.json() == {
        'forced_open': False,
        'has_more': False,
        'notifications': [],
    }


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_bad_feeds(
        taxi_fleet_notifications,
        mock_fleet_parks_list,
        dispatcher_access_control,
        mock_feeds,
        load_json,
        endpoint,
):

    mock_feeds.set_feeds(load_json('bad_feeds.json'))

    response = await taxi_fleet_notifications.post(
        endpoint,
        params=build_params(endpoint),
        headers=build_headers(endpoint),
    )

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert dispatcher_access_control.parks_users_list.times_called == 1
    assert mock_feeds.fetch.times_called == 1
    check_fetch_request(mock_feeds.fetch.next_call())

    assert response.status_code == 200, response.text
    assert response.json() == {
        'cursor': '2019-01-04T23:59:59+0000',
        'forced_open': False,
        'has_more': False,
        'notifications': [],
    }


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_park_not_found(
        taxi_fleet_notifications, mock_fleet_parks_list, endpoint,
):

    response = await taxi_fleet_notifications.post(
        endpoint,
        params=build_params(endpoint, park_id='park_invalid'),
        headers=build_headers(endpoint, park_id='park_invalid'),
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'park_not_found',
        'message': 'Park not found',
    }


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_no_user_in_park(
        taxi_fleet_notifications,
        mock_fleet_parks_list,
        dispatcher_access_control,
        endpoint,
):

    dispatcher_access_control.set_users([])
    response = await taxi_fleet_notifications.post(
        endpoint,
        params=build_params(endpoint),
        headers=build_headers(endpoint),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'invalid_park',
        'message': 'No such user in park',
    }


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_invalid_cursor(taxi_fleet_notifications, endpoint):

    response = await taxi_fleet_notifications.post(
        endpoint,
        params=build_params(endpoint),
        json={'cursor': 'invalid'},
        headers=build_headers(endpoint),
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == '400'


BAD_HEADERS_PARAMS = [
    (ENDPOINT, {'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET}, 401),
    (FLEET_ENDPOINT, {'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET}, 401),
    (
        ENDPOINT,
        {
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
        403,
    ),
    (
        FLEET_ENDPOINT,
        {
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
        403,
    ),
    (FLEET_ENDPOINT, utils.HEADERS, 400),
]


@pytest.mark.parametrize(
    'endpoint, bad_headers, expected_code', BAD_HEADERS_PARAMS,
)
async def test_no_user_ticket(
        taxi_fleet_notifications, endpoint, bad_headers, expected_code,
):

    response = await taxi_fleet_notifications.post(
        endpoint, params=build_params(endpoint), headers=bad_headers,
    )

    assert response.status_code == expected_code, response.text
    assert response.json()['code'] == str(expected_code)
