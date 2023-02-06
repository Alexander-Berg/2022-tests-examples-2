import json

import pytest

from tests_fleet_notifications import utils

ENDPOINT = '/v1/notifications/status'
FLEET_ENDPOINT = '/fleet/notifications/v1/notifications/status'
ENDPOINTS = [ENDPOINT, FLEET_ENDPOINT]

ID1 = 'notification1'
ID2 = 'notification2'


def build_params(endpoint, park_id='park_valid'):
    if endpoint == ENDPOINT:
        return {'park_id': park_id}
    return {}


def build_headers(endpoint, park_id='park_valid'):
    if endpoint == ENDPOINT:
        return utils.HEADERS
    return {**utils.HEADERS, 'X-Park-ID': park_id}


def build_feeds_statuses(notification_ids):
    result = {}
    for notification_id in notification_ids:
        result[notification_id] = 200
    return result


def check_log_status_request(request, expected_request):
    request_data = json.loads(request['request'].get_data())
    assert request_data == expected_request


def build_log_status_ok_request(notification_ids, status):
    return {
        'channel': 'park:park_valid:user:100',
        'feed_ids': notification_ids,
        'service': 'fleet-notifications',
        'status': status,
    }


def check_response(response_json, notification_ids, status):
    assert sorted(response_json['results'], key=lambda i: i['id']) == sorted(
        [
            {'id': notification_id, 'status': 'ok'}
            for notification_id in notification_ids
        ],
        key=lambda i: i['id'],
    )


def build_payload(ids, status):
    return {'ids': ids, 'status': status}


@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.parametrize('notification_ids', [[ID1], [ID1, ID2]])
@pytest.mark.parametrize('status', ['read', 'viewed'])
async def test_ok(
        taxi_fleet_notifications,
        mock_fleet_parks_list,
        dispatcher_access_control,
        mock_feeds,
        endpoint,
        notification_ids,
        status,
):
    mock_feeds.set_statuses(build_feeds_statuses(notification_ids))

    response = await taxi_fleet_notifications.post(
        endpoint,
        params=build_params(endpoint),
        json=build_payload(notification_ids, status),
        headers=build_headers(endpoint),
    )

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert mock_feeds.log_status.times_called == 1
    check_log_status_request(
        mock_feeds.log_status.next_call(),
        build_log_status_ok_request(notification_ids, status),
    )

    assert response.status_code == 200, response.text
    check_response(response.json(), notification_ids, status)


@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.parametrize(
    'status_code, status_message', [(404, 'not_found'), (400, 'fail')],
)
async def test_not_found(
        taxi_fleet_notifications,
        mock_fleet_parks_list,
        dispatcher_access_control,
        mock_feeds,
        endpoint,
        status_code,
        status_message,
):
    mock_feeds.set_statuses({ID1: status_code})

    response = await taxi_fleet_notifications.post(
        endpoint,
        params=build_params(endpoint),
        json=build_payload([ID1], 'read'),
        headers=build_headers(endpoint),
    )

    assert mock_feeds.log_status.times_called == 1
    check_log_status_request(
        mock_feeds.log_status.next_call(),
        build_log_status_ok_request([ID1], 'read'),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'results': [{'id': ID1, 'status': status_message}],
    }


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_invalid_status(
        taxi_fleet_notifications,
        mock_fleet_parks_list,
        dispatcher_access_control,
        mock_feeds,
        endpoint,
):

    response = await taxi_fleet_notifications.post(
        endpoint,
        params=build_params(endpoint),
        json=build_payload([ID1], 'invalid'),
        headers=build_headers(endpoint),
    )

    assert mock_fleet_parks_list.mock_parks_list.times_called == 0
    assert mock_feeds.log_status.times_called == 0

    assert response.status_code == 400, response.text
    assert response.json()['code'] == '400'


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_park_not_found(
        taxi_fleet_notifications, mock_fleet_parks_list, endpoint,
):

    response = await taxi_fleet_notifications.post(
        endpoint,
        params=build_params(endpoint, park_id='park_invalid'),
        json=build_payload([ID1], 'read'),
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
        json=build_payload([ID1], 'read'),
        headers=build_headers(endpoint),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'invalid_park',
        'message': 'No such user in park',
    }


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
        endpoint,
        params=build_params(endpoint),
        json=build_payload([ID1], 'read'),
        headers=bad_headers,
    )

    assert response.status_code == expected_code, response.text
    assert response.json()['code'] == str(expected_code)
