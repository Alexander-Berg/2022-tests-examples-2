import json

import pytest

from tests_fleet_tutorials import utils

ENDPOINT = '/v1/tutorials/status'
FLEET_ENDPOINT = '/fleet/tutorials/v1/tutorials/status'
ENDPOINTS = [ENDPOINT, FLEET_ENDPOINT]


def build_headers(endpoint, park_id='park_id_1'):
    if endpoint == ENDPOINT:
        return utils.HEADERS
    return {**utils.HEADERS, 'X-Park-ID': park_id}


def build_params(endpoint, park_id='park_id_1'):
    if endpoint == ENDPOINT:
        return {'park_id': park_id}
    return {}


def check_log_status_request(
        request, feed_id, feed_status, payload_uids=None, payload_status=None,
):
    request_data = json.loads(request['request'].get_data())
    assert request_data['feed_id'] == feed_id
    assert request_data['status'] == feed_status
    assert request_data['channel'] == 'user:100'
    if payload_uids is not None:
        for payload_uid in payload_uids:
            assert (
                request_data['meta'][payload_uid]['last_status']['status']
                == payload_status
            )


@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.parametrize('set_status', ['viewed', 'read'])
async def test_set_payload_status(
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_fleet_tutorials,
        endpoint,
        set_status,
):
    feed_id = 'feed_id_1'
    payload_uid = '1111-111-1111'
    payload_id = feed_id + ':' + payload_uid

    mock_feeds.set_statuses({feed_id: 200})

    response = await taxi_fleet_tutorials.post(
        endpoint,
        params=build_params(endpoint),
        json={'payload_ids': [payload_id], 'status': set_status},
        headers=build_headers(endpoint),
    )

    assert mock_feeds.log_status.times_called == 1
    check_log_status_request(
        mock_feeds.log_status.next_call(),
        feed_id,
        feed_status='viewed',
        payload_uids=[payload_uid],
        payload_status=set_status,
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'statuses': [{'payload_id': payload_id, 'status': 'ok'}],
    }


@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.parametrize('set_status', ['viewed', 'read'])
async def test_set_all_payloads_status(
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_fleet_tutorials,
        endpoint,
        set_status,
):
    feed_id = 'feed_id_1'
    payload_uid_1 = '1111-111-1111'
    payload_uid_2 = '2222-222-2222'
    payload_id_1 = feed_id + ':' + payload_uid_1
    payload_id_2 = feed_id + ':' + payload_uid_2

    mock_feeds.set_statuses({feed_id: 200})

    response = await taxi_fleet_tutorials.post(
        endpoint,
        params=build_params(endpoint),
        json={
            'payload_ids': [payload_id_1, payload_id_2],
            'status': set_status,
        },
        headers=build_headers(endpoint),
    )

    assert mock_feeds.log_status.times_called == 1
    check_log_status_request(
        mock_feeds.log_status.next_call(),
        feed_id,
        feed_status=set_status,
        payload_uids=[payload_uid_1, payload_uid_2],
        payload_status=set_status,
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'statuses': [
            {'payload_id': payload_id_1, 'status': 'ok'},
            {'payload_id': payload_id_2, 'status': 'ok'},
        ],
    }


@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.parametrize('set_status', ['viewed', 'read'])
async def test_set_last_payload_status(
        mock_feeds,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_fleet_tutorials,
        endpoint,
        set_status,
):
    feed_id = 'feed_id_2'
    payload_uid = '2222-222-2222'
    payload_id = feed_id + ':' + payload_uid

    mock_feeds.set_statuses({feed_id: 200})

    response = await taxi_fleet_tutorials.post(
        endpoint,
        params=build_params(endpoint),
        json={'payload_ids': [payload_id], 'status': set_status},
        headers=build_headers(endpoint),
    )

    assert mock_feeds.log_status.times_called == 1
    check_log_status_request(
        mock_feeds.log_status.next_call(),
        feed_id,
        feed_status=set_status,
        payload_uids=[payload_uid],
        payload_status=set_status,
    )

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
    payload_uid = '2222-222-2222'
    payload_id = feed_id + ':' + payload_uid

    mock_feeds.set_statuses({feed_id: status_code})

    response = await taxi_fleet_tutorials.post(
        endpoint,
        params=build_params(endpoint),
        json={'payload_ids': [payload_id], 'status': 'read'},
        headers=build_headers(endpoint),
    )

    assert mock_feeds.log_status.times_called == 1
    check_log_status_request(
        mock_feeds.log_status.next_call(),
        feed_id,
        feed_status='read',
        payload_uids=[payload_uid],
        payload_status='read',
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'statuses': [{'payload_id': payload_id, 'status': status_message}],
    }
