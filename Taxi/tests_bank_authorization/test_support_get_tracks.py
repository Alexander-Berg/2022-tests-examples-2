import pytest

from tests_bank_authorization import common

BUID = 'buid1'
HANDLE_URL = '/authorization-support/v1/get_tracks'


async def test_get_tracks(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'filters': {'buid': BUID}, 'limit': 100},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['tracks']) == 3


async def test_get_tracks_with_limit(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'filters': {'buid': BUID}, 'limit': 1},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['tracks']) == 1
    assert resp['cursor'] == 'eyJjdXJzb3Jfa2V5IjozfQ=='


async def test_get_tracks_with_cursor(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    request_cursor = 'eyJjdXJzb3Jfa2V5IjozfQ=='
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'filters': {'buid': BUID}, 'limit': 1, 'cursor': request_cursor},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['tracks']) == 1
    response_cursor = 'eyJjdXJzb3Jfa2V5IjoyfQ=='
    assert resp['cursor'] == response_cursor


async def test_get_tracks_without_user_id(taxi_bank_authorization, mockserver):
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'filters': {}, 'limit': 100},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'operation_type, count', [('start_session', 2), ('new_card', 1)],
)
async def test_get_tracks_with_type(
        taxi_bank_authorization,
        mockserver,
        access_control_mock,
        operation_type,
        count,
):
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {'buid': BUID, 'operation_type': operation_type},
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['tracks']) == count
    assert 'cursor' not in resp


async def test_get_tracks_with_created_at(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    start_time = '2022-02-03T00:00:00.0+00:00'
    end_time = '2022-02-04T00:00:00.0+00:00'
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'buid': BUID,
                'created_date_from': start_time,
                'created_date_to': end_time,
            },
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['tracks'] == [
        {
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a33',
            'buid': BUID,
            'operation_type': 'start_session',
            'created_at': '2022-02-03T20:28:58.838783+00:00',
            'updated_at': '2022-02-04T20:28:58.838783+00:00',
        },
    ]
    assert 'cursor' not in resp


async def test_get_tracks_with_updated_at(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    start_time = '2022-02-04T00:00:00.0+00:00'
    end_time = '2022-02-05T00:00:00.0+00:00'
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'buid': BUID,
                'updated_date_from': start_time,
                'updated_date_to': end_time,
            },
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['tracks'] == [
        {
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a33',
            'buid': BUID,
            'operation_type': 'start_session',
            'created_at': '2022-02-03T20:28:58.838783+00:00',
            'updated_at': '2022-02-04T20:28:58.838783+00:00',
        },
    ]
    assert 'cursor' not in resp


async def test_get_tracks_with_all_time(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    start_created_time = '2022-02-03T00:00:00.0+00:00'
    end_created_time = '2022-02-04T00:00:00.0+00:00'
    start_updated_time = '2022-02-04T00:00:00.0+00:00'
    end_updated_time = '2022-02-05T00:00:00.0+00:00'
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'buid': BUID,
                'created_date_from': start_created_time,
                'created_date_to': end_created_time,
                'updated_date_from': start_updated_time,
                'updated_date_to': end_updated_time,
            },
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['tracks'] == [
        {
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a33',
            'buid': BUID,
            'operation_type': 'start_session',
            'created_at': '2022-02-03T20:28:58.838783+00:00',
            'updated_at': '2022-02-04T20:28:58.838783+00:00',
        },
    ]
    assert 'cursor' not in resp


async def test_get_tracks_with_all_time_and_type(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    start_time = '2022-02-01T00:00:00.0+00:00'
    end_time = '2022-02-03T00:00:00.0+00:00'
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'buid': BUID,
                'operation_type': 'start_session',
                'created_date_from': start_time,
                'created_date_to': end_time,
                'updated_date_from': start_time,
                'updated_date_to': end_time,
            },
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['tracks'] == [
        {
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a11',
            'buid': BUID,
            'operation_type': 'start_session',
            'created_at': '2022-02-01T20:28:58.838783+00:00',
            'updated_at': '2022-02-01T20:28:58.838783+00:00',
        },
    ]
    assert 'cursor' not in resp
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_tracks_access_deny(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(''),
        json={'filters': {'buid': BUID}, 'limit': 100},
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_get_tracks_filter_track_id(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    track_id = '7948e3a9-623c-4524-a390-9e4264d27a11'
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'filters': {'track_id': track_id, 'buid': BUID}, 'limit': 100},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['tracks']) == 1
    assert resp['tracks'][0]['track_id'] == track_id
