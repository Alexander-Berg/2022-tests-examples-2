import json

import pytest

from tests_fleet_tutorials import utils

ENDPOINT = '/v1/tutorials/remove'
FLEET_ENDPOINT = '/fleet/tutorials/v1/tutorials/remove'
ENDPOINTS = [ENDPOINT, FLEET_ENDPOINT]

FEED_ID = 'feed_id_1'
PAYLOAD_ID = 'feed_id_1:1111-111-1111'
PAYLOAD_IDS = [PAYLOAD_ID]
USER_CHANNEL = 'user:100'


def build_headers(endpoint, park_id='park_id_1'):
    if endpoint == ENDPOINT:
        return utils.HEADERS
    return {**utils.HEADERS, 'X-Park-ID': park_id}


def build_params(endpoint, park_id='park_id_1'):
    if endpoint == ENDPOINT:
        return {'park_id': park_id}
    return {}


def check_remove_request(request, feed_id):
    request_data = json.loads(request['request'].get_data())
    assert request_data['feed_id'] == feed_id
    assert request_data['channels'] == [USER_CHANNEL]


def check_log_status_request(request, feed_id, payload_uid):
    request_data = json.loads(request['request'].get_data())
    assert request_data['feed_id'] == feed_id
    assert request_data['status'] == 'viewed'
    assert request_data['channel'] == USER_CHANNEL
    assert (
        request_data['meta'][payload_uid]['last_status']['status'] == 'removed'
    )


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_ok(
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_fleet_tutorials,
        endpoint,
):
    feed_id = 'feed_id_1'
    payload_id_1 = feed_id + ':1111-111-1111'
    payload_id_2 = feed_id + ':2222-222-2222'

    mock_feeds.set_statuses({feed_id: 200})

    response = await taxi_fleet_tutorials.post(
        endpoint,
        params=build_params(endpoint),
        json={'payload_ids': [payload_id_1, payload_id_2]},
        headers=build_headers(endpoint),
    )

    assert mock_feeds.remove.times_called == 1
    check_remove_request(mock_feeds.remove.next_call(), feed_id)

    assert response.status_code == 200, response.text
    assert response.json() == {
        'statuses': [
            {'payload_id': payload_id_1, 'status': 'ok'},
            {'payload_id': payload_id_2, 'status': 'ok'},
        ],
    }


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_set_status_removed(
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_fleet_tutorials,
        endpoint,
):
    feed_id = 'feed_id_1'
    payload_uid = '1111-111-1111'
    payload_id = feed_id + ':' + payload_uid

    mock_feeds.set_statuses({feed_id: 200})

    response = await taxi_fleet_tutorials.post(
        endpoint,
        params=build_params(endpoint),
        json={'payload_ids': [payload_id]},
        headers=build_headers(endpoint),
    )

    assert mock_feeds.remove.times_called == 0
    assert mock_feeds.log_status.times_called == 1

    check_log_status_request(
        mock_feeds.log_status.next_call(), feed_id, payload_uid,
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'statuses': [{'payload_id': payload_id, 'status': 'ok'}],
    }


@pytest.mark.parametrize('endpoint', ENDPOINTS)
async def test_remove_last_payload(
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_fleet_tutorials,
        endpoint,
):
    feed_id = 'feed_id_2'
    payload_uid = '2222-222-2222'
    payload_id = feed_id + ':' + payload_uid

    mock_feeds.set_statuses({feed_id: 200})

    response = await taxi_fleet_tutorials.post(
        endpoint,
        params=build_params(endpoint),
        json={'payload_ids': [payload_id]},
        headers=build_headers(endpoint),
    )

    assert mock_feeds.remove.times_called == 1
    check_remove_request(mock_feeds.remove.next_call(), feed_id)

    assert response.status_code == 200, response.text
    assert response.json() == {
        'statuses': [{'payload_id': payload_id, 'status': 'ok'}],
    }


FEEDS_FAIL_PARAMS = [(400, 'fail'), (404, 'not_found')]


@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.parametrize('status_code, status_message', FEEDS_FAIL_PARAMS)
async def test_feeds_fail(
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_fleet_tutorials,
        endpoint,
        status_code,
        status_message,
):
    feed_id = 'feed_id_2'
    payload_id = feed_id + ':2222-222-2222'

    mock_feeds.set_statuses({feed_id: status_code})

    response = await taxi_fleet_tutorials.post(
        endpoint,
        params=build_params(endpoint),
        json={'payload_ids': [payload_id]},
        headers=build_headers(endpoint),
    )

    assert mock_feeds.remove.times_called == 1
    check_remove_request(mock_feeds.remove.next_call(), feed_id)

    assert response.status_code == 200, response.text
    assert response.json() == {
        'statuses': [{'payload_id': payload_id, 'status': status_message}],
    }
