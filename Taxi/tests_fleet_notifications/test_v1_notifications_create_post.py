import json

import pytest

from tests_fleet_notifications import utils

ENDPOINT = '/v1/notifications/create'

HEADERS = {
    'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
    'X-Idempotency-Token': 'idempotency_token',
}

REQUEST_ID = 'request_id_1'

PAYLOAD = {
    'entity': {'id': 'news_id', 'type': 'news'},
    'text': 'text_1',
    'title': 'title_1',
}


def check_create_request(request, channels, expire=None, publish_at=None):
    request_headers = request['request'].headers
    request_data = json.loads(request['request'].get_data())
    assert request_headers['X-Idempotency-Token'] == 'idempotency_token'
    assert request_data['service'] == 'fleet-notifications'
    assert request_data['request_id'] == REQUEST_ID
    assert request_data['payload'] == PAYLOAD
    assert sorted(
        request_data['channels'], key=lambda i: i['channel'],
    ) == sorted(channels, key=lambda i: i['channel'])
    if expire:
        assert request_data['expire'] == expire
    if publish_at:
        assert request_data['publish_at'] == publish_at


OK_PARAMS = [
    ([{'country': 'Rus'}], [{'channel': 'country:Rus'}]),
    (
        [
            {'country': 'Rus', 'position': 'director'},
            {'city': 'Moscow', 'position': 'director'},
        ],
        [
            {'channel': 'country:Rus:position:director'},
            {'channel': 'city:Moscow:position:director'},
        ],
    ),
    ([{'park_id': 'park1'}], [{'channel': 'park:park1'}]),
    (
        [{'group_id': 'group1', 'park_id': 'park1'}],
        [{'channel': 'park:park1:group:group1'}],
    ),
    (
        [{'user_id': 'user1', 'park_id': 'park1'}],
        [{'channel': 'park:park1:user:user1'}],
    ),
]


@pytest.mark.parametrize('destinations, channels', OK_PARAMS)
async def test_ok(
        taxi_fleet_notifications, mock_feeds, destinations, channels,
):

    response = await taxi_fleet_notifications.post(
        ENDPOINT,
        json={
            'request_id': REQUEST_ID,
            'destinations': destinations,
            'payload': PAYLOAD,
        },
        headers=HEADERS,
    )

    assert mock_feeds.create.times_called == 1
    check_create_request(mock_feeds.create.next_call(), channels)

    assert response.status_code == 200, response.text
    assert response.json() == {}


@pytest.mark.now('2020-01-31T00:00:00')
async def test_ok_with_expiry_and_publish_date(
        taxi_fleet_notifications, mock_feeds,
):
    destinations = [{'country': 'Rus'}]
    channels = [{'channel': 'country:Rus'}]

    response = await taxi_fleet_notifications.post(
        ENDPOINT,
        json={
            'request_id': REQUEST_ID,
            'destinations': destinations,
            'payload': PAYLOAD,
            'expiry_date': '2020-03-26T00:00:00+00:00',
            'publish_at': '2020-03-26T00:00:00+03:00',
        },
        headers=HEADERS,
    )

    assert mock_feeds.create.times_called == 1
    check_create_request(
        mock_feeds.create.next_call(),
        channels,
        expire='2020-03-26T00:00:00+00:00',
        publish_at='2020-03-25T21:00:00+00:00',
    )

    assert response.status_code == 200, response.text
    assert response.json() == {}


@pytest.mark.now('2020-01-31T00:00:00+00:00')
async def test_invalid_expiry_date(taxi_fleet_notifications):
    destinations = [{'country': 'Rus'}]

    response = await taxi_fleet_notifications.post(
        ENDPOINT,
        json={
            'request_id': REQUEST_ID,
            'destinations': destinations,
            'payload': PAYLOAD,
            'expiry_date': '2020-01-31T00:00:00+00:00',
        },
        headers=HEADERS,
    )

    expected_response = {
        'code': 'invalid_date',
        'message': '\'expiry_date\' can\'t be less than now',
    }
    assert response.status_code == 400, response.text
    assert response.json() == expected_response


@pytest.mark.now('2020-01-31T00:00:00+00:00')
async def test_invalid_publish_at(taxi_fleet_notifications):
    destinations = [{'country': 'Rus'}]

    response = await taxi_fleet_notifications.post(
        ENDPOINT,
        json={
            'request_id': REQUEST_ID,
            'destinations': destinations,
            'payload': PAYLOAD,
            'publish_at': '2020-01-31T00:00:00+00:00',
        },
        headers=HEADERS,
    )

    expected_response = {
        'code': 'invalid_date',
        'message': '\'publish_at\' can\'t be less than now',
    }
    assert response.status_code == 400, response.text
    assert response.json() == expected_response


@pytest.mark.now('2020-01-31T00:00:00+00:00')
async def test_invalid_expiry_and_publish_date(taxi_fleet_notifications):
    destinations = [{'country': 'Rus'}]

    response = await taxi_fleet_notifications.post(
        ENDPOINT,
        json={
            'request_id': REQUEST_ID,
            'destinations': destinations,
            'payload': PAYLOAD,
            'expiry_date': '2020-01-31T00:00:01+00:00',
            'publish_at': '2020-01-31T00:00:02+00:00',
        },
        headers=HEADERS,
    )

    expected_response = {
        'code': 'invalid_date',
        'message': '\'expiry_date\' must be greater than \'publish_at\'',
    }
    assert response.status_code == 400, response.text
    assert response.json() == expected_response


INVALID_DESTINATION_PARAMS = [
    {'park_id': 'park1', 'group_id': 'group1', 'user_id': 'user1'},
    {'park_id': 'park1', 'group_id': 'group1', 'position': 'director'},
    {'park_id': 'park1', 'user_id': 'user1', 'position': 'director'},
]


@pytest.mark.parametrize('destination', INVALID_DESTINATION_PARAMS)
async def test_invalid_destination(taxi_fleet_notifications, destination):
    response = await taxi_fleet_notifications.post(
        ENDPOINT,
        json={
            'request_id': REQUEST_ID,
            'destinations': [destination],
            'payload': PAYLOAD,
        },
        headers=HEADERS,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_destination',
        'message': 'Too many destination properties',
    }
