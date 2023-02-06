import json

import pytest

from tests_fleet_notifications import utils

ENDPOINT = '/v1/notifications/count'
FLEET_ENDPOINT = '/fleet/notifications/v1/notifications/count'
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


def check_request(request, is_superuser=False):
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


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_ok(
        taxi_fleet_notifications,
        mock_fleet_parks_list,
        dispatcher_access_control,
        mock_feeds,
        endpoint,
):

    response = await taxi_fleet_notifications.get(
        endpoint,
        params=build_params(endpoint),
        headers=build_headers(endpoint),
    )

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert dispatcher_access_control.parks_users_list.times_called == 1
    assert mock_feeds.summary.times_called == 1
    check_request(mock_feeds.summary.next_call())

    assert response.status_code == 200, response.text
    assert response.json() == {'new': 3}


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_park_not_found(
        taxi_fleet_notifications, mock_fleet_parks_list, endpoint,
):

    response = await taxi_fleet_notifications.get(
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
    response = await taxi_fleet_notifications.get(
        endpoint,
        params=build_params(endpoint),
        headers=build_headers(endpoint),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'invalid_park',
        'message': 'No such user in park',
    }


BAD_HEADERS_PARAMS = [
    (
        ENDPOINT,
        {'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET},
        401,
        {
            'code': '401',
            'message': 'missing or empty X-Ya-User-Ticket-Provider header',
        },
    ),
    (
        FLEET_ENDPOINT,
        {'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET},
        401,
        {
            'code': '401',
            'message': 'missing or empty X-Ya-User-Ticket-Provider header',
        },
    ),
    (
        ENDPOINT,
        {
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
        403,
        {'code': '403', 'message': 'missing or empty X-Yandex-UID header'},
    ),
    (
        FLEET_ENDPOINT,
        {
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
        403,
        {'code': '403', 'message': 'missing or empty X-Yandex-UID header'},
    ),
    (
        FLEET_ENDPOINT,
        utils.HEADERS,
        400,
        {'code': '400', 'message': 'Missing X-Park-ID in header'},
    ),
]


@pytest.mark.parametrize(
    'endpoint, bad_headers, expected_code, expected_response',
    BAD_HEADERS_PARAMS,
)
async def test_no_user_ticket(
        taxi_fleet_notifications,
        endpoint,
        bad_headers,
        expected_code,
        expected_response,
):

    response = await taxi_fleet_notifications.get(
        endpoint, params=build_params(endpoint), headers=bad_headers,
    )

    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response
